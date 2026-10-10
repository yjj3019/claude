# Golden Test 003: RCA

## Task

Analyze a Linux incident and write RCA.

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

Use [evidence](fixtures/GT003-evidence.md) and the [baseline](prompts/GT003-baseline.md) / [FEF](prompts/GT003-fef.md) task pair. Evaluators use the [answer key](fixtures/GT003-answer-key.md) for expected facts, critical failures and scoring anchors. The model must not receive the key. This manual test is **NOT_RUN**; CI checks availability and contracts only.
