# GT013 Result - YYYY-MM-DD

## Run Setup

- Test: GT013 - Coding Existing-Helper Reuse
- Fixture: `tests/fixtures/GT013-code/`
- Answer key: `tests/fixtures/GT013-answer-key.md`
- Baseline runs: 0
- FEF runs: 0
- Model/environment (same model and settings for both variants):
- Requested and served model, effort, and any fallback:
- Evaluator:
- Status: NOT RUN

## Score Summary

Record separate rows for each served model, with matched baseline/FEF settings. Replace MODEL with the served model name in every table. Never pool scores or failure counts across models.

| Model | Variant | Average | Std Dev | Min | Max |
|---|---|---:|---:|---:|---:|
| MODEL | FEF | | | | |
| MODEL | Baseline | | | | |

## Per-Run Scores

| Run ID | Model | Variant | Helper /20 | Location /20 | Tests /20 | Sibling /15 | Minimal /10 | No Test Tamper /10 | No Dependency /5 | Total /100 | Notes |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|

## Failure Mode Counts

| Model | Failure Mode | FEF | Baseline |
|---|---|---:|---:|
| MODEL | Existing helper missed | | |
| MODEL | Duplicate parser logic added | | |
| MODEL | Sibling caller missed | | |
| MODEL | Tests still fail | | |
| MODEL | Test changed to match bug | | |
| MODEL | New dependency/API hallucination | | |
| MODEL | Unrelated rewrite/bloat | | |


## Decision

PASS/HOLD/FAIL:
