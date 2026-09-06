# Adaptive Effort / Complexity Router

Compact tiering so everyday work defaults to **Sonnet** while Haiku is reserved for light Notion/doc recording. Escalate **model before packs**. Does not replace `docs/loading-map.md` Load Limits or the Model-Invariant Floor.

**When to load:** only when choosing/switching models by complexity, explaining L0–L3, or resolving an escalation dispute. Do **not** preload on L0–L1 cold-start.

## Tier Table

| Tier | Signals (examples) | Model default | Load |
|---|---|---|---|
| L0 Light docs | Notion notes/rows, short doc capture, trivial filing, simple checklist ticks | Haiku 4.5 | Kernel only (or Kernel + 1 allowlisted Notion/doc section) |
| L1 Default / routine | coding, summaries, Q&A, edits, most everyday asks — **default when unsure** | Sonnet 5 | **Model tier**; packs follow loading-map when mapped (`kernel_only_safe=false`); Kernel-light when unmapped |
| L2 Complex everyday | multi-step, multi-file, architecture review/lite, careful review | Opus 5 (1M) | Kernel + loading-map caps (existing Load Limits) |
| L3 Hardest / long-running | deep RCA / root cause / 근본 원인·원인 분석, large refactor / 대규모 리팩터, security audit / 보안 감사, multi-hour / 장기 작업, high-stakes | Fable 5.1 | Kernel + map caps; may use 1 workflow/reviewer only if risk needs it |

## Rules

1. **Classify first from the user ask** (object + risk), not from available files. **L0–L3 primarily select MODEL.**
2. **When unsure → Sonnet (L1), not Haiku.** Prefer Sonnet as the safe default for everyday work.
3. **Haiku only when the ask is clearly light Notion/doc recording** (narrow gate: notes, rows, short docs, trivial filings, simple checklist ticks; KO synonyms: 노션/메모/체크리스트) — not a general “anything quick” floor.
4. **Escalate model before expanding packs** (invariant floor).
5. **Never preload** `docs/model-usage.md`, README, CHANGELOG, PROGRESS, or SESSION_LOG on L0–L1.
6. **Pack selection follows `docs/loading-map.md` / `kernel_only_safe`.** L0 may use Kernel only, or Kernel + at most one allowlisted Notion/doc module (`modules/Meeting.md`). Mapped L1–L3 routes use loading-map Load Limits (Module 1 / Domain ≤2 / Workflow 1 / Reviewer 1 / Policies ≤3) — **never strip Integrity Policies** (Evidence/FileHandling/Freshness/ToolExecution) required by triggers just to “look light.” L3 may use one workflow or one reviewer only when risk requires it. Do not lower the floor too far — over-routing to Haiku is undesirable.

## Model-Invariant Floor vs Adaptive

- **Floor (invariant):** same Kernel, Integrity intent, Context Budget, and loading-map routing on every model. Model choice does not rewrite which Integrity Policies triggers require.
- **Adaptive (model + optional trim):** L0–L3 choose capacity (Haiku→Fable). Optional trim applies only to Preference packs / non-required extras — **never** to trigger Integrity Policies on mapped coding or similar.
- Taxonomy map: MetaRules Low≈L0 light docs; Low/Medium routine≈L1; Medium complex≈L2; High≈L3. Autoload simple≈kernel_only_safe; substantial≈mapped loading-map.

## Escalation Ladder

`Haiku (L0)` → `Sonnet (L1)` → `Opus (L2)` → `Fable (L3)`.

De-escalate when remaining work is routine. Model capacity goes to deeper reasoning within the same loaded set — not extra file dumps.


## Risk ↔ Effort Coupling

Meta-review (sim round-2) — intentional deviation from a blanket high-risk→L2 floor:

1. **High risk ⇒ ban L0 (Haiku); floor at L1 (Sonnet) minimum.**
2. **Do not** raise every high-risk ask to L2/Opus solely because `risk_level=high`.
3. Raise to **L2+ only when L2/L3 text signals** (multi-step / multi-file / architecture review / deep RCA / root cause / 근본 원인 / 대규모 리팩터 / 보안 감사 / …) are also present — `classify_tier` / `effective_tier` encode this.
4. `detect_task.py` emits `effort_tier`, `model`, and optional `effort_reason` when the risk floor or L0-leak guard changes the tier.

## Bilingual + spacing-tolerant signals

L0–L3 keyword lists pair English with Korean equivalents. Matching collapses whitespace/common separators so `근본원인`, `근본 원인`, and `코드수정`/`코드 수정` behave the same (`R2-P0-KO-TIER-BLIND`, `R2-P2-KO-SPACING`).

## L0 leak guard

Haiku (L0) is Notion/light filing only. If the selected route loads substantial Manual/coding/security packs, domains, workflows, reviewers, policies, or the ask is high-risk, `effective_tier` raises to **≥L1** (`R2-P2-L0-LEAK`).

## Relation to Other Docs

- Pack selection: `docs/loading-map.md`
- Model floor / roster notes: `docs/model-usage.md`
- Entry pointer: `CLAUDE.md` § Adaptive Effort
