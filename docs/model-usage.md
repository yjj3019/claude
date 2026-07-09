# Model Usage Guide

This guide explains how to apply FEF across stronger reviewer models and faster builder models.
It does not claim that prompts increase model intelligence.

## Purpose

Use model capability deliberately:

- fast models for drafting, restructuring, extraction, and repetitive production work
- stronger models for ambiguity resolution, contradiction detection, technical review, and final decision support

FEF should improve consistency, calibration, and reviewability across both roles.

## Role Split

| Role | Best Use | Avoid |
|---|---|---|
| Builder | first drafts, outlines, tables, summaries, document assembly, format conversion | final high-risk claims without review |
| Reviewer | technical correctness, proposal logic, evidence discipline, risk review, contradiction detection | rewriting everything when a targeted review is enough |
| Architect | operating model, trade-off analysis, migration strategy, domain framing | cosmetic edits |

## Recommended Flow

For substantial enterprise artifacts:

1. Builder drafts using Kernel + loading map.
2. Reviewer checks only the highest-risk dimensions.
3. Builder applies accepted fixes.
4. Final reviewer pass runs once if the artifact is external-facing.

Do not create endless review loops.
Reviewer runs at most once per artifact unless the user explicitly asks for another pass.

## Task Routing

| Task | Preferred Role | FEF Packs |
|---|---|---|
| RHEL proposal draft | Builder | Proposal + RHEL + Proposal Workflow |
| RHEL proposal final review | Reviewer | Proposal Reviewer + Technical Reviewer if needed |
| Operations manual draft | Builder | Manual + RHEL/Linux + Manual Workflow |
| Operations manual safety review | Reviewer | Documentation Reviewer + Technical Reviewer |
| RCA | Reviewer first, Builder second | RCA + Evidence + Technical Reviewer |
| Architecture decision | Architect | Architecture + relevant domain + Decision/Evidence |
| Research brief | Builder then Reviewer if external | Research + Evidence |
| Prompt/framework improvement | Architect | PromptEngineering + Review |

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
