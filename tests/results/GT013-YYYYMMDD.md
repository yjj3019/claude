# GT013 Result - YYYY-MM-DD

## Run Setup

- Test: GT013 - Coding Existing-Helper Reuse
- Fixture: `tests/fixtures/GT013-code/`
- Answer key: `tests/fixtures/GT013-answer-key.md`
- Baseline runs: 0
- FEF runs: 0
- Fable5 reference runs: 0
- Model/environment:
- Evaluator:
- Status: NOT RUN

## Score Summary

| Variant | Average | Std Dev | Min | Max | Transfer vs Fable5 Avg |
|---|---:|---:|---:|---:|---:|
| Fable5 | | | | | 100% |
| Opus+FEF | | | | | |
| Sonnet+FEF | | | | | |
| Baseline | | | | | |

## Per-Run Scores

| Run ID | Variant | Helper /20 | Location /20 | Tests /20 | Sibling /15 | Minimal /10 | No Test Tamper /10 | No Dependency /5 | Total /100 | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|

## Failure Mode Counts

| Failure Mode | Fable5 | Opus+FEF | Sonnet+FEF | Baseline |
|---|---:|---:|---:|---:|
| Existing helper missed | | | | |
| Duplicate parser logic added | | | | |
| Sibling caller missed | | | | |
| Tests still fail | | | | |
| Test changed to match bug | | | | |
| New dependency/API hallucination | | | | |
| Unrelated rewrite/bloat | | | | |

## Decision

PASS/HOLD/FAIL:
