#!/usr/bin/env python3
"""Minimal automated runner for the fixture-mode coding Golden Tests (012-014).

Scope: only the three "fixture" mode tests are covered. The other 22 Golden
Tests are "manual" or "static" comparative-quality checks and are not
mechanically scorable — this script does not attempt to automate them.

What this script checks automatically (mechanical, deterministic):
- whether the project's own unit tests pass after the model's patch
- whether the shared root-cause file was actually touched (vs a caller-only fix)
- whether the test file itself was modified (a red flag: hiding the bug)
- whether a new third-party dependency was introduced

What this script does NOT score (still requires a human or LLM reviewer):
- diff minimalism/elegance, existing-pattern reuse quality, and the full
  100-point rubric in each GoldenTest-0NN.md. Those need judgment, not a
  regex/exit-code check.

Usage:
    # Dry run against the known answer-key patch (no API calls, no cost):
    python scripts/run_golden_test_coding.py --test 012 --patch-from tests/fixtures/GT012-code/money.py

    # Live run: caller supplies the model's already-edited fixture directory
    # (e.g. produced by `claude -p "$(cat tests/prompts/GT012-fef.md)"` run
    # with cwd set to a fresh copy of tests/fixtures/GT012-code/):
    python scripts/run_golden_test_coding.py --test 012 --edited-dir /path/to/model/output

This script never invokes the `claude` CLI itself and never spends API
budget — wiring a live model call into CI is a cost/secrets decision left
to the repository owner.
"""
from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEST_CONFIG = {
    "012": {"fixture": "GT012-code", "root_cause_file": "money.py", "callers": ["orders.py", "refunds.py"]},
    "013": {"fixture": "GT013-code", "root_cause_file": "amounts.py", "callers": ["refunds.py", "revenue.py"]},
    "014": {"fixture": "GT014-code", "root_cause_file": "billing.py", "callers": ["periods.py", "support.py"]},
}

STDLIB_ONLY_HINT = ("import ", "from ")


def copy_fixture(test_id: str) -> Path:
    cfg = TEST_CONFIG[test_id]
    src = ROOT / "tests" / "fixtures" / cfg["fixture"]
    if not src.is_dir():
        raise SystemExit(f"fixture not found: {src}")
    dst = Path(tempfile.mkdtemp(prefix=f"gt{test_id}-pristine-"))
    shutil.copytree(src, dst, dirs_exist_ok=True)
    return dst


def run_unittest(work_dir: Path) -> dict:
    work_dir = work_dir.resolve()
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py", "-v"],
        capture_output=True, text=True, cwd=work_dir,
    )
    stderr = proc.stderr
    passed = proc.returncode == 0
    return {"passed": passed, "returncode": proc.returncode, "output": stderr[-4000:]}


def new_imports(pristine_file: Path, edited_file: Path) -> list[str]:
    if not edited_file.exists():
        return []
    pristine_lines = {l.strip() for l in pristine_file.read_text(encoding="utf-8-sig").splitlines() if l.strip().startswith(STDLIB_ONLY_HINT)} if pristine_file.exists() else set()
    edited_lines = {l.strip() for l in edited_file.read_text(encoding="utf-8-sig").splitlines() if l.strip().startswith(STDLIB_ONLY_HINT)}
    return sorted(edited_lines - pristine_lines)


def score(test_id: str, pristine_dir: Path, edited_dir: Path) -> dict:
    cfg = TEST_CONFIG[test_id]
    unittest_result = run_unittest(edited_dir)

    root_cause_path = cfg["root_cause_file"]
    root_cause_touched = not filecmp.cmp(pristine_dir / root_cause_path, edited_dir / root_cause_path, shallow=False)

    caller_only_fix = (not root_cause_touched) and any(
        not filecmp.cmp(pristine_dir / c, edited_dir / c, shallow=False) for c in cfg["callers"]
    )

    test_files_pristine = sorted(p.name for p in pristine_dir.glob("test_*.py"))
    test_file_modified = any(
        not filecmp.cmp(pristine_dir / name, edited_dir / name, shallow=False) for name in test_files_pristine
    )

    new_deps = []
    for py_file in edited_dir.glob("*.py"):
        if py_file.name.startswith("test_"):
            continue
        new_deps.extend(new_imports(pristine_dir / py_file.name, py_file))
    # crude stdlib/project-local filter: flag only imports that are neither
    # stdlib-looking (no dots-as-package-path heuristics attempted) nor one
    # of the fixture's own local modules.
    local_modules = {p.stem for p in pristine_dir.glob("*.py")}
    flagged_deps = [
        line for line in new_deps
        if not any(f" {m}" in line or line.endswith(m) or f".{m}" in line for m in local_modules)
    ]

    hard_cap = 100
    reasons = []
    if not unittest_result["passed"]:
        hard_cap = min(hard_cap, 60)
        reasons.append("tests still fail after patch")
    if caller_only_fix:
        hard_cap = min(hard_cap, 55)
        reasons.append("caller-only fix: root-cause file untouched, only a caller changed")
    if test_file_modified:
        hard_cap = min(hard_cap, 50)
        reasons.append("test file was modified — possible bug-hiding change, needs manual review")
    if not root_cause_touched and not caller_only_fix:
        reasons.append("no code change detected in fixture directory")
        hard_cap = min(hard_cap, 40)

    return {
        "test_id": test_id,
        "mechanical_checks": {
            "unit_tests_pass": unittest_result["passed"],
            "root_cause_file_touched": root_cause_touched,
            "caller_only_fix": caller_only_fix,
            "test_file_modified": test_file_modified,
            "new_dependency_candidates": flagged_deps,
        },
        "mechanical_score_cap": hard_cap,
        "cap_reasons": reasons,
        "manual_review_required_for": [
            "root_cause_location_quality (20 pts)",
            "sibling_caller_coverage_reasoning (15 pts)",
            "minimal_diff_quality (10 pts)",
            "existing_pattern_reuse (5 pts)",
            "error_handling_quality (10 pts)",
        ],
        "unittest_output_tail": unittest_result["output"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--test", required=True, choices=sorted(TEST_CONFIG))
    parser.add_argument("--edited-dir", type=Path, help="Directory containing the model's already-edited fixture copy")
    parser.add_argument("--patch-from", type=Path, help="Apply this single file as the root-cause file content for a dry run (no live model call)")
    parser.add_argument("--output", type=Path, help="Optional JSON result path")
    args = parser.parse_args()

    pristine_dir = copy_fixture(args.test)
    try:
        if args.edited_dir:
            edited_dir = args.edited_dir.resolve()
        elif args.patch_from:
            edited_dir = Path(tempfile.mkdtemp(prefix=f"gt{args.test}-edited-"))
            shutil.copytree(pristine_dir, edited_dir, dirs_exist_ok=True)
            root_cause_file = TEST_CONFIG[args.test]["root_cause_file"]
            shutil.copy(args.patch_from, edited_dir / root_cause_file)
        else:
            parser.error("supply --edited-dir (live model output) or --patch-from (dry run)")

        result = score(args.test, pristine_dir, edited_dir)
    finally:
        shutil.rmtree(pristine_dir, ignore_errors=True)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    return 0 if result["mechanical_score_cap"] >= 85 else 1


if __name__ == "__main__":
    raise SystemExit(main())
