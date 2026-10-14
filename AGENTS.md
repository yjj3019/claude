# AGENTS.md

Read `CLAUDE.md` first; do not load a second copy of the inlined Kernel.

## Guidance Layout

- `kernel/` is the source; policies, modules, domains and reviewers are task-selected.
- `config/routes.json` / `scripts/detect_task.py` preview routes; `docs/loading-map.md` supports manual selection.
- Adaptive Effort preferences: `docs/adaptive-effort.md`, only when choosing models.
- Validate: `python scripts/validate_repository.py`; tests: `python -m unittest discover -s tests`.
- Install: `python scripts/install_pack.py --auto` copies host skills only; sibling install is opt-in and existing packs require `--force` to replace.

## Subagent Delegation Policy

Prefer existing FEF reviewers and built-in Explore for context isolation.

- Broad file/symbol exploration → built-in Explore or direct Read/Grep when volume is low.
- Verification commands (tests, lint, build) → run directly or via a short-lived Bash call; keep logs summarized.
- Architecture and security reviews → `architecture-reviewer` / `security-reviewer` (opus).
- Code-change and technical reviews → `code-change-reviewer` / `technical-reviewer` (sonnet).
- Documentation, prompt, and consistency checks → corresponding reviewers (haiku/sonnet).
- Pass only conclusions and evidence back to the main context.
- Main agent retains final judgment and implementation responsibility.
