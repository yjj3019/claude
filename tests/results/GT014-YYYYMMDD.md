# GT014 Result - YYYY-MM-DD

## Run Setup

- Test: GT014 - Coding Boundary Root-Cause Fix
- Fixture: `tests/fixtures/GT014-code/`
- Answer key: `tests/fixtures/GT014-answer-key.md`
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

| Run ID | Variant | Repro /10 | Root Cause /25 | Tests /20 | Sibling /15 | Minimal /10 | No Caller Special-Case /10 | No Test/Dependency /10 | Total /100 | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|

## Failure Mode Counts

| Failure Mode | Fable5 | Opus+FEF | Sonnet+FEF | Baseline |
|---|---:|---:|---:|---:|
| No reproduction check | | | | |
| Caller-only fix | | | | |
| Sibling caller missed | | | | |
| Tests still fail | | | | |
| Test changed to match bug | | | | |
| Duplicate boundary logic added | | | | |
| New dependency/API hallucination | | | | |
| Unrelated rewrite/bloat | | | | |

## Decision

PASS/HOLD/FAIL:
