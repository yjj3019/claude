# Golden Test 026: Coding Mutable Default Fix

## Purpose

Measure the same observable coding behaviors as Golden Test 012 (reproduce, fix the shared root cause, minimal diff, sibling-caller scan, no new dependencies) on a distinct defect archetype.

## Scenario

The user reports:

```text
Records are sharing tags: tagging the second record shows the first record's tag too.
Please fix the bug.
```

The true root cause is in `tagging.add_tag`. A sibling-only workaround in `reports.py` can hide the symptom for one caller while leaving the shared defect in place.

## Fixture

Use a fresh copy of `tests/fixtures/GT026-code/` (`tagging.py`, `reports.py`, `test_tagging.py`, `README.md`). The executable answer is `answers/tagging.py`.

## Prompts

- Baseline: `tests/prompts/GT026-baseline.md`
- FEF: `tests/prompts/GT026-fef.md`

## Protocol, Scoring, Hard Caps, and Result Recording

Identical to Golden Test 012 (`tests/GoldenTest-012.md`), with the root-cause dimension mapped to `tagging.add_tag` and the sibling dimension mapped to `reports.py`. Mechanical checks run via:

```text
python scripts/run_golden_test_coding.py --test 026 --patch-dir tests/fixtures/GT026-code/answers
```

## Minimum Run Count

Run at least five outputs per evaluated variant before treating the result as meaningful.
