# AGENTS.md

Read `CLAUDE.md` first; do not load a second copy of the inlined Kernel.

## Guidance Layout

- `kernel/` is canonical; select policies/modules/domains/reviewers per task.
- `config/routes.json` / `scripts/detect_task.py` preview routes; `docs/loading-map.md` supports manual selection.
- Model choice only: Adaptive Effort in `docs/adaptive-effort.md`.
- Validate: `python scripts/validate_repository.py`; tests: `python -m unittest discover -s tests`.
- Install: `python scripts/install_pack.py --auto`: host skills only; siblings opt-in; existing packs need `--force`.

## Subagent Delegation Policy

Use project reviewers and built-in Explore for context isolation.

- Broad exploration → built-in Explore; low volume → direct Read/Grep.
- Tests/lint/build → direct or short-lived Bash; summarize logs.
- Architecture and security reviews → `architecture-reviewer` / `security-reviewer` (opus).
- Code/technical review → `code-change-reviewer` / `technical-reviewer` (sonnet).
- Docs/prompt/consistency → corresponding reviewers (haiku/sonnet).
- Nontrivial coding-route changes: call `code-change-reviewer` once before delivery.
- Return conclusions and evidence only.
- Main agent owns decisions and implementation.

Reviewers use `omitClaudeMd: true` to avoid reloading Kernel/AGENTS.md.

TaskForge source: follow `docs/upstream-review-policy.md` if present.
