#!/usr/bin/env python3
"""Validate core FEF structure and loading-map contracts."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOADING_MAP = ROOT / "docs" / "loading-map.md"
CLAUDE = ROOT / "CLAUDE.md"

REQUIRED_KERNEL = [
    "kernel/CoreKernel.md",
    "kernel/MetaRules.md",
    "kernel/Checklist.md",
]
LIMITS = {"modules": 1, "domains": 2, "workflows": 1, "reviewers": 1, "policies": 3}
PATH_RE = re.compile(r"`((?:kernel|policies|modules|domains|reviewers|workflows|docs)/[^`]+\.md)`")
TEST_HEADER_RE = re.compile(r"^# Golden Test (\d{3}):", re.MULTILINE)
REQUIRED_PACKS = [
    "policies/FileHandling.md",
    "policies/ToolExecution.md",
    "policies/Freshness.md",
    "modules/Coding.md",
    "workflows/CodingWorkflow.md",
    "reviewers/CodeChangeReviewer.md",
    "reviewers/ProposalConsistencyReviewer.md",
]


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def validate_required_files(errors: list[str]) -> None:
    for rel in ["CLAUDE.md", "docs/loading-map.md", *REQUIRED_KERNEL, *REQUIRED_PACKS]:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}", errors)


def validate_references(errors: list[str]) -> None:
    for source in [CLAUDE, LOADING_MAP]:
        if not source.is_file():
            continue
        text = source.read_text(encoding="utf-8")
        for rel in sorted(set(PATH_RE.findall(text))):
            if not (ROOT / rel).is_file():
                fail(f"{source.relative_to(ROOT)} references missing file: {rel}", errors)


def validate_loading_map(errors: list[str]) -> None:
    if not LOADING_MAP.is_file():
        return
    task_map = LOADING_MAP.read_text(encoding="utf-8").split("## Task Map", 1)[1].split("\n## ", 1)[0]
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
    sources = [CLAUDE, LOADING_MAP, *(ROOT / "kernel").glob("*.md")]
    for source in sources:
        if not source.is_file():
            continue
        text = source.read_text(encoding="utf-8")
        for term in ["Fable5 Distilled Patterns", "Fable5 Enhanced"]:
            if term in text:
                fail(f"prohibited model-specific Runtime term in {source.relative_to(ROOT)}: {term}", errors)


def main() -> int:
    errors: list[str] = []
    validate_required_files(errors)
    validate_references(errors)
    validate_loading_map(errors)
    validate_golden_tests(errors)
    validate_runtime_terms(errors)
    if errors:
        print("FEF validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1
    print("FEF validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
