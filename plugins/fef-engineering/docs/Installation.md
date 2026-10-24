# TaskForge for Claude — Installation

Formerly FEF, maintained by yjj3019. This is a display-name change; keep the
existing IDs and follow [naming compatibility](ClaudeCode.md#product-name-and-retained-identifiers).

For the native Claude Code plugin, use `fef-engineering@fef-marketplace` and the
[plugin migration guide](ClaudeCode.md#plugin-validation-and-compatibility).
The script-based `fef-claude/` installation below is a separate entry and retains
its existing directory and invocation name.

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

The installed `SKILL.md` declares only the common `name: fef-claude` and a narrow
description for explicit TaskForge for Claude or FEF requests. It emits no Claude Code extension fields;
manual-only invocation controls belong to the active host's configuration. A
description is not an enforced invocation restriction. The body keeps the
existing selective loading map and budget. These metadata checks do not prove
upload acceptance, live discovery or activation on any host.
See [Claude Code frontmatter](https://code.claude.com/docs/en/skills#frontmatter-reference)
and the [Agent Skills specification](https://agentskills.io/specification#frontmatter).
See also [frontmatter outside Claude Code](https://code.claude.com/docs/en/skills#using-skill-frontmatter-outside-claude-code): Code-specific fields are not portable to strict upload contracts.

## Claude Projects

1. Paste `CLAUDE.md` into Project Instructions (`python3 scripts/install_pack.py --print-claude`).
2. Upload selected modules/domains/workflows as Project Knowledge — not the entire tree.
3. Keep Context Budget and Model-Invariant Floor (`docs/model-usage.md`).

## Example prompt

"Use FEF Core Kernel + Proposal Module + RHEL Domain Pack."

## Delegation distribution is blocked

Native 2.0.0 omits `ai-delegation-loop`. Its standalone install and ZIP commands
refuse distribution, including force, dry-run and evidence variants, until rights
are cleared. Existing installations and read-only inspection are preserved.
Do not copy the source archive as a substitute for a blocked installer.
See [clearance evidence and restoration criteria](third-party-clearance.md).
For independently versioned owned skills, see [skill versions](skill-versions.md).

## Optional Git executable for verification

Verification hooks and the verification wrapper accept `FEF_GIT_EXECUTABLE`.
Unset or empty retains the existing `git` lookup through PATH, including custom
wrappers. There is no automatic replacement of the selected Git installation.
The setting affects Git used for repository/snapshot observation, including HEAD
and recursive submodules; it does not rewrite the verification child command.

Set it in the terminal before launching the host, using a trusted existing
absolute executable path. On Windows it must be an `.exe` file. Do not include
shell quotes, arguments or a `~` abbreviation in the value. For example, only
if this exact Git for Windows installation exists:

```powershell
$env:FEF_GIT_EXECUTABLE = 'C:\Program Files\Git\mingw64\bin\git.exe'
```

This is a process/child environment setting, not a global PATH change.
[Git for Windows documents direct absolute-path invocation](https://gitforwindows.org/git-wrapper.html).
Use a supported installation and check local helper/configuration compatibility;
this option does not promise a speedup on other systems. A wrong path or failed
Git command leaves verification unavailable, with no retry through another Git
and no inferred successful result. Existing snapshot format, timeout and
sanitized operation diagnostics remain unchanged. To return to default behavior
for subsequently launched hosts in this PowerShell session:

```powershell
Remove-Item Env:\FEF_GIT_EXECUTABLE -ErrorAction SilentlyContinue
```

An already running host retains its inherited environment. Changing the setting
does not migrate state or update an installed plugin; install the updated pack
before using the option. These instructions do not change global settings.

<a id="fef-replacement-and-recovery"></a>

## TaskForge for Claude replacement and recovery

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
