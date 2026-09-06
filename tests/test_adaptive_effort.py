"""Unit tests for Adaptive Effort / Complexity Router."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.adaptive_effort import (  # noqa: E402
    FORBIDDEN_PRELOAD_L0_L1,
    L0_MODULE_ALLOWLIST,
    LOAD_LIMITS,
    TIERS,
    classify_tier,
    counts_from_selection,
    effective_tier,
    missing_integrity_policies,
    validate_pack_load,
)
from lib.routing import detect, load_config  # noqa: E402
import validate_framework as validator  # noqa: E402


class AdaptiveEffortTests(unittest.TestCase):
    def test_doc_and_entry_pointers(self):
        adaptive = (ROOT / "docs" / "adaptive-effort.md").read_text(encoding="utf-8-sig")
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8-sig")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8-sig")
        model_usage = (ROOT / "docs" / "model-usage.md").read_text(encoding="utf-8-sig")
        self.assertIn("## Tier Table", adaptive)
        self.assertIn("L0 Light docs", adaptive)
        self.assertIn("L1 Default", adaptive)
        self.assertIn("L3 Hardest", adaptive)
        self.assertIn("When unsure", adaptive)
        self.assertIn("Escalate model before expanding packs", adaptive)
        self.assertIn("primarily select", adaptive)
        self.assertIn("## Adaptive Effort", claude)
        self.assertIn("docs/adaptive-effort.md", claude)
        self.assertIn("Adaptive Effort", agents)
        self.assertIn("CLAUDE.md", agents)
        self.assertIn("docs/adaptive-effort.md", agents)
        self.assertIn("## Adaptive Effort", model_usage)
        self.assertLessEqual(
            len(claude.encode("utf-8")),
            validator.MAX_CLAUDE_ENTRY_BYTES,
        )

    def test_default_unsure_is_sonnet_l1(self):
        self.assertEqual(classify_tier("Help me with this"), "L1")
        self.assertEqual(classify_tier("Please look into it"), "L1")
        self.assertEqual(TIERS[classify_tier("unclear ask")].model, "Sonnet 5")

    def test_quick_fact_does_not_force_haiku(self):
        # General quick facts / Q&A are Sonnet (L1), not Haiku.
        self.assertEqual(classify_tier("What is SELinux?"), "L1")
        self.assertEqual(classify_tier("Define cold-start latency"), "L1")
        self.assertEqual(classify_tier("quick fact about DNS"), "L1")
        self.assertEqual(classify_tier("yes or no: is TCP reliable?"), "L1")

    def test_notion_doc_signals_route_to_haiku_l0(self):
        self.assertEqual(classify_tier("Add a Notion note about the meeting"), "L0")
        self.assertEqual(classify_tier("Append a row to the Notion tracker"), "L0")
        self.assertEqual(classify_tier("Short doc capture of today's standup"), "L0")
        self.assertEqual(classify_tier("Trivial filing into the archive folder"), "L0")
        self.assertEqual(classify_tier("Simple checklist ticks for onboarding"), "L0")
        self.assertEqual(classify_tier("meeting notes from standup"), "L0")
        self.assertEqual(classify_tier("checklist for onboarding"), "L0")
        self.assertEqual(TIERS["L0"].model, "Haiku 4.5")

    def test_korean_notion_synonyms_route_l0(self):
        self.assertEqual(classify_tier("노션에 메모 추가해줘"), "L0")
        self.assertEqual(classify_tier("체크리스트 업데이트해줘"), "L0")
        self.assertEqual(classify_tier("회의 메모해 줘"), "L0")

    def test_mild_refactor_stays_l1_not_l2(self):
        self.assertEqual(classify_tier("refactor one function"), "L1")
        self.assertEqual(classify_tier("small refactor of a helper"), "L1")
        self.assertEqual(classify_tier("multi-file refactor across services"), "L2")
        self.assertEqual(classify_tier("large refactor of the auth stack"), "L3")

    def test_l0_allows_kernel_or_one_notion_section(self):
        self.assertEqual(validate_pack_load("L0"), [])
        self.assertEqual(
            validate_pack_load("L0", modules=1, module_paths=["modules/Meeting.md"]),
            [],
        )
        errors = validate_pack_load(
            "L0",
            modules=1,
            workflows=1,
            preloaded=["docs/model-usage.md", "PROGRESS.md"],
        )
        self.assertTrue(any("Notion/doc" in e or "no domains" in e for e in errors))
        self.assertTrue(any("must not preload docs/model-usage.md" in e for e in errors))
        self.assertTrue(any("must not preload PROGRESS.md" in e for e in errors))
        self.assertTrue(validate_pack_load("L0", modules=2))
        # F-11: Coding.md must not count as L0 Notion/doc section
        blocked = validate_pack_load(
            "L0", modules=1, module_paths=["modules/Coding.md"]
        )
        self.assertTrue(any("not allowlisted" in e for e in blocked))
        self.assertIn("modules/Meeting.md", L0_MODULE_ALLOWLIST)

    def test_l1_blocks_heavy_preload(self):
        self.assertEqual(classify_tier("Small one-file edit to fix a typo"), "L1")
        errors = validate_pack_load("L1", modules=1, preloaded=FORBIDDEN_PRELOAD_L0_L1)
        self.assertTrue(any("must not preload" in e for e in errors))
        self.assertEqual(validate_pack_load("L1", modules=1), [])
        self.assertTrue(validate_pack_load("L1", modules=2))  # exceeds map cap

    def test_f01_l1_mapped_coding_allows_loading_map_packs(self):
        """F-01 contract: L1 = Sonnet model tier; packs follow loading-map when mapped.

        Routine coding stays Sonnet (not Opus) and MUST keep Integrity policies
        (FileHandling/ToolExecution) — Adaptive must not force wf/rev/pol=0.
        """
        ask = "fix a bug in auth.py"
        self.assertEqual(classify_tier(ask), "L1")
        self.assertEqual(TIERS["L1"].model, "Sonnet 5")
        # Caps equal loading-map Load Limits (not the old wf/rev/pol=0 strip).
        for key in LOAD_LIMITS:
            self.assertEqual(
                getattr(TIERS["L1"], f"max_{key}"),
                LOAD_LIMITS[key],
                msg=f"L1 max_{key} must follow loading-map",
            )
        errors = validate_pack_load(
            "L1",
            modules=1,
            domains=0,
            workflows=1,
            reviewers=1,
            policies=2,
            kernel_only_safe=False,
            module_paths=["modules/Coding.md"],
            policy_paths=[
                "policies/FileHandling.md",
                "policies/ToolExecution.md",
            ],
        )
        self.assertEqual(errors, [])
        # Against real detect() coding selection
        selection = detect(ask, load_config())
        self.assertFalse(selection["kernel_only_safe"])
        self.assertEqual(selection["task_type"], "coding")
        counts = counts_from_selection(selection)
        route_errors = validate_pack_load(
            "L1",
            kernel_only_safe=False,
            module_paths=[selection["module"]] if selection.get("module") else [],
            policy_paths=selection.get("policies") or [],
            **counts,
        )
        self.assertEqual(route_errors, [])
        intact = missing_integrity_policies(
            selection.get("policies") or [],
            ("policies/FileHandling.md", "policies/ToolExecution.md"),
        )
        self.assertEqual(intact, [])

    def test_l1_kernel_only_forbids_packs(self):
        errors = validate_pack_load(
            "L1", modules=1, workflows=1, kernel_only_safe=True
        )
        self.assertTrue(any("kernel_only_safe" in e for e in errors))

    def test_l3_respects_load_limits(self):
        self.assertEqual(classify_tier("Deep RCA of a multi-hour production outage"), "L3")
        tier = TIERS["L3"]
        self.assertEqual(tier.max_modules, LOAD_LIMITS["modules"])
        self.assertEqual(tier.max_domains, LOAD_LIMITS["domains"])
        self.assertEqual(tier.max_workflows, LOAD_LIMITS["workflows"])
        self.assertEqual(tier.max_reviewers, LOAD_LIMITS["reviewers"])
        self.assertEqual(tier.max_policies, LOAD_LIMITS["policies"])
        ok = validate_pack_load(
            "L3",
            modules=1,
            domains=2,
            workflows=1,
            reviewers=1,
            policies=3,
        )
        self.assertEqual(ok, [])
        over = validate_pack_load(
            "L3",
            modules=2,
            domains=3,
            workflows=2,
            reviewers=2,
            policies=4,
        )
        self.assertTrue(any("Load Limits" in e or "exceeds modules" in e for e in over))
        self.assertGreaterEqual(len(over), 4)

    def test_doc_states_sonnet_default_and_l3_constraints(self):
        adaptive = (ROOT / "docs" / "adaptive-effort.md").read_text(encoding="utf-8-sig")
        self.assertIn("When unsure → Sonnet (L1)", adaptive)
        self.assertIn("Haiku only", adaptive)
        self.assertIn("Kernel only", adaptive)
        self.assertIn("Load Limits", adaptive)
        self.assertIn("Never preload", adaptive)
        self.assertIn("Model-Invariant Floor", adaptive)
        self.assertIn("Integrity", adaptive)

    def test_mapped_route_samples_align_with_adaptive(self):
        """F-03: route samples must not false-green against Adaptive pack contract."""
        config = load_config()
        samples = [
            ("fix a bug in the payment module", "coding"),
            ("research current version of OpenShift networking", "research"),
            ("write an operations manual for RHEL patching", "manual"),
            ("write a technical blog post about SELinux", "technical_blog"),
        ]
        for ask, expected_route in samples:
            with self.subTest(ask=ask):
                selection = detect(ask, config)
                self.assertEqual(selection["task_type"], expected_route)
                self.assertFalse(selection["kernel_only_safe"])
                tier = classify_tier(ask)
                # Routine mapped asks stay L1 (Sonnet); do not bump to L2 just for packs.
                if expected_route == "coding":
                    self.assertEqual(tier, "L1")
                counts = counts_from_selection(selection)
                errors = validate_pack_load(
                    tier,
                    kernel_only_safe=False,
                    module_paths=[selection["module"]] if selection.get("module") else [],
                    policy_paths=selection.get("policies") or [],
                    **counts,
                )
                self.assertEqual(errors, [])

    def test_korean_l3_signals_match_english_root_cause(self):
        """R2-P0-KO-TIER-BLIND + R2-P2-KO-SPACING"""
        self.assertEqual(classify_tier("프로덕션 장애 근본 원인 분석"), "L3")
        self.assertEqual(classify_tier("production outage root cause analysis"), "L3")
        self.assertEqual(classify_tier("근본원인분석"), "L3")
        self.assertEqual(classify_tier("대규모 리팩터"), "L3")
        self.assertEqual(classify_tier("보안 감사 수행"), "L3")
        self.assertEqual(classify_tier("장기 작업 에이전트"), "L3")

    def test_high_risk_bans_l0_not_blanket_l2(self):
        """R2-P1-RISK-TIER-DECOUPLED: floor L1 only; no blanket Opus."""
        tier, reason = effective_tier(
            "Add a Notion note about the meeting",
            risk_level="high",
        )
        self.assertEqual(tier, "L1")
        self.assertIsNotNone(reason)
        self.assertEqual(TIERS[tier].model, "Sonnet 5")
        # High-risk alone without L2/L3 signals stays L1 (not L2)
        tier2, _ = effective_tier(
            "customer production checklist update please",
            risk_level="high",
        )
        self.assertEqual(tier2, "L1")
        # High-risk + L3 signals stays/raises to L3 via text signals
        tier3, _ = effective_tier(
            "프로덕션 장애 근본 원인 분석",
            risk_level="high",
        )
        self.assertEqual(tier3, "L3")

    def test_l0_leak_raises_when_substantial_packs(self):
        """R2-P2-L0-LEAK"""
        selection = {
            "module": "modules/Coding.md",
            "workflow": "workflows/CodingWorkflow.md",
            "reviewer": "reviewers/CodeChangeReviewer.md",
            "policies": ["policies/FileHandling.md"],
            "domains": [],
            "kernel_only_safe": False,
        }
        # Ask text looks like Notion, but packs are substantial → ≥L1
        tier, reason = effective_tier(
            "Add a Notion note about the meeting",
            risk_level="low",
            selection=selection,
        )
        self.assertEqual(tier, "L1")
        self.assertIsNotNone(reason)

    def test_risk_floor_documented(self):
        adaptive = (ROOT / "docs" / "adaptive-effort.md").read_text(encoding="utf-8-sig")
        self.assertIn("Risk ↔ Effort Coupling", adaptive)
        self.assertIn("ban L0", adaptive)
        self.assertIn("Do not", adaptive)
        loading = (ROOT / "docs" / "loading-map.md").read_text(encoding="utf-8-sig")
        self.assertIn("Domain overflow", loading)
        self.assertIn("dropped", loading)
        self.assertTrue("fallback" in loading.lower() or "FALLBACK" in loading)


if __name__ == "__main__":
    unittest.main()
