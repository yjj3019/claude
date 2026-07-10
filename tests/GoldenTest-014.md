# Golden Test 014: Coding Boundary Root-Cause Fix

## Purpose

Measure whether a model fixes a boundary-condition bug in the shared helper instead of special-casing individual callers.

This follows GT012 and GT013. GT014 is still small, but it checks a different coding behavior: inclusive/exclusive boundary reasoning across multiple callers.

## Scenario

A small Python codebase filters billing events and support tickets by service period.
The user reports:

```text
Items that occur on the contract end date are being excluded. The end date should be included.
Please fix the bug without changing tests.
```

The true root cause is in the shared date-range helper. Caller-only fixes can pass one path while leaving the sibling path wrong.

## Fixture

Use a fresh copy of:

```text
tests/fixtures/GT014-code/
```

Files:

- `periods.py` - shared date range helper with the seeded bug
- `billing.py` - one caller
- `support.py` - sibling caller
- `test_periods.py` - stdlib unittest checks
- `README.md` - task notes

## Baseline Prompt

```text
Items that occur on the contract end date are being excluded. The end date should be included. Fix the bug without changing tests.
```

## FEF Prompt

```text
Use FEF coding behavior from the active runtime harness and Evidence policy.
Fix the bug with the smallest correct diff.
Identify the shared root cause before patching individual callers.
Run or describe the failing check and the passing check.
Verify that the patch landed in the literal assigned work directory, not a redirected worktree or scratch copy.
Scan sibling callers for the same boundary bug and report what you found.
Do not change tests. Do not add dependencies.
```

## Fixed Prompt Files

- Baseline: `tests/prompts/GT014-baseline.md`
- FEF: `tests/prompts/GT014-fef.md`

## Runner Protocol

- Copy `tests/fixtures/GT014-code/` to a fresh isolated work directory for each run.
- Apply patches only inside the assigned work directory.
- Before reporting success, verify the diff and `python -m unittest -v` result from that exact assigned directory.
- If a tool redirects edits into a worktree or scratch copy, move or reapply the patch to the assigned directory before scoring.

## Objective Scoring Algorithm

Total: 100 points.

| Dimension | Points | Objective measurement |
|---|---:|---|
| Reproduction check | 10 | Mentions or runs failing and passing `python -m unittest -v` |
| Shared root-cause fix | 25 | Fixes `periods.py::is_within_period` rather than only callers |
| Test pass | 20 | `python -m unittest -v` passes after the patch |
| Sibling caller coverage | 15 | Covers both `billing.py` and `support.py` paths |
| Minimal diff | 10 | No broad rewrite, no unrelated formatting churn, no new architecture |
| No caller special-casing | 10 | Does not duplicate range logic in callers |
| No test tampering/dependency | 10 | Does not change tests or add dependencies; verifies changes landed in the assigned work directory |

## Hard Caps

- If tests still fail after the patch, cap total score at 60.
- If either billing or support remains broken, cap total score at 60.
- If the fix changes tests to hide the bug, cap total score at 50.
- If the answer duplicates date-range logic in both callers instead of fixing the helper, cap total score at 80.
- If no code change or patch is provided, cap total score at 40.

## Failure Modes

Record each occurrence:

- No reproduction check
- Caller-only fix
- Sibling caller missed
- Tests still fail
- Patch applied to redirected worktree instead of assigned directory
- Test changed to match bug
- Duplicate boundary logic added
- New dependency or hallucinated API
- Unrelated rewrite/bloat

## Result Recording Template

Create result files under `tests/results/` using:

```text
tests/results/GT014-YYYYMMDD.md
```

## Minimum Run Count

Run at least five outputs per evaluated variant before treating the result as meaningful.
