# Kernel-Only vs FEF Diagnostic — Design

This is a design document. No dataset, prompts, or execution plan exist yet.
No model or MCP/SSH execution has occurred for this experiment. Do not create
`v4` or run any prompt until this design is explicitly approved.

## Purpose

`docs/opus5-diagnostic-findings.md` (DIAGNOSTIC-D) compared Opus 5 baseline
against Opus 5 + full routed FEF and found no net improvement on simple
evidence-judgment scenarios, recommending a Kernel-only default for that task
shape. This experiment tests that recommendation directly: does full FEF give
a real advantage over Kernel-only on simple evidence judgment, or is Kernel
alone sufficient?

## Comparison Conditions

- Kernel-only (Kernel + Meta Rules + Checklist, no loading-map packs)
- FEF (routed: Kernel + `docs/loading-map.md`-selected packs)
- Same evidence fixtures presented identically to both conditions

## Scope

- Model: Claude Opus 5
- Minimum scenarios: 5
- Repetitions: at least 3 per condition per scenario

## Evaluation Axes

1. Factual accuracy
2. Presence of unsupported claims
3. Completion-status judgment
4. Instruction adherence
5. Response proportionality

## Success Criteria

- FEF shows a clear improvement in accuracy or safety over Kernel-only.
- Any increase in response length is proportional to the improvement it buys.
- Wording differences alone do not count as improvement.

## Abort Conditions

- A tool call occurs.
- The served model cannot be confirmed.
- A fallback occurs.
- A response asserts success beyond what the evidence supports.

## Constraints

- `diagnostic_only`.
- Not usable alone as promotion evidence.
- Must not modify `v3` or `DIAGNOSTIC-D`.

## Current Decision

Design only. Creating a `v4` holdout version and running any model against it
are both deferred until this design is explicitly approved.
