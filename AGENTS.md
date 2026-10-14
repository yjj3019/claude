# AGENTS.md

Read `CLAUDE.md` first; do not load a second copy of the inlined Kernel.

## Guidance Layout

- `kernel/` is the source; policies, modules, domains and reviewers are task-selected.
- `config/routes.json` / `scripts/detect_task.py` preview routes; `docs/loading-map.md` supports manual selection.
- Adaptive Effort preferences: `docs/adaptive-effort.md`, only when choosing models.
- Validate: `python scripts/validate_repository.py`; tests: `python -m unittest discover -s tests`.
- Install: `python scripts/install_pack.py --auto` copies host skills only; sibling install is opt-in and existing packs require `--force` to replace.

## Subagent Delegation Policy

Prefer native Claude Code subagents to keep the main context lean and control cost.

- File, symbol, call-site, and documentation exploration → delegate to **luna-explorer** (read-only, haiku).
- Tests, builds, lint, typecheck, and other verification commands → delegate to **luna-runner** (haiku). Do not let it modify source.
- Important architecture or implementation direction decisions → call **astra-reviewer** (opus, read-only) immediately before locking the decision.
- Same error unfixed after two attempts → call **astra-reviewer**.
- Design, implementation, complex debugging, integration, and final review remain with the main agent (Sol role).
- Pass only the conclusion + evidence (paths, line numbers, key findings) back to the main context. Do not flood it with raw search results or full logs.
- For critical facts, the main agent re-reads the original files.
- Parallelize only independent work; avoid concurrent edits to the same files.
- For exhaustive searches, state scope and residual omission risk.

Astra is advisory only; the main agent retains final authority.
Do not assume an external Advisor feature; use the official Agent tool / subagent mechanism.
