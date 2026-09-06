# Adaptive Effort / Complexity Router

Compact tiering so everyday work defaults to **Sonnet** while Haiku is reserved for light Notion/doc recording. Escalate **model before packs**. Does not replace `docs/loading-map.md` Load Limits or the Model-Invariant Floor.

**When to load:** only when choosing/switching models by complexity, explaining L0–L3, or resolving an escalation dispute. Do **not** preload on L0–L1 cold-start.

## Tier Table

| Tier | Signals (examples) | Model default | Load |
|---|---|---|---|
| L0 Light docs | Notion notes/rows, short doc capture, trivial filing, simple checklist ticks | Haiku 4.5 | Kernel only (or Kernel + 1 Notion/doc section if needed) |
| L1 Default / routine | coding, summaries, Q&A, edits, most everyday asks — **default when unsure** | Sonnet 5 | Kernel + ≤1 module/section |
| L2 Complex everyday | multi-step, multi-file, architecture lite, careful review | Opus 5 (1M) | Kernel + loading-map caps (existing Load Limits) |
| L3 Hardest / long-running | deep RCA, large refactor, multi-hour agent work, high-stakes | Fable 5.1 | Kernel + map caps; may use 1 workflow/reviewer only if risk needs it |

## Rules

1. **Classify first from the user ask** (object + risk), not from available files.
2. **When unsure → Sonnet (L1), not Haiku.** Prefer Sonnet as the safe default for everyday work.
3. **Haiku only when the ask is clearly light Notion/doc recording** (narrow gate: notes, rows, short docs, trivial filings, simple checklist ticks) — not a general “anything quick” floor.
4. **Escalate model before expanding packs** (invariant floor).
5. **Never preload** `docs/model-usage.md`, README, CHANGELOG, PROGRESS, or SESSION_LOG on L0–L1.
6. L0 may use Kernel only, or Kernel + at most one Notion/doc section. L1 may add at most one module/section. L2–L3 stay inside loading-map Load Limits (Module 1 / Domain ≤2 / Workflow 1 / Reviewer 1 / Policies ≤3); L3 may use one workflow or one reviewer only when risk requires it. Do not lower the floor too far — over-routing to Haiku is undesirable.

## Escalation Ladder

`Haiku (L0)` → `Sonnet (L1)` → `Opus (L2)` → `Fable (L3)`.

De-escalate when remaining work is routine. Model capacity goes to deeper reasoning within the same loaded set — not extra file dumps.

## Relation to Other Docs

- Pack selection: `docs/loading-map.md`
- Model floor / roster notes: `docs/model-usage.md`
- Entry pointer: `CLAUDE.md` § Adaptive Effort
