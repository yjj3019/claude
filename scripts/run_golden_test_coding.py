#!/usr/bin/env python3
"""Minimal automated runner for the fixture-mode coding Golden Tests (012-014, 026-030).

Scope: only the "fixture" mode coding tests are covered. The other Golden
Tests are "manual" or "static" comparative-quality checks and are not
mechanically scorable - this script does not attempt to automate them.

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
    # Dry run against the executable answer files (no API calls, no cost;
    # must exit 0 - this is also a CI regression gate for the runner itself):
    python scripts/run_golden_test_coding.py --test 012 --patch-dir tests/fixtures/GT012-code/answers

    # Negative control: patching with the buggy pristine file must exit 1:
    python scripts/run_golden_test_coding.py --test 012 --patch-from tests/fixtures/GT012-code/money.py

    # Live run: caller supplies the model's already-edited fixture directory
    # (e.g. produced by `claude -p "$(cat tests/prompts/GT012-fef.md)"` run
    # with cwd set to a fresh copy of tests/fixtures/GT012-code/):
    python scripts/run_golden_test_coding.py --test 012 --edited-dir /path/to/model/output

This script never invokes the `claude` CLI itself and never spends API
budget - wiring a live model call into CI is a cost/secrets decision left
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

# fix_files: files a correct patch is expected to change (the defect site).
# sibling_files: files a correct patch should leave alone; changing only these
# without touching any fix_file indicates a workaround, not a root-cause fix.
# Note GT013: the seeded defect is duplicated parsing in the two callers, so
# the callers ARE the fix_files and the shared helper is the sibling. GT014's
# defect is the boundary in periods.py, not the callers in billing.py.
TEST_CONFIG = {
    "012": {"fixture": "GT012-code", "fix_files": ["money.py"], "sibling_files": ["orders.py", "refunds.py"]},
    "013": {"fixture": "GT013-code", "fix_files": ["refunds.py", "revenue.py"], "sibling_files": ["amounts.py"]},
    "014": {"fixture": "GT014-code", "fix_files": ["periods.py"], "sibling_files": ["billing.py", "support.py"]},
    "026": {"fixture": "GT026-code", "fix_files": ["tagging.py"], "sibling_files": ["reports.py"]},
    "027": {"fixture": "GT027-code", "fix_files": ["inventory.py"], "sibling_files": ["audit.py"]},
    "028": {"fixture": "GT028-code", "fix_files": ["loader.py"], "sibling_files": ["summary.py"]},
    "029": {"fixture": "GT029-code", "fix_files": ["ranking.py"], "sibling_files": ["leaderboard.py"]},
    "030": {"fixture": "GT030-code", "fix_files": ["wallet.py"], "sibling_files": ["statements.py"]},
}

IMPORT_HINT = ("import ", "from ")
# Python 3.10+; falls back to an empty set on older interpreters (treated as
# "cannot verify stdlib membership", never as "safe to flag").
STDLIB_NAMES = getattr(sys, "stdlib_module_names", frozenset())


def copy_fixture(test_id: str) -> Path:
    cfg = TEST_CONFIG[test_id]
    src = ROOT / "tests" / "fixtures" / cfg["fixture"]
    if not src.is_dir():
        raise SystemExit(f"fixture not found: {src}")
    dst = Path(tempfile.mkdtemp(prefix=f"gt{test_id}-pristine-"))
    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "answers"))
    return dst


def file_changed(pristine_dir: Path, edited_dir: Path, relpath: str) -> bool:
    """True if relpath differs or was deleted. Never raises on a missing file."""
    edited = edited_dir / relpath
    if not edited.exists():
        return True
    pristine = pristine_dir / relpath
    if not pristine.exists():
        return True
    return not filecmp.cmp(pristine, edited, shallow=False)


def run_unittest(work_dir: Path) -> dict:
    work_dir = work_dir.resolve()
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py", "-v"],
        capture_output=True, text=True, cwd=work_dir,
    )
    stderr = proc.stderr
    passed = proc.returncode == 0
    return {"passed": passed, "returncode": proc.returncode, "output": stderr[-4000:]}


def imported_module_names(py_file: Path) -> set[str]:
    """Top-level module names this file imports, e.g. {'re', 'decimal'}."""
    names = set()
    if not py_file.exists():
        return names
    for line in py_file.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if stripped.startswith("import "):
            for part in stripped[len("import "):].split(","):
                names.add(part.strip().split(" as ")[0].split(".")[0])
        elif stripped.startswith("from "):
            mod = stripped[len("from "):].split(" import ")[0].strip()
            names.add(mod.split(".")[0])
    return names


def new_non_stdlib_imports(pristine_file: Path, edited_file: Path, local_modules: set[str]) -> list[str]:
    """New import names in edited_file vs pristine_file, excluding stdlib and local fixture modules.

    If STDLIB_NAMES is unavailable (pre-3.10), nothing is flagged rather than
    risking false positives on ordinary stdlib imports.
    """
    if not STDLIB_NAMES:
        return []
    added = imported_module_names(edited_file) - imported_module_names(pristine_file)
    return sorted(added - STDLIB_NAMES - local_modules)


def score(test_id: str, pristine_dir: Path, edited_dir: Path) -> dict:
    cfg = TEST_CONFIG[test_id]
    unittest_result = run_unittest(edited_dir)

    fix_files_touched = any(file_changed(pristine_dir, edited_dir, f) for f in cfg["fix_files"])

    caller_only_fix = (not fix_files_touched) and any(
        file_changed(pristine_dir, edited_dir, c) for c in cfg["sibling_files"]
    )

    test_files_pristine = sorted(p.name for p in pristine_dir.glob("test_*.py"))
    test_file_modified = any(file_changed(pristine_dir, edited_dir, name) for name in test_files_pristine)

    local_modules = {p.stem for p in pristine_dir.glob("*.py")}
    flagged_deps = []
    for py_file in sorted(edited_dir.glob("*.py")):
        if py_file.name.startswith("test_"):
            continue
        flagged_deps.extend(new_non_stdlib_imports(pristine_dir / py_file.name, py_file, local_modules))
    flagged_deps = sorted(set(flagged_deps))

    any_change = fix_files_touched or caller_only_fix or test_file_modified

    hard_cap = 100
    reasons = []
    if not unittest_result["passed"]:
        hard_cap = min(hard_cap, 60)
        reasons.append("tests still fail after patch")
    if caller_only_fix:
        hard_cap = min(hard_cap, 55)
        reasons.append("caller-only fix: no expected fix file touched, only a sibling changed")
    if test_file_modified:
        hard_cap = min(hard_cap, 50)
        reasons.append("test file was modified - possible bug-hiding change, needs manual review")
    if not any_change:
        hard_cap = min(hard_cap, 40)
        reasons.append("no code change detected in fixture directory")
    if flagged_deps:
        hard_cap = min(hard_cap, 70)
        reasons.append(f"candidate new dependency not in stdlib or fixture: {', '.join(flagged_deps)}")

    return {
        "test_id": test_id,
        "mechanical_checks": {
            "unit_tests_pass": unittest_result["passed"],
            "fix_files_touched": fix_files_touched,
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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--test", required=True, choices=sorted(TEST_CONFIG))
    parser.add_argument("--edited-dir", type=Path, help="Directory containing the model's already-edited fixture copy")
    parser.add_argument("--patch-from", type=Path, help="Dry run: overlay this single file onto the fixture copy, matched by filename (no live model call)")
    parser.add_argument("--patch-dir", type=Path, help="Dry run: overlay every *.py in this directory onto the fixture copy, matched by filename")
    parser.add_argument("--output", type=Path, help="Optional JSON result path")
    args = parser.parse_args(argv)

    pristine_dir = copy_fixture(args.test)
    dry_run_dir = None
    try:
        if args.edited_dir:
            edited_dir = args.edited_dir.resolve()
        elif args.patch_from or args.patch_dir:
            dry_run_dir = Path(tempfile.mkdtemp(prefix=f"gt{args.test}-edited-"))
            shutil.copytree(pristine_dir, dry_run_dir, dirs_exist_ok=True)
            overlays = [args.patch_from] if args.patch_from else sorted(args.patch_dir.glob("*.py"))
            if not overlays:
                parser.error(f"--patch-dir contains no *.py files: {args.patch_dir}")
            for overlay in overlays:
                shutil.copy(overlay, dry_run_dir / overlay.name)
            edited_dir = dry_run_dir
        else:
            parser.error("supply --edited-dir (live model output), --patch-from, or --patch-dir (dry run)")

        result = score(args.test, pristine_dir, edited_dir)
    finally:
        shutil.rmtree(pristine_dir, ignore_errors=True)
        if dry_run_dir is not None:
            shutil.rmtree(dry_run_dir, ignore_errors=True)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    # NOTE: 85 is this script's own single-run mechanical threshold, not the
    # GoldenTest-0NN.md PASS rule (which requires an *average over >=5 runs*
    # plus non-mechanical dimensions this script does not score). Do not
    # treat a 0 exit here as "the model passed the Golden Test."
    return 0 if result["mechanical_score_cap"] >= 85 else 1


if __name__ == "__main__":
    raise SystemExit(main())
