"""Unit tests for Adaptive Effort / Complexity Router."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.adaptive_effort import (  # noqa: E402
    FORBIDDEN_PRELOAD_L0_L1,
    LOAD_LIMITS,
    TIERS,
    classify_tier,
    validate_pack_load,
)
import validate_framework as validator  # noqa: E402


class AdaptiveEffortTests(unittest.TestCase):
    def test_doc_and_entry_pointers(self):
        adaptive = (ROOT / "docs" / "adaptive-effort.md").read_text(encoding="utf-8-sig")
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8-sig")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8-sig")
        model_usage = (ROOT / "docs" / "model-usage.md").read_text(encoding="utf-8-sig")
        self.assertIn("## Tier Table", adaptive)
        self.assertIn("L0 Quick", adaptive)
        self.assertIn("L3 Hardest", adaptive)
        self.assertIn("Escalate model before expanding packs", adaptive)
        self.assertIn("## Adaptive Effort", claude)
        self.assertIn("docs/adaptive-effort.md", claude)
        self.assertIn("Adaptive Effort", agents)
        self.assertIn("## Adaptive Effort", model_usage)
        self.assertLessEqual(
            len(claude.encode("utf-8")),
            validator.MAX_CLAUDE_ENTRY_BYTES,
        )

    def test_l0_forbids_multi_pack_load(self):
        self.assertEqual(classify_tier("What is SELinux?"), "L0")
        self.assertEqual(classify_tier("Define cold-start latency"), "L0")
        tier = TIERS["L0"]
        self.assertTrue(tier.kernel_only)
        self.assertEqual(tier.max_modules, 0)
        errors = validate_pack_load(
            "L0",
            modules=1,
            workflows=1,
            preloaded=["docs/model-usage.md", "PROGRESS.md"],
        )
        self.assertTrue(any("forbids multi-pack" in e for e in errors))
        self.assertTrue(any("must not preload docs/model-usage.md" in e for e in errors))
        self.assertTrue(any("must not preload PROGRESS.md" in e for e in errors))
        self.assertEqual(validate_pack_load("L0"), [])

    def test_l1_blocks_heavy_preload(self):
        self.assertEqual(classify_tier("Small one-file edit to fix a typo"), "L1")
        errors = validate_pack_load("L1", modules=1, preloaded=FORBIDDEN_PRELOAD_L0_L1)
        self.assertTrue(any("must not preload" in e for e in errors))
        self.assertEqual(validate_pack_load("L1", modules=1), [])
        self.assertTrue(validate_pack_load("L1", modules=2))  # exceeds L1 cap

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

    def test_doc_states_l0_and_l3_constraints(self):
        adaptive = (ROOT / "docs" / "adaptive-effort.md").read_text(encoding="utf-8-sig")
        self.assertIn("Kernel only", adaptive)
        self.assertIn("L0 forbids multi-pack load", adaptive)
        self.assertIn("Load Limits", adaptive)
        self.assertIn("Never preload", adaptive)


if __name__ == "__main__":
    unittest.main()
