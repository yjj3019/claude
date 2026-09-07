# Installation

## URL-only (AI hosts)

From a fresh clone:

```bash
git clone https://github.com/yjj3019/claude.git
cd claude
python3 scripts/install_pack.py --auto
```

- `--auto` detects Claude Code, Codex, Grok, Cursor, and AGENTS-compatible skills roots and installs `fef-claude/` (**host skills only**).
- Sibling install is **opt-in**: `--siblings PATH`, `FEF_SIBLING_ROOTS`, `--siblings-only`, and/or `--scan-sibling-parent` (parent-dir scan default OFF).
- Existing `fef-claude/` is **preserved** unless `--force` (identical entry-file hash is skipped). Non-destructive = create skill dirs + preserve existing pack.
- `--print-bootstrap` — host/sibling one-liners (sibling remains opt-in).
- `--print-claude` prints exact steps to paste `CLAUDE.md` into Claude Project Instructions.
- `--check` verifies an install; with `--with-tests`, also runs `validate_framework.py`.
- Preferred Claude Code path remains: open the git clone as the workspace so root `CLAUDE.md` loads.

### Multi-repo (opt-in siblings)

```bash
python3 /path/to/claude/scripts/install_pack.py --auto
# → host skills only

python3 /path/to/claude/scripts/install_pack.py --siblings /other/project
# → <sibling>/.claude/skills/fef-claude (and/or .agents/skills)
```

## Claude Code

1. Clone or copy this repository and open it as the Claude Code workspace root (loads `CLAUDE.md`).
2. Or run `python3 scripts/install_pack.py --auto` and point the host at the installed `fef-claude/` pack.
3. Hooks under `.claude/settings.json` enforce test-before-stop when using this repo as workspace. They invoke `python`; on Linux/macOS change both commands to `python3`, otherwise the hooks fail open and enforcement is silently off (see `docs/ClaudeCode.md`).

## Claude Projects

1. Paste `CLAUDE.md` into Project Instructions (`python3 scripts/install_pack.py --print-claude`).
2. Upload selected modules/domains/workflows as Project Knowledge — not the entire tree.
3. Keep Context Budget and Model-Invariant Floor (`docs/model-usage.md`).

## Example prompt

"Use FEF Core Kernel + Proposal Module + RHEL Domain Pack."
