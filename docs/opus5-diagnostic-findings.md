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

## Response Proportionality

Word counts are whitespace-delimited word counts, not API token counts.

| Scenario | Baseline (words) | FEF (words) | FEF / Baseline |
|---|---:|---:|---:|
| PRIVATE-001 | 188 | 355 | 1.89× |
| PRIVATE-002 | 274 | 314 | 1.15× |
| PRIVATE-003 | 266 | 259 | 0.97× |
| PRIVATE-004 | 350 | 746 | 2.13× |
| PRIVATE-005 | 902 | 232 | 0.26× |
| **Mean** | 396 | 381 | — |
| **Median** | 274 | 314 | — |

- The PRIVATE-005 baseline response is a length outlier (902 words, more than
  double the next-longest response) and skews the mean toward baseline; the
  mean difference (396 vs. 381) should not be read as "baseline and FEF are
  about the same length" for that reason.
- By median, FEF responses ran about 15% longer than baseline (314 vs. 274
  words).
- Per-scenario variance is large (0.26× to 2.13×) in both directions, so no
  consistent conciseness effect — better or worse — is observed for FEF here.
- With 5 scenarios and one repetition per condition, this is a diagnostic
  observation only, not a proportionality finding with statistical support.

## Overall

- Opus 5 already performs FEF-style evidence/inference separation in its
  unassisted baseline on these scenarios.
- No net improvement from FEF was observed on this sample beyond the lexical
  scorer difference explained above.
- For simple evidence-judgment tasks, a Kernel-only configuration is the
  recommended default; the full routed pack set did not show an added benefit
  here.
- This DIAGNOSTIC-D result is the final evidence basis for closing the current
  Fable work as diagnostic-only.

## DIAGNOSTIC-E Exclusion

DIAGNOSTIC-E was not completed. Its one Claude app response and one CLI smoke
response are excluded from the formal comparison. They do not change or extend
the DIAGNOSTIC-D conclusion, and no additional Claude/API/paid-model execution
is required for this closeout.

## Limitations

- 5 scenarios, 1 repetition per condition — not enough for a reliability or
  statistical-significance claim.
- `diagnostic_only`: no independent private-holdout provenance verification and
  no semantic-similarity leakage evidence were produced for this batch.
- Formal benchmark promotion is **NO-GO** because independently verified
  provenance and semantic evidence are missing.

## Recommended Next Steps

- Add proportionality/conciseness as a scored dimension — the PRIVATE-004
  over-elaboration gap would not be visible in the current pass/fail scorer.
- Expand the exact-phrase check to phrase groups (equivalent wording) for terms
  like "남아" in a future dataset version, rather than a single required string.
- Do not modify DIAGNOSTIC-D or its existing stored results to produce this
  summary; they remain as originally collected.
