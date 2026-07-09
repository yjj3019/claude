# Golden Test 011: Proposal Consistency Check

## Purpose

Evaluate whether FEF improves review quality for an existing proposal by detecting inconsistencies, requirement gaps, unsupported claims, and reviewer-facing risks.

This test is domain-neutral by default. Add the relevant Domain Pack only when the proposal contains domain-specific technical, security, compliance, or operational claims.

## Scenario

A draft enterprise proposal is ready for internal review before customer submission.
The user asks:

```text
Check this proposal for consistency.
```

The proposal contains intentional issues across executive summary, solution description, roadmap, pricing/effort assumptions, and appendix.

## Test Input Shape

Include a proposal excerpt with:

- 1 executive summary
- 1 requirements table
- 3-5 solution sections
- 1 roadmap or schedule section
- 1 risk/support section
- 1 appendix or assumptions section

Seed the excerpt with:

- two internal contradictions
- two requirement coverage gaps
- two terminology/name/version inconsistencies
- two unsupported claims
- one roadmap/scope mismatch
- one risk or dependency hidden in the appendix but absent from the main body

## Baseline Prompt

```text
Check this proposal for consistency and list issues.
```

## FEF Prompt

```text
Use FEF Kernel and docs/loading-map.md for a Proposal consistency check.
Apply Proposal Module Consistency Review Mode, Proposal Workflow Consistency Check Workflow, Proposal Reviewer, and relevant Writing/Evidence/Review policies.
Add a Domain Pack and Technical Reviewer only if the proposal includes technical, security, compliance, operational, or version-sensitive claims.
Check the proposal for internal consistency, requirement coverage, claim/evidence alignment, terminology/version/number consistency, and submission risk.
```

## Scoring Rubric

Total: 100 points.

| Dimension | Points | Measurement |
|---|---:|---|
| Internal contradiction detection | 20 | Finds both contradictions and explains why they matter |
| Requirement coverage | 20 | Maps requirements to proposal content and identifies both gaps |
| Terminology/version/number consistency | 15 | Detects inconsistent names, versions, dates, quantities, or scope statements |
| Claim/evidence discipline | 15 | Flags unsupported claims without over-tagging defensible statements |
| Risk and dependency surfacing | 10 | Finds hidden assumptions, exclusions, dependencies, or risks |
| Severity classification | 10 | Classifies issues as Critical/Major/Minor/Suggestion proportionally |
| Actionability | 10 | Provides targeted fixes without rewriting the full proposal unnecessarily |

## Evaluator Notes

- A dimension score must never exceed its maximum points.
- Do not award points for generic advice that does not point to a specific proposal issue.
- If the test excerpt contains technical claims and the answer fails to request or apply relevant domain validation, cap total score at 80.
- If the answer rewrites the whole proposal instead of producing a review, cap actionability at 5/10.
- If the answer misses a submission-blocking contradiction, cap total score at 70.

## Failure Modes

Record each occurrence:

- Contradiction missed
- Requirement gap missed
- Unsupported claim accepted as fact
- Generic review with no traceable issue locations
- Excessive rewrite instead of review
- Severity inflation or under-classification
- Domain-sensitive claim reviewed without relevant domain validation

## Result Recording Template

Create result files under `tests/results/` using:

```text
tests/results/GT011-YYYYMMDD.md
```

Each result file should include:

```markdown
# GT011 Result - YYYY-MM-DD

## Run Setup

- Baseline runs: N
- FEF runs: N
- Model/environment:
- Evaluator:

## Score Summary

| Variant | Average | Std Dev | Min | Max |
|---|---:|---:|---:|---:|
| Baseline | | | | |
| FEF | | | | |

## Dimension Scores

| Dimension | Baseline Avg | FEF Avg | Delta |
|---|---:|---:|---:|
| Internal contradiction detection | | | |
| Requirement coverage | | | |
| Terminology/version/number consistency | | | |
| Claim/evidence discipline | | | |
| Risk and dependency surfacing | | | |
| Severity classification | | | |
| Actionability | | | |

## Failure Mode Counts

| Failure Mode | Baseline Count | FEF Count |
|---|---:|---:|
| Contradiction missed | | |
| Requirement gap missed | | |
| Unsupported claim accepted | | |
| Generic review | | |
| Excessive rewrite | | |
| Severity error | | |
| Missing domain validation | | |

## Decision

PASS if FEF average uplift is at least +10 points and variance decreases.
Otherwise FAIL or HOLD with notes.
```

## Minimum Run Count

Run at least five baseline and five FEF outputs before treating the result as meaningful.
