# Fable Leakage Diagnostic Baseline

## Scope

This is a diagnostic comparison, not private-holdout certification. It compares
the 15 files under `tests/benchmarks/pilot/PB001` through `PB006` with these six
tracked distillation or validation references:

- `docs/fable-pattern-bank.md`
- `docs/fable-distillation-prompts.md`
- `docs/fable-transfer-protocol.md`
- `tests/results/GT012-20260710.md`
- `tests/results/GT013-20260710.md`
- `tests/results/GT014-20260710.md`

## 2026-07-21 Result

- Pair comparisons: 90
- Exact hash matches: 0
- Normalized 8-gram overlaps: 0
- Maximum deterministic MinHash similarity: 0.0
- Canary hits: 0 (no private canary set was available)
- Semantic similarity: `not_run`
- Implemented-check result: PASS
- Promotion eligibility: false

The local detailed report is stored at
`.local/fable/leakage/smoke-vs-distillation.json` and is intentionally Git-ignored.
Its SHA-256 at execution was
`6af9e1fa9cfb9500495a5db1185142fb2f281d45cc8f0f1b0bed04154ffeb529`.

## Interpretation

The public smoke fixtures contain no detected verbatim or normalized 8-gram
reuse from the tracked distillation/validation material. This does not establish
semantic independence, private-holdout provenance, or promotion readiness.
Promotion remains blocked until an independently maintained private corpus,
secret canaries, and semantic-similarity evidence are supplied.
