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
- Existing `fef-claude/` is **preserved** unless `--force` (identical shipped-file fingerprint plus intact installation is skipped). Non-destructive = create skill dirs + preserve existing pack.
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
3. Hooks under `.claude/settings.json` remind you to test before stopping when using this repo as workspace. Their exec-form `command` is `python`; if that executable is unavailable, set all four interpreter fields to the available Python executable (often `python3` on Linux/macOS). Missing interpreters leave verification unavailable; see `docs/ClaudeCode.md`.

The installed `SKILL.md` declares `name: fef-claude` and a narrow description for
explicit FEF requests. Claude Code's `disable-model-invocation: true` makes this
skill a manual `/fef-claude` entry; other hosts must use their own invocation
controls. The body keeps the existing selective loading map and budget. These
metadata contracts do not establish live discovery or activation on every host.
See [Claude Code frontmatter](https://code.claude.com/docs/en/skills#frontmatter-reference)
and the [Agent Skills specification](https://agentskills.io/specification#frontmatter).

## Claude Projects

1. Paste `CLAUDE.md` into Project Instructions (`python3 scripts/install_pack.py --print-claude`).
2. Upload selected modules/domains/workflows as Project Knowledge — not the entire tree.
3. Keep Context Budget and Model-Invariant Floor (`docs/model-usage.md`).

## Example prompt

"Use FEF Core Kernel + Proposal Module + RHEL Domain Pack."

## Separate delegation skill

From this clone, `python scripts/install_pack.py --pack ai-delegation-loop --dest /path/to/skills` installs only delegation beside `fef-claude/`. `--dest` is the skills root, not an installed FEF directory. This explicit selection requires `--dest`; host/sibling discovery is not used. `--dry-run` writes nothing, differing installs are refused, and `--force` preserves a backup outside skill discovery. `--check` compares all installed bytes with the current canonical package.

For tool-specific user/project paths and reproducible ZIPs see [delegation installation](https://github.com/yjj3019/claude/blob/main/skills/ai-delegation-loop/installation.ko.md). The root FEF instructions are not replaced. See [provenance and licensing](https://github.com/yjj3019/claude/blob/main/docs/delegation-loop/INTEGRATION.md).

## FEF replacement and recovery

The FEF branch of this installer stages inside the selected skills root, hashes
the copied payload against its source snapshot and verifies the manifest before
changing an existing pack. Source/destination overlap, symlinks and Windows
junctions/reparse points are refused, including ancestors and shipped files.
Default refusal and no-write identical skip remain; `--dry-run` creates nothing.

An explicit `--force` replacement preserves **all** old contents, including user
files, at `<skills-root>/.fef-install-<unique>/old/`. The path is printed on stderr.
That nested backup is outside the direct `fef-claude/` skill entry; do not point a
host's discovery root inside it. Backups consume space and are not auto-deleted.
If copy/stage verification fails, the original stays in place. If publishing or
its verification fails, the installer tries to restore the old pack. If rollback
also fails, both available versions remain and the recovery path is reported.

Stop host use and concurrent installers before manual recovery. Inspect the
reported directory and its user files; `--check --dest <skills-root>` verifies an
active installation's manifest, not permission to discard edits. Preserve any
failed new `fef-claude/` separately before moving the reported `old/` back to that
name. Verify again and retain the backup until accepted. No automatic global
configuration changes or live host activation are performed. Renames handle
ordinary failures; this is not a transactional lock against hostile concurrent
filesystem modification or a guarantee against power-loss interruption.
