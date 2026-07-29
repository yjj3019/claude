# Opus 5 Diagnostic Findings (DIAGNOSTIC-D)

Date: 2026-07-29

This document summarizes a single-operator diagnostic comparison of Claude Opus 5
baseline versus Opus 5 + FEF (routed) on five private-holdout evidence-judgment
scenarios. It is diagnostic only. It is not a benchmark promotion result and must
not be cited as one.

## Execution

- Opus 5 baseline (`O5-B`): 5 runs
- Opus 5 + FEF (`O5-F`): 5 runs
- Total: 10 runs, one repetition per condition (`diagnostic_only`)
- Model confirmed via the Claude.ai chat surface for each run
- No fallback observed on any run
- `tool_calls: 0` on every run (required constraint, not merely observed)

## Results

| Metric | Baseline (O5-B) | FEF (O5-F) |
|---|---|---|
| Semantically correct | 5 / 5 | 5 / 5 |
| Automatic pass (lexical scorer) | 4 / 5 | 5 / 5 |
| Hard failure | 0 | 0 |
| Manual review | 1 | 0 |

Hard failures: 0 across all 10 runs. Manual review: 1 run, baseline only.

The single manual-review case was a missing exact required substring ("남아") in
an otherwise semantically correct, fully evidence-faithful response — a lexical
scorer limitation, not a semantic failure. The response conveyed the same
non-completion finding using different wording (e.g. "잔존", "남는 가설") that the
current exact-substring check does not recognize as equivalent.

## Scenario-Level Qualitative Notes

- **PRIVATE-001**: FEF was marginally better at handling residual uncertainty in
  the evidence (e.g. distinguishing confirmed backfill count from unconfirmed
  target/idempotency assumptions).
- **PRIVATE-002 / PRIVATE-003**: No material difference between baseline and FEF.
- **PRIVATE-004**: Baseline was more concise; FEF was more detailed than the
  scenario required (over-elaboration, not incorrectness).
- **PRIVATE-005**: Baseline's duplicate-charge risk analysis was stronger than
  FEF's on this run.

## Overall

- Opus 5 already performs FEF-style evidence/inference separation in its
  unassisted baseline on these scenarios.
- No net improvement from FEF was observed on this sample beyond the lexical
  scorer difference explained above.
- For simple evidence-judgment tasks, a Kernel-only configuration is the
  recommended default; the full routed pack set did not show an added benefit
  here.

## Limitations

- 5 scenarios, 1 repetition per condition — not enough for a reliability or
  statistical-significance claim.
- `diagnostic_only`: no independent private-holdout provenance verification and
  no semantic-similarity leakage evidence were produced for this batch.
- Must not be used as grounds for formal benchmark promotion (`GO`/`CONDITIONAL_GO`).

## Recommended Next Steps

- Add proportionality/conciseness as a scored dimension — the PRIVATE-004
  over-elaboration gap would not be visible in the current pass/fail scorer.
- Expand the exact-phrase check to phrase groups (equivalent wording) for terms
  like "남아" in a future dataset version, rather than a single required string.
- Do not modify DIAGNOSTIC-D or its existing stored results to produce this
  summary; they remain as originally collected.
