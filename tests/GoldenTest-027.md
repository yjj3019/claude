# Golden Test 027: Coding Internal-State Aliasing Fix

## Purpose

Measure the same observable coding behaviors as Golden Test 012 (reproduce, fix the shared root cause, minimal diff, sibling-caller scan, no new dependencies) on a distinct defect archetype.

## Scenario

The user reports:

```text
After running an audit report, the live inventory is reordered and contains "AUDITED".
Please fix the bug.
```

The true root cause is in `inventory.list_items`. A sibling-only workaround in `audit.py` can hide the symptom for one caller while leaving the shared defect in place.

## Fixture

Use a fresh copy of `tests/fixtures/GT027-code/` (`inventory.py`, `audit.py`, `test_inventory.py`, `README.md`). The executable answer is `answers/inventory.py`.

## Prompts

- Baseline: `tests/prompts/GT027-baseline.md`
- FEF: `tests/prompts/GT027-fef.md`

## Protocol, Scoring, Hard Caps, and Result Recording

Identical to Golden Test 012 (`tests/GoldenTest-012.md`), with the root-cause dimension mapped to `inventory.list_items` and the sibling dimension mapped to `audit.py`. Mechanical checks run via:

```text
python scripts/run_golden_test_coding.py --test 027 --patch-dir tests/fixtures/GT027-code/answers
```

## Minimum Run Count

Run at least five outputs per evaluated variant before treating the result as meaningful.
