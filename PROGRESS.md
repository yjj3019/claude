# Project Progress

## Recent (2026-10)

- **Context and harness optimization (2026-10-09)**: Compacted CLAUDE.md core to ~69 lines / 3.9kB. Integrated Coding/Research procedures into modules. Session-scoped verification hooks. Full details: `docs/precise-analysis-2026-10-09.md`.
- **Native Skills + Plugin packaging (2026-10-15)**: Added `.claude-plugin/` manifest and marketplace, plus `skills/fef-coding/` and `skills/fef-rca/` for on-demand native Skills. Plugin install path documented in README.
- **Repository cleanup (2026-10-15)**: Historical simulation, review, ablation, and source-history files moved to `docs/archive/`. Stub docs removed. Full prior progress log preserved in `docs/archive/PROGRESS-full.md`.

## Current Status

Core framework is stable. Prefer native Skills for ordinary coding/RCA tasks. Use `scripts/detect_task.py` or loading map for complex multi-pack routes. Verification hooks and golden tests remain active.

Open items from earlier rounds (S4-08 hook payload verification, valid pack-ablation re-run outside this repo) are recorded in the archived progress log.

Full historical entries (August–September 2026 rounds, ablation experiments, Fable deletion, routing priority changes, etc.) are in `docs/archive/PROGRESS-full.md`.
