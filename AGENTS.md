# AGENTS.md

Read `CLAUDE.md` first; do not load a second copy of the inlined Kernel.

## Guidance Layout

- `kernel/` is the source; policies, modules, domains and reviewers are task-selected.
- `config/routes.json` / `scripts/detect_task.py` preview routes; `docs/loading-map.md` supports manual selection.
- Adaptive Effort preferences: `docs/adaptive-effort.md`, only when choosing models.
- Validate: `python scripts/validate_repository.py`; tests: `python -m unittest discover -s tests`.
- Install: `python scripts/install_pack.py --auto` copies host skills only; sibling install is opt-in and existing packs require `--force` to replace.
