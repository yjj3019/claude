# Golden Test 029: Coding Numeric-String Sort Fix

## Purpose

Measure the same observable coding behaviors as Golden Test 012 (reproduce, fix the shared root cause, minimal diff, sibling-caller scan, no new dependencies) on a distinct defect archetype.

## Scenario

The user reports:

```text
Entry id "10" is ranked before id "9". Ids are numeric strings and must sort numerically.
Please fix the bug.
```

The true root cause is in `ranking.order_by_id`. A sibling-only workaround in `leaderboard.py` can hide the symptom for one caller while leaving the shared defect in place.

## Fixture

Use a fresh copy of `tests/fixtures/GT029-code/` (`ranking.py`, `leaderboard.py`, `test_ranking.py`, `README.md`). The executable answer is `answers/ranking.py`.

## Prompts

- Baseline: `tests/prompts/GT029-baseline.md`
- FEF: `tests/prompts/GT029-fef.md`

## Protocol, Scoring, Hard Caps, and Result Recording

Identical to Golden Test 012 (`tests/GoldenTest-012.md`), with the root-cause dimension mapped to `ranking.order_by_id` and the sibling dimension mapped to `leaderboard.py`. Mechanical checks run via:

```text
python scripts/run_golden_test_coding.py --test 029 --patch-dir tests/fixtures/GT029-code/answers
```

## Minimum Run Count

Run at least five outputs per evaluated variant before treating the result as meaningful.
