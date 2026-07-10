# Golden Test 012: Coding Root-Cause Fix

## Purpose

Measure whether Opus/Sonnet+FEF reproduce observable Fable5 coding behaviors on a small, fact-checkable bug fix task:

- reproduce the failure
- fix the shared root cause
- keep the diff minimal
- reuse existing code paths
- scan sibling callers for the same bug pattern
- avoid hallucinated APIs or new dependencies

This test evaluates behavior, not personality imitation.

## Scenario

A small Python codebase calculates order totals and refund totals from CSV-like rows.
The user reports:

```text
Totals are wrong when amount values contain comma thousands separators, for example "1,200".
Please fix the bug.
```

The true root cause is in the shared money parser. A caller-only fix can make one path pass while leaving the sibling path broken.

## Fixture

Use a fresh copy of:

```text
tests/fixtures/GT012-code/
```

Files:

- `money.py` - shared parser with the seeded bug
- `orders.py` - one caller
- `refunds.py` - sibling caller
- `test_money.py` - stdlib unittest checks
- `README.md` - task notes

## Baseline Prompt

```text
The tests fail for amounts like "1,200". Fix the bug.
```

## FEF Prompt

```text
Use FEF coding behavior from the active runtime harness and Evidence policy.
Fix the bug with the smallest correct diff.
First identify the shared root cause, then patch the shared function if appropriate.
Run or describe the failing check and the passing check.
After the fix, scan sibling callers for the same bug pattern and report what you found.
Do not add dependencies.
```

## Fixed Prompt Files

- Baseline: `tests/prompts/GT012-baseline.md`
- FEF: `tests/prompts/GT012-fef.md`

## Runner Protocol

- Copy `tests/fixtures/GT012-code/` to a temporary work directory for each run.
- Run baseline and FEF variants against identical fresh copies.
- Keep model, environment, and generation settings fixed where possible.
- Require the model to provide a patch/diff or edited files plus a short verification note.
- Run `python -m unittest -v` after applying the patch.
- Record `git diff` or file diff for scoring.
- Blind evaluator scoring where practical; at minimum hide variant labels during scoring.

## Objective Scoring Algorithm

Total: 100 points.

| Dimension | Points | Objective measurement |
|---|---:|---|
| Reproduction check | 15 | Mentions or runs a failing check before/while fixing, and a passing check after fixing |
| Root-cause location | 20 | Fixes the shared parser in `money.py::parse_money`, not only `orders.py` or `refunds.py` |
| Test pass | 20 | `python -m unittest -v` passes after the patch |
| Sibling caller coverage | 15 | Fix covers both `orders.total_orders` and `refunds.total_refunds`; answer mentions sibling scan or equivalent |
| Minimal diff | 10 | No broad rewrite, no unrelated formatting churn, no new architecture |
| Existing pattern reuse | 5 | Keeps callers using `parse_money` instead of duplicating parsing logic |
| Error handling quality | 10 | Does not silently convert invalid non-empty values to `0`; preserves blank/None handling |
| No hallucinated dependency/API | 5 | Uses only Python standard library and existing files |

## Hard Caps

- If tests still fail after the patch, cap total score at 60.
- If the fix is caller-only and leaves either orders or refunds broken, cap total score at 55.
- If the answer adds an external dependency, cap total score at 70.
- If the answer rewrites the whole fixture or changes tests to hide the bug, cap total score at 50.
- If no code change or patch is provided, cap total score at 40.

## Failure Modes

Record each occurrence:

- No reproduction check
- Caller-only fix
- Sibling caller missed
- Tests still fail
- Test changed to match bug
- Silent invalid-value fallback introduced
- New dependency or hallucinated API
- Unrelated rewrite/bloat

## Result Recording Template

Create result files under `tests/results/` using:

```text
tests/results/GT012-YYYYMMDD.md
```

Each result file should include:

```markdown
# GT012 Result - YYYY-MM-DD

## Run Setup

- Test: GT012 - Coding Root-Cause Fix
- Fixture: `tests/fixtures/GT012-code/`
- Baseline runs: N
- FEF runs: N
- Fable5 reference runs: N, if available
- Model/environment:
- Evaluator:

## Score Summary

| Variant | Average | Std Dev | Min | Max | Transfer vs Fable5 Avg |
|---|---:|---:|---:|---:|---:|
| Fable5 | | | | | 100% |
| Opus+FEF | | | | | |
| Sonnet+FEF | | | | | |
| Baseline | | | | | |

## Per-Run Scores

| Run ID | Variant | Repro /15 | Root Cause /20 | Tests /20 | Sibling /15 | Minimal /10 | Reuse /5 | Error Handling /10 | No Dependency /5 | Total /100 | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|

## Failure Mode Counts

| Failure Mode | Fable5 | Opus+FEF | Sonnet+FEF | Baseline |
|---|---:|---:|---:|---:|
| No reproduction check | | | | |
| Caller-only fix | | | | |
| Sibling caller missed | | | | |
| Tests still fail | | | | |
| Test changed to match bug | | | | |
| Silent invalid-value fallback | | | | |
| New dependency/API hallucination | | | | |
| Unrelated rewrite/bloat | | | | |

## Decision

PASS for a model if:

- average score is at least 85, and
- standard deviation is lower than baseline, and
- root-cause location pass rate is at least 80%, and
- no run changes tests to hide the bug.
```

## Minimum Run Count

Run at least five outputs per evaluated variant before treating the result as meaningful.
