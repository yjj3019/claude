#!/usr/bin/env python3
"""Validate core FEF structure and loading-map contracts."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from generate_agents import AGENTS, expected_agents
from sync_kernel import synchronized_text
from markdown_sections import parse_sections

ROOT = Path(__file__).resolve().parents[1]
LOADING_MAP = ROOT / "docs" / "loading-map.md"
CLAUDE = ROOT / "CLAUDE.md"
# Structural cold-start budget (align with measure_load.MAX_COLD_START_BYTES).
MAX_CLAUDE_ENTRY_BYTES = 7000
HEAVY_NON_DEFAULT_PATHS = (
    "PROGRESS.md",
    "SESSION_LOG.md",
    "CHANGELOG.md",
    "README.md",
    "docs/model-usage.md",
    "docs/adaptive-effort.md",
)
HEAVY_NAME_FRAGMENTS = ("optimization", "simulation-", "-report")

REQUIRED_KERNEL = [
    "kernel/CoreKernel.md",
    "kernel/MetaRules.md",
    "kernel/Checklist.md",
]
LIMITS = {"modules": 1, "domains": 2, "workflows": 1, "reviewers": 1, "policies": 3}
PATH_RE = re.compile(
    r"`((?:(?:kernel|policies|modules|domains|reviewers|workflows|docs|tests|examples)/[^`]+|"
    r"(?:CLAUDE|AGENTS|README|CHANGELOG|ROADMAP|CONTRIBUTING))\.md)`"
)
TEST_HEADER_RE = re.compile(r"^# Golden Test (\d{3}):", re.MULTILINE)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REQUIRED_PACKS = [
    "policies/FileHandling.md",
    "policies/ToolExecution.md",
    "policies/Freshness.md",
    "modules/Coding.md",
    "workflows/CodingWorkflow.md",
    "reviewers/CodeChangeReviewer.md",
    "reviewers/ProposalConsistencyReviewer.md",
]
REFERENCE_ROOT_FILES = ("CLAUDE.md", "AGENTS.md", "README.md", "CHANGELOG.md", "ROADMAP.md", "CONTRIBUTING.md")
REFERENCE_DIRS = ("kernel", "policies", "modules", "domains", "reviewers", "workflows", "docs", "tests", "examples")


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def validate_required_files(errors: list[str]) -> None:
    for rel in ["CLAUDE.md", "docs/loading-map.md", *REQUIRED_KERNEL, *REQUIRED_PACKS]:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}", errors)


def validate_inlined_kernel(errors: list[str]) -> None:
    if not CLAUDE.is_file():
        return
    text = CLAUDE.read_text(encoding="utf-8-sig")
    try:
        expected = synchronized_text(text)
    except ValueError as error:
        fail(str(error), errors)
        return
    if text != expected:
        fail("CLAUDE.md inlined Kernel is out of sync; run python scripts/sync_kernel.py", errors)


def validate_generated_agents(errors: list[str]) -> None:
    try:
        expected = expected_agents()
    except ValueError as error:
        fail(str(error), errors)
        return
    actual = {path.name: path.read_text(encoding="utf-8-sig") for path in AGENTS.glob("*.md")} if AGENTS.is_dir() else {}
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    stale = sorted(name for name in expected.keys() & actual.keys() if expected[name] != actual[name])
    if missing or extra or stale:
        details = "; ".join(filter(None, [
            f"missing: {', '.join(missing)}" if missing else "",
            f"extra: {', '.join(extra)}" if extra else "",
            f"stale: {', '.join(stale)}" if stale else "",
        ]))
        fail(f"generated reviewer agents are out of sync ({details}); run python scripts/generate_agents.py", errors)


def validate_references(errors: list[str]) -> None:
    # docs/releases/ holds frozen point-in-time release notes; a later file
    # deletion (e.g. a closed workstream's docs) shouldn't retroactively fail
    # a historical snapshot's own references. Live docs elsewhere still get
    # the same treatment.
    sources = [ROOT / name for name in REFERENCE_ROOT_FILES if (ROOT / name).is_file()]
    sources += [
        source for directory in REFERENCE_DIRS for source in (ROOT / directory).rglob("*.md")
        if "releases" not in source.relative_to(ROOT).parts
    ]
    for source in sources:
        text = source.read_text(encoding="utf-8-sig")
        for line_number, line in enumerate(text.splitlines(), 1):
            for rel in PATH_RE.findall(line):
                if not (ROOT / rel).is_file():
                    fail(f"{source.relative_to(ROOT)}:{line_number} references missing file: {rel}", errors)
            for target in MARKDOWN_LINK_RE.findall(line):
                target = target.split("#", 1)[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                resolved = (source.parent / target).resolve()
                if not resolved.exists():
                    fail(f"{source.relative_to(ROOT)}:{line_number} has broken Markdown link: {target}", errors)


def validate_loading_map(errors: list[str]) -> None:
    if not LOADING_MAP.is_file():
        return
    text = LOADING_MAP.read_text(encoding="utf-8")
    sections = parse_sections(text)
    if "Task Map" not in sections:
        fail("docs/loading-map.md: missing Task Map section", errors)
        return
    task_map = sections["Task Map"]
    lines = task_map.splitlines()
    rows = [line for line in lines if line.startswith("|") and "---" not in line]
    for row in rows[2:]:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) != 6:
            fail(f"invalid task-map row with {len(cells)} columns: {row}", errors)
            continue
        task = cells[0]
        refs = PATH_RE.findall(row)
        counts = {key: 0 for key in LIMITS}
        for rel in refs:
            category = rel.split("/", 1)[0]
            if category in counts:
                counts[category] += 1
        for category, limit in LIMITS.items():
            if counts[category] > limit:
                fail(f"{task}: {category} count {counts[category]} exceeds limit {limit}", errors)
        if task == "Proposal consistency check" and refs.count("reviewers/ProposalConsistencyReviewer.md") != 1:
            fail("Proposal consistency check must use only reviewers/ProposalConsistencyReviewer.md", errors)
        if task == "Code modification":
            for rel in ["modules/Coding.md", "workflows/CodingWorkflow.md"]:
                if rel not in refs:
                    fail(f"Code modification route missing: {rel}", errors)


def validate_golden_tests(errors: list[str]) -> None:
    seen: dict[str, Path] = {}
    for path in sorted((ROOT / "tests").glob("GoldenTest-*.md")):
        match = TEST_HEADER_RE.search(path.read_text(encoding="utf-8-sig"))
        if not match:
            fail(f"missing Golden Test ID header: {path.relative_to(ROOT)}", errors)
            continue
        test_id = match.group(1)
        if path.stem != f"GoldenTest-{test_id}":
            fail(f"Golden Test filename/header mismatch: {path.relative_to(ROOT)}", errors)
        if test_id in seen:
            fail(f"duplicate Golden Test ID {test_id}: {seen[test_id].relative_to(ROOT)}, {path.relative_to(ROOT)}", errors)
        seen[test_id] = path


def validate_runtime_terms(errors: list[str]) -> None:
    sources = [CLAUDE, LOADING_MAP, *(ROOT / "kernel").glob("*.md"), *(ROOT / "policies").glob("*.md")]
    for source in sources:
        if not source.is_file():
            continue
        text = source.read_text(encoding="utf-8")
        for term in ["Fable5 Distilled Patterns", "Fable5 Enhanced"]:
            if term in text:
                fail(f"prohibited model-specific Runtime term in {source.relative_to(ROOT)}: {term}", errors)



def validate_context_and_model_floor(errors: list[str]) -> None:
    """Require entry pointers to Context Budget and Model-Invariant Floor."""
    model_usage = ROOT / "docs" / "model-usage.md"
    if model_usage.is_file():
        mu = model_usage.read_text(encoding="utf-8-sig")
        for phrase in (
            "## Model-Invariant Floor",
            "Opus",
            "Fable",
            "Sonnet",
            "Haiku",
            "escalate the model",
        ):
            if phrase not in mu:
                fail(f"docs/model-usage.md missing required floor/roster phrase: {phrase}", errors)
    else:
        fail("missing docs/model-usage.md", errors)

    for rel, phrases in (
        ("CLAUDE.md", ("## Context Budget", "Model-Invariant Floor", "loading-map")),
        ("AGENTS.md", ("Context Budget", "Model-Invariant Floor", "escalate")),
    ):
        target = ROOT / rel
        if not target.is_file():
            fail(f"missing {rel}", errors)
            continue
        body = target.read_text(encoding="utf-8-sig")
        for phrase in phrases:
            if phrase not in body:
                fail(f"{rel} missing required phrase: {phrase}", errors)

    if not (ROOT / "scripts" / "install_pack.py").is_file():
        fail("missing scripts/install_pack.py (URL-only install entry)", errors)



def validate_claude_entry_budget(errors: list[str]) -> None:
    """Keep CLAUDE.md under the structural cold-start byte budget."""
    if not CLAUDE.is_file():
        return
    size = len(CLAUDE.read_text(encoding="utf-8-sig").encode("utf-8"))
    if size > MAX_CLAUDE_ENTRY_BYTES:
        fail(
            f"CLAUDE.md cold-start size {size} exceeds budget {MAX_CLAUDE_ENTRY_BYTES} bytes",
            errors,
        )


def validate_heavy_paths_not_default(errors: list[str]) -> None:
    """Heavy repo docs must not appear in loading-map Task Map / routes required sets."""
    import json
    referenced: set[str] = set()
    if LOADING_MAP.is_file():
        sections = parse_sections(LOADING_MAP.read_text(encoding="utf-8-sig"))
        task_map = sections.get("Task Map", "")
        for rel in PATH_RE.findall(task_map):
            referenced.add(rel)
    routes = ROOT / "config" / "routes.json"
    if routes.is_file():
        data = json.loads(routes.read_text(encoding="utf-8"))
        for route in data.get("routes") or []:
            for key in ("module", "workflow", "reviewer"):
                value = route.get(key)
                if value:
                    referenced.add(value)
            for domain in route.get("domains") or []:
                referenced.add(domain)
            for policy in route.get("policies") or []:
                referenced.add(policy)
    for rel in HEAVY_NON_DEFAULT_PATHS:
        if rel in referenced:
            fail(f"heavy path must not be in default loading-map/routes set: {rel}", errors)
        if rel in REQUIRED_PACKS:
            fail(f"heavy path must not be in REQUIRED_PACKS: {rel}", errors)
    for rel in sorted(referenced):
        name = rel.lower()
        if any(fragment in name for fragment in HEAVY_NAME_FRAGMENTS):
            fail(f"optimization/report path must not be in default load set: {rel}", errors)


def validate_latency_contract_phrases(errors: list[str]) -> None:
    """Require explicit latency-over-load policy in entry files."""
    for rel, phrases in (
        ("CLAUDE.md", ("Latency > completeness", "cold-start", "model-usage.md")),
        ("AGENTS.md", ("Latency > completeness",)),
    ):
        target = ROOT / rel
        if not target.is_file():
            fail(f"missing {rel}", errors)
            continue
        body = target.read_text(encoding="utf-8-sig")
        for phrase in phrases:
            if phrase not in body:
                fail(f"{rel} missing latency phrase: {phrase}", errors)
    model_usage = ROOT / "docs" / "model-usage.md"
    if model_usage.is_file():
        mu = model_usage.read_text(encoding="utf-8-sig")
        if "## When to Load This Doc" not in mu:
            fail("docs/model-usage.md missing ## When to Load This Doc", errors)
        if "only when choosing or switching" not in mu and "only** when choosing or switching" not in mu:
            # accept either markdown bold form
            if "when choosing or switching" not in mu:
                fail("docs/model-usage.md missing choose/switch load gate wording", errors)
    else:
        fail("missing docs/model-usage.md", errors)


def validate_adaptive_effort(errors: list[str]) -> None:
    """Require Adaptive Effort router doc + entry pointers without bloating cold-start."""
    adaptive = ROOT / "docs" / "adaptive-effort.md"
    if not adaptive.is_file():
        fail("missing docs/adaptive-effort.md", errors)
    else:
        body = adaptive.read_text(encoding="utf-8-sig")
        for phrase in (
            "## Tier Table",
            "L0 Light docs",
            "L1 Default",
            "L2 Complex everyday",
            "L3 Hardest",
            "Escalate model before expanding packs",
            "When unsure → Sonnet (L1)",
            "Haiku only",
            "Never preload",
            "Load Limits",
            "primarily select",
            "Integrity",
            "Model-Invariant Floor",
            "Risk ↔ Effort Coupling",
            "ban L0",
        ):
            if phrase not in body:
                fail(f"docs/adaptive-effort.md missing required phrase: {phrase}", errors)
    for rel, phrases in (
        ("CLAUDE.md", ("## Adaptive Effort", "docs/adaptive-effort.md", "model before packs")),
        ("AGENTS.md", ("Adaptive Effort", "docs/adaptive-effort.md")),
        ("docs/model-usage.md", ("## Adaptive Effort", "docs/adaptive-effort.md", "narrow gate")),
    ):
        target = ROOT / rel
        if not target.is_file():
            fail(f"missing {rel}", errors)
            continue
        body = target.read_text(encoding="utf-8-sig")
        for phrase in phrases:
            if phrase not in body:
                fail(f"{rel} missing adaptive-effort phrase: {phrase}", errors)


def validate_adaptive_route_alignment(errors: list[str]) -> None:
    """F-03: wire classify_tier / validate_pack_load against mapped route samples.

    Stops false-green when L1 model tier disagrees with loading-map pack counts.
    """
    try:
        from lib.adaptive_effort import (
            classify_tier,
            counts_from_selection,
            missing_integrity_policies,
            validate_pack_load,
        )
        from lib.routing import detect, load_config
    except ImportError as exc:
        fail(f"adaptive route alignment import failed: {exc}", errors)
        return

    config = load_config()
    samples = (
        ("fix a bug in the payment module", "coding", "L1"),
        ("research current version of OpenShift networking", "research", None),
        ("write an operations manual for RHEL patching", "manual", None),
        ("write a technical blog post about SELinux", "technical_blog", None),
        ("What is Kubernetes?", None, "L1"),  # kernel-only
        # R2-P1-CI-EN-ONLY-SAMPLES: Korean + high-risk unmapped + fallback negatives
        ("프로덕션 장애 근본 원인 분석", "rca", "L3"),
        ("코드수정 최소 변경", "coding", "L1"),
    )
    for ask, expected_route, expected_tier in samples:
        selection = detect(ask, config)
        tier = classify_tier(ask)
        if expected_tier and tier != expected_tier:
            fail(
                f"adaptive classify_tier({ask!r}) expected {expected_tier}, got {tier}",
                errors,
            )
        if expected_route is None:
            if not selection.get("kernel_only_safe"):
                fail(f"expected kernel_only_safe for ask {ask!r}", errors)
            continue
        if selection.get("task_type") != expected_route:
            fail(
                f"route sample {ask!r}: expected {expected_route}, "
                f"got {selection.get('task_type')}",
                errors,
            )
        if selection.get("kernel_only_safe"):
            fail(f"mapped route sample unexpectedly kernel_only_safe: {ask!r}", errors)
            continue
        counts = counts_from_selection(selection)
        pack_errors = validate_pack_load(
            tier,
            kernel_only_safe=False,
            module_paths=[selection["module"]] if selection.get("module") else [],
            policy_paths=selection.get("policies") or [],
            **counts,
        )
        for item in pack_errors:
            fail(f"adaptive×route {expected_route}: {item}", errors)
        if expected_route == "coding":
            for item in missing_integrity_policies(
                selection.get("policies") or [],
                ("policies/FileHandling.md", "policies/ToolExecution.md"),
            ):
                fail(f"adaptive×route coding integrity: {item}", errors)

    # High-risk unmapped + coding-fallback negatives (R2-P0 / R2-P1)
    hi = detect("운영 환경에서 고객 데이터 마이그레이션 계획 검토", config)
    if hi.get("risk_level") != "high" or hi.get("kernel_only_safe") is not False:
        fail("high-risk unmapped sample missing safety floor", errors)
    if "policies/Evidence.md" not in (hi.get("policies") or []):
        fail("high-risk unmapped sample missing Evidence.md", errors)
    for neg in (
        "what is the error budget concept?",
        "이 문서의 오탈자 수정해",
    ):
        sel = detect(neg, config)
        if sel.get("task_type") == "coding":
            fail(f"coding fallback overfire on {neg!r}", errors)

def validate_no_wrapper_policy(errors: list[str]) -> None:
    prohibited = {"operationalintegrity", "discipline", "corepolicyset"}
    for path in (ROOT / "policies").glob("*.md"):
        if re.sub(r"[^a-z]", "", path.stem.lower()) in prohibited:
            fail(f"wrapper policy bypass is prohibited: {path.relative_to(ROOT)}", errors)


def main() -> int:
    errors: list[str] = []
    validate_required_files(errors)
    validate_inlined_kernel(errors)
    validate_generated_agents(errors)
    validate_references(errors)
    validate_loading_map(errors)
    validate_golden_tests(errors)
    validate_runtime_terms(errors)
    validate_no_wrapper_policy(errors)
    validate_context_and_model_floor(errors)
    validate_claude_entry_budget(errors)
    validate_heavy_paths_not_default(errors)
    validate_latency_contract_phrases(errors)
    validate_adaptive_effort(errors)
    validate_adaptive_route_alignment(errors)
    if errors:
        print("FEF validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1
    print("FEF validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
