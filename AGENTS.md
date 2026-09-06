# AGENTS.md

Lightweight entry for AGENTS-compatible hosts. **Read `CLAUDE.md` first** — it is the persistent runtime bootstrap (inlined Kernel, Autoload, Context Budget, Model-Invariant Floor, Adaptive Effort). Do not duplicate those contracts here.

## Guidance Layout

- `kernel/` — always-on reasoning behavior (also inlined in `CLAUDE.md`)
- `policies/` — trigger-loaded Evidence, FileHandling, ToolExecution, Freshness, …
- `modules/` `domains/` `reviewers/` `workflows/` — task packs via `docs/loading-map.md`
- `docs/adaptive-effort.md` — L0–L3 model tiers (detail; see `CLAUDE.md` Adaptive Effort)
- `docs/model-usage.md` — load only when choosing/switching models
- `scripts/validate_framework.py` / `install_pack.py` / `measure_load.py` / `detect_task.py`
- `tests/` — golden tests and unit tests

## Use Rule

When this repository is the working root, apply `CLAUDE.md` first and follow its routing. Do not load every file by default.

## Multi-repo

When this repository appears **with other git repos** (multi-root / siblings), run `python3 scripts/install_pack.py --auto` once before other work (or `python3 <this-repo>/scripts/install_pack.py --auto` if cwd is another repo). Details: README.
