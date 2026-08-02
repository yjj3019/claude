# Golden Test 030: Coding Float Money Fix

## Purpose

Measure the same observable coding behaviors as Golden Test 012 (reproduce, fix the shared root cause, minimal diff, sibling-caller scan, no new dependencies) on a distinct defect archetype.

## Scenario

The user reports:

```text
Charging 0.10 + 0.20 shows 0.30000000000000004 on the statement.
Please fix the bug.
```

The true root cause is in `wallet.charge_total`. A sibling-only workaround in `statements.py` can hide the symptom for one caller while leaving the shared defect in place.

## Fixture

Use a fresh copy of `tests/fixtures/GT030-code/` (`wallet.py`, `statements.py`, `test_wallet.py`, `README.md`). The executable answer is `answers/wallet.py`.

## Prompts

- Baseline: `tests/prompts/GT030-baseline.md`
- FEF: `tests/prompts/GT030-fef.md`

## Protocol, Scoring, Hard Caps, and Result Recording

Identical to Golden Test 012 (`tests/GoldenTest-012.md`), with the root-cause dimension mapped to `wallet.charge_total` and the sibling dimension mapped to `statements.py`. Mechanical checks run via:

```text
python scripts/run_golden_test_coding.py --test 030 --patch-dir tests/fixtures/GT030-code/answers
```

## Minimum Run Count

Run at least five outputs per evaluated variant before treating the result as meaningful.
