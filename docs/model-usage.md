# Model Usage Guide

This guide explains how to apply FEF across stronger reviewer models and faster builder models.
It does not claim that prompts increase model intelligence.

## Purpose

Use model capability deliberately:

- fast models for drafting, restructuring, extraction, and repetitive production work
- stronger models for ambiguity resolution, contradiction detection, technical review, and final decision support

FEF should improve consistency, calibration, and reviewability across both roles.

Use `docs/fable-transfer-protocol.md` when Fable5 feedback is used to improve Opus/Sonnet behavior.

## Role Split

| Role | Best Use | Avoid |
|---|---|---|
| Builder | first drafts, outlines, tables, summaries, document assembly, format conversion | final high-risk claims without review |
| Reviewer | technical correctness, proposal logic, evidence discipline, risk review, contradiction detection | rewriting everything when a targeted review is enough |
| Architect | operating model, trade-off analysis, migration strategy, domain framing | cosmetic edits |

## Execution Shape

Choose the smallest shape that fits the dependency structure:

| Shape | Use when | Avoid when |
|---|---|---|
| Single session | Small, sequential, tightly coupled work with a clear target | Independent work would otherwise block the main task |
| Parallel subagents | Research, repository scans, comparisons, or other independent subtasks | The work is sequential or agents would edit the same files |
| Agent team | Peers must exchange evidence, challenge competing hypotheses, or coordinate directly | Ordinary delegation and aggregation are enough |
| External automation | Steps are stable, repeated, triggered externally, or must run unattended | The task is a one-off Markdown workflow |

Keep Markdown files under `workflows/` distinct from executable external automation. A project lesson remains local until repeated evidence, a clear trigger, and a removal condition justify broader promotion; update an existing lesson rather than duplicating it.

## Model and Effort Examples

Model availability and names vary by platform and release; treat these as operating examples, not API contracts.

| Work | Model class | Effort |
|---|---|---|
| Simple extraction or recording | Lowest-cost capable model | low |
| General writing or implementation | Sonnet-class model | medium |
| Technical judgment or independent review | Opus-class model | high |
| Hardest long-horizon autonomous work | Fable-class model, when available | high; xhigh only when capability justifies latency and cost |

## Recommended Flow

For substantial enterprise artifacts:

1. Builder drafts using Kernel + loading map.
2. Reviewer checks only the highest-risk dimensions.
3. Builder applies accepted fixes.
4. Final reviewer pass runs once if the artifact is external-facing.

Do not create endless review loops.
Reviewer runs at most once per artifact unless the user explicitly asks for another pass.

## Task Routing

Use this table only to choose the model role. Use `docs/loading-map.md` for FEF pack selection.

| Task | Preferred Role |
|---|---|
| RHEL proposal draft | Builder |
| RHEL proposal final review | Reviewer |
| Operations manual draft | Builder |
| Operations manual safety review | Reviewer |
| RCA | Reviewer first, Builder second |
| Architecture decision | Architect |
| Research brief | Builder then Reviewer if external |
| Prompt/framework improvement | Architect |

## Escalation Triggers

Use the stronger reviewer/architect role when the task includes:

- public-sector, legal, compliance, security, or financial implications
- lifecycle, support, certification, or version-sensitive claims
- migration or rollback risk
- customer-facing proposal language
- contradictory or ambiguous requirements
- production incident analysis

## Output Discipline

- Drafting should optimize for completeness and usable structure.
- Reviewing should optimize for correctness, risk, and evidence.
- Finalization should optimize for concise, decision-ready output.

Do not imitate another model's personality or hidden reasoning style.
Replicate only observable engineering behaviors: context framing, evidence discipline, calibrated claims, and targeted review.
