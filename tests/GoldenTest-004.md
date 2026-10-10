# Golden Test 004: OpenShift Analysis

## Task

Analyze OpenShift release impact.

## Evaluation

Score 1-5 for:

- problem framing
- evidence handling
- calibration
- structure
- operational usefulness
- risk handling
- completeness
- review quality

## Compare

Run:

1. Baseline model
2. Model + FEF

Record:

- baseline score
- FEF score
- improvement
- remaining weakness

## Reproducible synthetic input

Use [evidence](fixtures/GT004-evidence.md) and the [baseline](prompts/GT004-baseline.md) / [FEF](prompts/GT004-fef.md) task pair. Evaluators use the [answer key](fixtures/GT004-answer-key.md) for expected facts, critical failures and scoring anchors. The model must not receive the key. This manual test is **NOT_RUN**; CI checks availability and contracts only.
