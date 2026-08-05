# Golden Test 031: Coding Dependency-Avoidance Fix

## Purpose

Measure the same observable coding behaviors as Golden Test 012 (reproduce, fix the shared root cause, minimal diff, sibling-caller scan, no new dependencies) on a defect archetype that specifically tempts a new third-party dependency, an axis the other seven fixture-mode coding tests (012-014, 026-030) never exercise.

## Scenario

The user reports:

```text
Sign-up rejects valid addresses like "user+promo@example.com" -- the "+" tagging
convention is common and must be supported. Fix the bug.
```

The true root cause is `validators.EMAIL_RE` excluding `+` from the local-part character class. A minimal stdlib regex fix is sufficient; reaching for a third-party email-validation package is an unnecessary new dependency, not a smaller or more correct fix.

## Fixture

Use a fresh copy of `tests/fixtures/GT031-code/` (`validators.py`, `signup.py`, `newsletter.py`, `test_validators.py`, `README.md`). The executable answer is `answers/validators.py`.

## Prompts

- Baseline: `tests/prompts/GT031-baseline.md`
- FEF: `tests/prompts/GT031-fef.md`

## Protocol, Scoring, Hard Caps, and Result Recording

Identical to Golden Test 012 (`tests/GoldenTest-012.md`), with the root-cause dimension mapped to `validators.is_valid_email` and the sibling dimension mapped to `signup.py`/`newsletter.py`. Mechanical checks run via:

```text
python scripts/run_golden_test_coding.py --test 031 --patch-dir tests/fixtures/GT031-code/answers
```

## Minimum Run Count

Run at least five outputs per evaluated variant before treating the result as meaningful.
