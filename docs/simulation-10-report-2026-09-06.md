# Simulation-10 Report (2026-09-06)

Structural/routing/load/install simulations on baseline `f98d14c` (main), fixes on branch `fix/sim-10-claude-optimize`.

**Method:** mechanical checks only (`detect_task.py`, `CLAUDE.md` / `loading-map` / `model-usage` presence, `sync_kernel.py --check`, `measure_load.py`, `install_pack.py --auto`, fence-aware `markdown_sections.parse_sections`, hooks/agents discovery). This is a **simulation rubric** for repository structure — not a host-model quality score. No invented behavioral /100 scores.

Timezone note: work recorded 2026-09-06 evening KST (UTC+9).

## Summary table

| ID | Scenario | Expected | Pre-fix | Post-fix | Issue IDs |
|---|---|---|---|---|---|
| SIM-01 | Simple Q&A / Sonnet default | Kernel only (`kernel_only_safe`); model=Sonnet L1 | PASS | PASS | — |
| SIM-02 | Everyday complex / Opus | Architecture (or similar) mapped packs | PASS | PASS | — |
| SIM-03 | Hardest long-running / Fable | Fable 5.1 notes + Model-Invariant Floor | FAIL | PASS | P0-NO-FABLE51-FLOOR |
| SIM-04 | Routine coding / Sonnet | Coding route packs | PASS | PASS | — |
| SIM-05 | CLAUDE.md autoload budget | Context Budget + Autoload; lean entry | PARTIAL | PASS | P1-NO-CONTEXT-BUDGET-ENTRY |
| SIM-06 | Skills/hooks discovery | `.claude/agents` + Stop/PostToolUse hooks | PASS | PASS | — |
| SIM-07 | Drift/sync | `sync_kernel.py --check` fails on mutate | PASS | PASS | — |
| SIM-08 | Full-doc load anti-pattern | Forbid full preload; measure_load dump ≫ route | PARTIAL | PASS | P1-NO-MEASURE-LOAD |
| SIM-09 | Install-from-URL only | `install_pack.py --auto` | FAIL | PASS | P0-NO-INSTALL-PACK |
| SIM-10 | Model routing invariant floor | Opus/Fable/Sonnet/Haiku floor in docs+AGENTS | FAIL | PASS | P0-NO-MODEL-FLOOR |
| SIM-10b | Fence-aware `##` parse | Fenced `##` ignored by helper | FAIL→helper | PASS | P1-NO-FENCE-HELPER |

Pre-fix tally (10 primary sims): **5 PASS, 2 PARTIAL, 3 FAIL**. Post-fix: **10/10 PASS** (+ fence helper PASS).

## Per-scenario notes

### SIM-01 Simple Q&A / Sonnet default — PASS
- `detect_task.py --task "what is Kubernetes?"` → `kernel_only_safe=true`, no module.
- Autoload: simple low-risk uses Kernel only; **Sonnet (L1) is the default when unsure**.

### SIM-02 Everyday complex / Opus — PASS
- OpenShift architecture review → `architecture_review` + Architecture module/workflow/reviewer.
- Opus 5 remains the advisory everyday-complex default.

### SIM-03 Hardest / Fable — FAIL→PASS
- Pre-fix: model-usage had only a Fable-class table row; no Fable 5.1 section; no Model-Invariant Floor.
- Post-fix: roster + floor + `### Claude Fable 5.1 Runtime Notes`; escalate ladder includes Fable.

### SIM-04 Routine coding / Sonnet — PASS
- Korean minimal-fix task → `coding` with Coding module/workflow + FileHandling/ToolExecution.

### SIM-05 CLAUDE.md budget — PARTIAL→PASS
- Entry was ~8KB with Autoload but lacked an explicit **Context Budget** section and model-floor pointer.
- Post-fix: `## Context Budget` + floor pointer; still under 20KB.

### SIM-06 Skills/hooks — PASS
- 8 generated agents under `.claude/agents/`; `settings.json` wires `record_test_run` + `verify_before_stop`.

### SIM-07 Sync drift — PASS
- Clean tree: `--check` exit 0. Mutating inlined Kernel body → exit 1 until restored/sync.

### SIM-08 Full-doc anti-pattern — PARTIAL→PASS
- Docs said “load only what required” but no mechanical dump comparison.
- `measure_load.py`: Kernel ~8.7KB; heaviest mapped route ~19KB; full-tree anti-pattern ~142KB (~7.6×).

### SIM-09 Install URL-only — FAIL→PASS
- Pre-fix: no `install_pack.py`; Installation.md was manual copy only.
- Post-fix: `--auto` installs `fef-claude/` with `CLAUDE.md` marker; unittest coverage added.

### SIM-10 Model floor — FAIL→PASS
- Pre-fix: role/effort notes without invariant floor or escalate≠expand at AGENTS entry.
- Post-fix: floor in `docs/model-usage.md`, `CLAUDE.md`, `AGENTS.md`; validate asserts phrases.

### SIM-10b Fence-aware parse — helper added
- FEF loads whole packs (not ChatGPT-style section Task Maps), but `validate_framework` now uses fence-aware H2 isolation for loading-map sections; unit test proves fenced `##` is ignored.

## Phase 2 — Problems derived

| Priority | ID | Defect |
|---|---|---|
| P0 | P0-NO-INSTALL-PACK | No URL-only `install_pack.py --auto` |
| P0 | P0-NO-MODEL-FLOOR | No Model-Invariant Floor / 4-model roster as operating rule |
| P0 | P0-NO-FABLE51-FLOOR | No Fable 5.1 runtime notes aligned to user roster |
| P1 | P1-NO-CONTEXT-BUDGET-ENTRY | CLAUDE/AGENTS lacked explicit Context Budget + escalate≠expand |
| P1 | P1-NO-MEASURE-LOAD | No mechanical Kernel vs route vs full-dump estimator |
| P1 | P1-NO-KO-README | No `README.ko.md` |
| P1 | P1-NO-FENCE-HELPER | No shared fence-aware `##` helper for validators |
| P2 | P2-SCORECARD-NO-SIM | Scorecard lacked simulation protocol |

## Phase 3 — Fixes implemented

1. `scripts/install_pack.py` (+ `tests/test_install_pack.py`) — `--auto` / `--print-claude` / `--check`
2. `docs/model-usage.md` — roster, Model-Invariant Floor, Fable 5.1 notes
3. `CLAUDE.md` / `AGENTS.md` — Context Budget + floor pointers
4. `scripts/measure_load.py`, `scripts/markdown_sections.py`
5. `validate_framework.py` — floor/install presence + fence-aware Task Map parse
6. Bilingual README + Installation/scripts README updates
7. Scorecard Simulation Protocol → this report

## Phase 4 — Validation (post-fix)

```text
python3 scripts/sync_kernel.py --check
python3 scripts/validate_framework.py
python3 scripts/validate_routes.py
python3 scripts/measure_load.py
python3 -m unittest discover -s tests -p "test_*.py"
```

Do not read the simulation table as model accuracy percentages.

## Errata (post-7abcc92 / Adaptive)

**SIM-01 narrative correction (F-06):** Early draft text called Haiku the “advisory fast path” for simple Q&A. After `7abcc92` (Revise Adaptive Effort: Sonnet default; Haiku for light Notion/docs) and the Adaptive router, **Sonnet is the default** for unsure/routine/Q&A. **Haiku is reserved for light Notion/doc recording only** (narrow gate). Kernel-only pack load for simple Q&A remains correct; only the model advisory changed.

See also: `docs/adaptive-effort.md`, `docs/precise-analysis-2026-09-06.md` (F-01–F-12).

