# Golden Test 028: Coding BOM Header Fix

## Purpose

Measure the same observable coding behaviors as Golden Test 012 (reproduce, fix the shared root cause, minimal diff, sibling-caller scan, no new dependencies) on a distinct defect archetype.

## Scenario

The user reports:

```text
KeyError: 'name' when reading the exported CSV, but the header clearly says name,score.
Please fix the bug.
```

The true root cause is in `loader.parse_export`. A sibling-only workaround in `summary.py` can hide the symptom for one caller while leaving the shared defect in place.

## Fixture

Use a fresh copy of `tests/fixtures/GT028-code/` (`loader.py`, `summary.py`, `test_loader.py`, `README.md`). The executable answer is `answers/loader.py`.

## Prompts

- Baseline: `tests/prompts/GT028-baseline.md`
- FEF: `tests/prompts/GT028-fef.md`

## Protocol, Scoring, Hard Caps, and Result Recording

Identical to Golden Test 012 (`tests/GoldenTest-012.md`), with the root-cause dimension mapped to `loader.parse_export` and the sibling dimension mapped to `summary.py`. Mechanical checks run via:

```text
python scripts/run_golden_test_coding.py --test 028 --patch-dir tests/fixtures/GT028-code/answers
```

## Minimum Run Count

Run at least five outputs per evaluated variant before treating the result as meaningful.
