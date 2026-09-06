# Model Usage Guide

This guide explains how to apply FEF across stronger reviewer models and faster builder models.
It does not claim that prompts increase model intelligence.

## Purpose

Use model capability deliberately:

- fast models for drafting, restructuring, extraction, and repetitive production work
- stronger models for ambiguity resolution, contradiction detection, technical review, and final decision support

FEF should improve consistency, calibration, and reviewability across both roles.


## When to Load This Doc

Load `docs/model-usage.md` **only** when choosing or switching among Opus / Fable / Sonnet / Haiku, or when tuning effort/thinking for the active model. Do **not** load it every turn, and do not load it for ordinary single-model tasks that already follow the Model-Invariant Floor. Model choice does not justify loading extra packs; escalate the model instead of dumping docs.

## Model Roster (user-authoritative, 2026-09-06)

| Model | Product label | Role |
|---|---|---|
| Opus | Opus 5 (1M context) | Best for everyday complex tasks |
| Fable | Fable 5.1 | Most capable for hardest and longest-running tasks |
| Sonnet | Sonnet 5 | Efficient for routine tasks |
| Haiku | Haiku 4.5 | Fastest for quick answers |

Names and availability vary by platform; treat this roster as the repository preference when the host exposes these models. Verify host availability before switching.

## Model-Invariant Floor

Regardless of which model is selected (Opus / Fable / Sonnet / Haiku):

1. **Same Required Kernel + Operational Integrity** — never skip evidence, completion, file/tool, or freshness gates on Haiku (or any model).
2. **Same Context Budget** — `CLAUDE.md` Kernel plus packs named by `docs/loading-map.md` within Load Limits (Module 1 / Domain ≤2 / Workflow 1 / Reviewer 1 / Policies ≤3). Do not dump extra docs onto weaker models to “compensate,” and do not dump more onto Fable/Opus either.
3. **Same loading map / task routing** — model choice does not change which packs load.
4. **Same output contract** — facts vs assumptions, `[unverified]`, smallest complete change, no fake completion claims.
5. **When blocked:** escalate the model (`Haiku` → `Sonnet` → `Opus` → `Fable`) when blocked twice or risk rises — do **not** expand unrelated instructions as a substitute; gather necessary task evidence.
6. **Stronger models:** still obey budget; extra capacity goes to deeper reasoning within the same loaded set, not extra file loads.

Kernel and Integrity Policies remain model-independent. Model choice does not relax Autoload Protocol or Instruction Precedence.

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

Raise the automation level one shape at a time: single session, then subagent, then team or scheduled/external automation. Move up only after the smaller shape has measured success rate, cost, and rollback safety, tracked the same way as the Effort Calibration Guardrail below; do not start at the largest shape a task could theoretically use.

## Model and Effort Examples

Model availability and names vary by platform and release; treat these as operating examples, not API contracts.

| Work | Model class | Effort |
|---|---|---|
| Simple extraction or recording | Lowest-cost capable model | low |
| General writing or implementation | Sonnet-class model | medium |
| Technical judgment or independent review | Opus-class model | high |
| Hardest long-horizon autonomous work | Fable 5.1, when available | high; xhigh only when capability justifies latency and cost |

### Claude Haiku 4.5 Runtime Notes

For an API runtime explicitly targeting `claude-haiku-4-5`:

- Use Haiku for high-volume extraction, classification, routing, template filling, document or Notion records, brief summaries, and independent lightweight subtasks with an explicit source and output schema.
- Haiku 4.5 supports manual extended thinking, not adaptive thinking. Keep thinking off for routine work; use a bounded thinking budget only when evaluation shows it is cheaper and reliable enough compared with escalation.
- Escalate material ambiguity—conflicting source values, missing required fields, unsupported inference, or a decision that changes downstream action—to Sonnet for one focused interpretation pass. Escalate high-impact legal, financial, security, architecture, or customer-facing judgment to Opus or the designated high-risk reviewer.
- Do not escalate cosmetic wording, obvious formatting, or reversible schema mapping. A stronger model may review meaning but cannot grant authority: destructive, public, permission-changing, or otherwise user-controlled actions still require user approval.
- Respect the 200k context and 64k output limits; chunk and aggregate high-volume work rather than silently truncating it.

Verified 2026-07-26 against Anthropic's [Haiku 4.5 announcement](https://www.anthropic.com/news/claude-haiku-4-5), [Haiku model page](https://www.anthropic.com/claude/haiku), and [current model overview](https://platform.claude.com/docs/en/about-claude/models/overview). Re-check when the model or API behavior changes.

### Notion Record Integrity

Choose the lowest-cost model that preserves the edit contract:

- Use Haiku at low effort for new pages, fixed-schema transcription, simple append operations, and short summaries.
- Use Sonnet at medium effort for exact `old_str`/`new_str` replacement, code-fence or table preservation, and multi-section merges.
- Escalate deletion, structural changes, multiple matches, or child-page/database impact to the designated stronger reviewer or user approval boundary.
- Fetch before editing, update the smallest matching region, and fetch again before claiming completion. Do not pass raw conversations or raw tool responses when a compact record schema is sufficient.

Adopted 2026-07-26 as an FEF operating rule based on an internal operational decision.

For record ownership, lifecycle, deployment-state, and portability rules, use `docs/knowledge-governance.md`.

### Claude Sonnet 5 Runtime Notes

For an API runtime explicitly targeting `claude-sonnet-5`:

- Start at `high` only for initial workload calibration, then record and reuse the lowest effort that preserves Golden Test quality; use `xhigh` for the hardest coding or agentic work and `low` only for short, scoped, latency-sensitive tasks.
- Keep adaptive thinking enabled where possible. Manual extended thinking with `budget_tokens` is invalid, as are non-default `temperature`, `top_p`, and `top_k` values.
- Recount tokens and re-tune `max_tokens`, cost, and latency budgets for Sonnet 5 instead of reusing Sonnet 4.6 measurements; leave output headroom at higher effort.
- State task-wide scope explicitly, keep tool use proportional, and remove rigid progress-update schedules unless evaluation shows they help.

Verified 2026-07-26 against Anthropic's [Sonnet 5 model guide](https://platform.claude.com/docs/en/about-claude/models/whats-new-sonnet-5) and [Sonnet 5 prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5). Re-check when the model or API behavior changes.

### Claude Opus 5 Runtime Notes

For an API runtime explicitly targeting `claude-opus-5`:

- Start at `high` effort and use the lowest level that preserves Golden Test quality; use `max` only when an evaluation shows a material gain.
- Keep thinking enabled where possible. If thinking is disabled, use `high` effort or below; `xhigh` and `max` are invalid with disabled thinking.
- Do not add blanket final-verification, double-check, or verifier-subagent instructions. Use FEF's proportional checkpoint or one-pass review only when task risk requires it.
- Request concise output and intended scope explicitly, and cap subagents to genuinely independent, sizeable work.

Verified 2026-07-26 against Anthropic's [Opus 5 model guide](https://platform.claude.com/docs/en/about-claude/models/whats-new-opus-5) and [Opus 5 prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5). Re-check when the model or API behavior changes.


### Claude Fable 5.1 Runtime Notes

For a runtime explicitly targeting Fable 5.1 (hardest / longest-running work):

- Prefer Fable for multi-hour autonomous agent runs, deep multi-file investigations, conflicting-evidence synthesis, and high-stakes architecture or security judgments when host access is available.
- Keep the same Context Budget and loading map as Opus/Sonnet/Haiku; do not preload every module or doc because the model is stronger.
- Use high effort by default for long-horizon work; raise further only when evaluation shows a material gain worth latency and cost.
- Cap parallel subagents to independent, sizeable work; aggregate once. Prefer checkpoint verification during long runs and at most one reviewer pass after a draft.
- Escalate *to* Fable when Sonnet/Opus are blocked twice on the same obstacle or when task risk clearly requires maximum capability; de-escalate when remaining work is routine.

Recorded 2026-09-06 as repository operating preference (user-authoritative roster). Re-check when the host renames or gates the model.

### Effort Calibration Guardrail

Run an effort sweep during model or prompt evaluation, not on every request. Record the chosen effort per stable workload class and re-run the sweep only after a model or prompt change, an acceptance regression, or a material cost or latency shift.

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
