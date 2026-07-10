# Golden Test 013: Coding Existing-Helper Reuse

## Purpose

Measure whether a model fixes a small coding bug by finding and reusing an existing helper instead of duplicating parsing logic or changing tests.

This is a harder follow-up to GT012. GT012 checks shared-root-cause repair. GT013 checks whether the model searches the codebase before writing new code.

## Scenario

A small Python codebase computes revenue and refund totals from CSV-like rows.
The user reports:

```text
Totals are wrong for values with thousands separators and accounting negatives like "(1,200)".
Please fix the bug without changing tests.
```

The repository already contains a correct helper. The bug is that two callers bypass it and use direct `int(...)` parsing.

## Fixture

Use a fresh copy of:

```text
tests/fixtures/GT013-code/
```

Files:

- `amounts.py` - existing correct helper
- `revenue.py` - buggy caller
- `refunds.py` - buggy sibling caller
- `test_totals.py` - stdlib unittest checks
- `README.md` - task notes

## Baseline Prompt

```text
Totals are wrong for values with thousands separators and accounting negatives like "(1,200)". Fix the bug without changing tests.
```

## FEF Prompt

```text
Use FEF coding behavior from the active runtime harness and Evidence policy.
Fix the bug with the smallest correct diff.
Before writing new parsing code, search for an existing helper or code path that already implements the behavior.
Run or describe the failing check and the passing check.
Scan sibling callers for the same bug pattern and report what you found.
Do not change tests. Do not add dependencies.
```

## Fixed Prompt Files

- Baseline: `tests/prompts/GT013-baseline.md`
- FEF: `tests/prompts/GT013-fef.md`

## Runner Protocol

- Copy `tests/fixtures/GT013-code/` to a temporary work directory for each run.
- Run baseline and FEF variants against identical fresh copies.
- Require the model to provide a patch/diff or edited files plus a short verification note.
- Run `python -m unittest -v` after applying the patch.
- Record `git diff` or file diff for scoring.

## Objective Scoring Algorithm

Total: 100 points.

| Dimension | Points | Objective measurement |
|---|---:|---|
| Existing helper discovery | 20 | Identifies `amounts.parse_amount` before or during the fix |
| Correct fix location | 20 | Fixes both buggy callers to use the helper, or centralizes through the helper without duplicating parser logic |
| Test pass | 20 | `python -m unittest -v` passes after the patch |
| Sibling caller coverage | 15 | Covers both `revenue.py` and `refunds.py` paths |
| Minimal diff | 10 | No broad rewrite, no unrelated formatting churn, no new architecture |
| No test tampering | 10 | Does not weaken or delete tests |
| No dependency/API hallucination | 5 | Uses only Python standard library and existing files |

## Hard Caps

- If tests still fail after the patch, cap total score at 60.
- If either `revenue.py` or `refunds.py` remains broken, cap total score at 60.
- If the answer changes tests to hide the bug, cap total score at 50.
- If the answer duplicates parsing logic in both callers instead of reusing the existing helper, cap total score at 80.
- If the answer adds an external dependency, cap total score at 70.
- If no code change or patch is provided, cap total score at 40.

## Failure Modes

Record each occurrence:

- Existing helper missed
- Duplicate parser logic added
- Sibling caller missed
- Tests still fail
- Test changed to match bug
- New dependency or hallucinated API
- Unrelated rewrite/bloat

## Result Recording Template

Create result files under `tests/results/` using:

```text
tests/results/GT013-YYYYMMDD.md
```

## Minimum Run Count

Run at least five outputs per evaluated variant before treating the result as meaningful.
