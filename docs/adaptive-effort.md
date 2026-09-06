# Adaptive Effort / Complexity Router

Compact tiering so simple asks stay Kernel-only while hard work escalates **model before packs**. Does not replace `docs/loading-map.md` Load Limits or the Model-Invariant Floor.

**When to load:** only when choosing/switching models by complexity, explaining L0–L3, or resolving an escalation dispute. Do **not** preload on L0–L1 cold-start.

## Tier Table

| Tier | Signals (examples) | Model default | Load |
|---|---|---|---|
| L0 Quick | definition, yes/no, trivial lookup, single short fact | Haiku 4.5 | Kernel only |
| L1 Routine | small edit, simple coding, short summary, one-file | Sonnet 5 | Kernel + ≤1 module/section |
| L2 Complex everyday | multi-step, multi-file, architecture lite, careful review | Opus 5 (1M) | Kernel + loading-map caps (existing Load Limits) |
| L3 Hardest / long-running | deep RCA, large refactor, multi-hour agent work, high-stakes | Fable 5.1 | Kernel + map caps; may use 1 workflow/reviewer only if risk needs it |

## Rules

1. **Classify first from the user ask** (object + risk), not from available files.
2. **Start at the lowest tier that is safe**; escalate only when blocked twice, ambiguity/risk rises, or the user asks for depth.
3. **Escalate model before expanding packs** (invariant floor).
4. **Never preload** `docs/model-usage.md`, README, CHANGELOG, PROGRESS, or SESSION_LOG on L0–L1.
5. L0 forbids multi-pack load (Kernel only). L1 may add at most one module/section. L2–L3 stay inside loading-map Load Limits (Module 1 / Domain ≤2 / Workflow 1 / Reviewer 1 / Policies ≤3); L3 may use one workflow or one reviewer only when risk requires it.

## Escalation Ladder

`Haiku (L0)` → `Sonnet (L1)` → `Opus (L2)` → `Fable (L3)`.

De-escalate when remaining work is routine. Model capacity goes to deeper reasoning within the same loaded set — not extra file dumps.

## Relation to Other Docs

- Pack selection: `docs/loading-map.md`
- Model floor / roster notes: `docs/model-usage.md`
- Entry pointer: `CLAUDE.md` § Adaptive Effort
