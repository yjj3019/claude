# Claude Code Guide

Start Code in the target repository. Its native discovery loads project instructions;
a host skill copy does not replace the target project's CLAUDE.md.
FEF workflows are Markdown procedures, not executable .claude/workflows.

## Native Skills and Plugin

This repository now includes a Claude Code plugin manifest (`.claude-plugin/plugin.json`) and example native Skills under `skills/`:

- `skills/fef-coding/SKILL.md` — ordinary code changes (smallest verified change).
- `skills/fef-rca/SKILL.md` — evidence-based root-cause analysis.
- `skills/ai-delegation-loop/` — existing independent skill.

To install as a plugin (recommended for reuse across projects):

```bash
/plugin marketplace add yjj3019/claude
/plugin install fef-engineering@fef-marketplace
```

Or load locally with `--plugin-dir`. Native Skills are discovered by name + description and load their body on demand. Prefer them for matching tasks; fall back to `scripts/detect_task.py` or the loading map for complex multi-pack routes.

### Plugin validation and compatibility

Licensing and redistribution permission remain unresolved. The source `LICENSE`
is incomplete, and the integrated DelegationLoop source has no license grant.
Plugin and marketplace metadata therefore omit a license identifier; this does
not grant new rights or resolve those permissions. See the source repository's
[attribution and license record](https://github.com/yjj3019/claude/blob/main/docs/delegation-loop/INTEGRATION.md#attribution-and-license).

The root plugin manifest is the single version source; the generated manifest is
an exact copy and the marketplace omits its redundant version. Version `1.3.1`
marks the separate native payload so cached `1.3.0` installs can receive the change
after release. See [manifest precedence](https://code.claude.com/docs/en/plugins-reference#metadata-precedence).

The native plugin is now `fef-engineering`, in both manifests. The marketplace
keeps `"renames": {"fef-claude": "fef-engineering"}` as append-only migration
history. The standalone installer still ships `fef-claude/` and `/fef-claude`.

After this change is released, existing native-plugin users should update the
marketplace, install the new ID once, and restart their session:

```text
/plugin marketplace update fef-marketplace
/plugin install fef-engineering@fef-marketplace
```

For testing uncommitted changes, add this clone's absolute local path as the
marketplace in an isolated Claude configuration; GitHub still serves the published
revision. Do not install both names as separate plugins to emulate an alias.
The [official migration procedure](https://code.claude.com/docs/en/plugins/host-marketplace#migrate-users-with-a-renames-map)
describes host migration of `enabledPlugins` and `pluginConfigs` in user, project
and local settings; managed settings require an administrator update. Git/URL
marketplaces require the explicit install above to populate the new cache.

Native skill names change as follows; update saved prompts and automation calls.
The rename map migrates plugin identity, not documented slash-command aliases:

| Former call | Current call |
|---|---|
| `/fef-claude:fef-coding` | `/fef-engineering:fef-coding` |
| `/fef-claude:fef-rca` | `/fef-engineering:fef-rca` |
| `/fef-claude:ai-delegation-loop` | `/fef-engineering:ai-delegation-loop` |

Plugin reviewer identifiers likewise use the `fef-engineering:` prefix. Skill
frontmatter names, reviewer file names and the separate standalone pack stay
unchanged. Old fully qualified plugin calls are not promised to resolve.

FEF verification state stays in the consuming repository's `.claude/.verification/`,
keyed by session ID. The hooks do not use `CLAUDE_PLUGIN_DATA` or plugin-specific
user options. A rename/resume regression test checks existing verification records
and confirms that a subsequent edit still requires new verification.
Host-managed cache and `${CLAUDE_PLUGIN_DATA}` paths depend on plugin identity;
FEF does not migrate custom data placed there by users. Preserve any such data
before migration and check it separately. Do not uninstall the old plugin as a
cleanup step: uninstall can delete its saved data. See
[plugin storage](https://code.claude.com/docs/en/plugins/manifest-reference#environment-variables).
No real user settings, credentials or saved data are changed by this repository edit.

On 2026-10-18, a local-marketplace fixture under an isolated `CLAUDE_CONFIG_DIR`
was tested with Claude Code 2.1.302, without model calls. Installing the old ID,
updating the renamed catalog and installing the new ID left only the new installed
ID and migrated both settings keys. A marker in the old data directory survived;
no new data directory was created by those commands. This checks that CLI path,
not arbitrary data migration, older clients or old slash-command alias resolution.

### Generated native distribution

The marketplace installs `plugins/fef-engineering/`, generated from canonical
runtime files. The self-contained payload includes Skills, reviewer agents,
hooks, scripts, Kernel, packs and runtime docs; it excludes root `CLAUDE.md`,
marketplace metadata, local verification state and historical model evidence.
Delegation acceptance guidance remains included. Keep this generated directory in
the distributed repository; Git-based installation does not build it for users.

From the source clone, regenerate after changing runtime inputs:

```sh
python scripts/build_plugin.py
python scripts/build_plugin.py --check
claude plugin validate .claude-plugin/marketplace.json
claude plugin validate plugins/fef-engineering
```

The check compares the exact managed file set and bytes without writing. It also
checks local Markdown file links; it does not fetch external links or validate all
anchor spellings. Extra output files cause a rebuild to stop for manual review,
including stale files from a removed input; they are never silently deleted.
Source and output links/junctions are refused using the existing installer guards.
This is not a security boundary against concurrent malicious filesystem changes.
Changed files are replaced individually; an interrupted build must pass `--check`
before release. Source-maintenance scripts are not part of the runtime payload.

Repository validation and CI check generated-file drift. Test the payload alone,
outside the clone, to ensure routing and hooks cannot fall back to source files.
For local plugin development, use `claude --plugin-dir ./plugins/fef-engineering`.
The existing `claude --plugin-dir .`, root manifest, clone `CLAUDE.md` and standalone
`fef-claude/` remain available. The plugin ID, skill namespaces and plugin data ID
do not change when the marketplace source moves. Installation paths do change;
runtime scripts derive them from their own location.

Consequently, `claude plugin validate .` still reports the intentional clone-root
`CLAUDE.md` advisory. The explicit marketplace/payload commands above validate the
distribution without that advisory, rather than suppressing messages. Root framework
validation remains in place. The plugin's SessionStart hook supplies the Kernel
and paths; live paid-session wiring remains unverified. See
[SessionStart context](https://code.claude.com/docs/en/hooks#sessionstart).
Do not treat plugin validation as security certification.

If repository validation reports a missing release tag in a shallow clone, first
check `git ls-remote --tags origin refs/tags/v1.2.0`. Fetch the existing tag with
`git fetch --no-tags origin refs/tags/v1.2.0:refs/tags/v1.2.0`; do not create a tag
on the current commit just to satisfy the check. CI already requests tags through
`actions/checkout`'s `fetch-tags: true`. The unreleased plugin version is separate
from the last tagged changelog release.

## Context and Execution

For official Mods capabilities versus custom masking, routing and escalation designs,
see [Mods and tiered agents](mods-and-tiered-agents.md). FEF's settings hooks are not
Mods; this repository does not install a three-tier tool-output filter or automatic
model escalation runtime. Mod evaluation scores are local decision aids, not official
benchmarks or measured savings.

- Keep the inlined core in CLAUDE.md. Preview routes with `python scripts/detect_task.py --task "..."`; read the loading map only for manual selection or clarification.
- Coding and Research modules contain their procedure. Do not load the compatibility workflow as a second copy. Select product domains and consequential reviewers only when needed.
- `@import` splits files but loads their content; it is not deferred loading. Native skill bodies/references can be loaded on demand, but registration and invocation still cost context.
- Use `/context` to inspect current occupancy and `/usage` for available cumulative attribution/limits. Estimates are not invoices; cache reduces billed input without removing context.
- Use `/clear` for unrelated tasks and focused `/compact` for a continuing long task. Preserve decisions, paths, actual verification, limits and next action. There is no universal 50–60% or 95% target.
- `/rewind` cannot guarantee rollback of Bash, DB or external actions. Inspect actual state after recovery.
- Plan Mode is useful for nontrivial tasks, not every local edit. Native Advisor and teams are optional; compare a single model's supported effort first. Do not install a deprecated advisor plugin by default.
- For large independent investigations, compare subagent isolation against startup/aggregation cost. Avoid automatic teams, repeated votes and always-on LLM hooks without measured benefit.

See [native context](https://code.claude.com/docs/en/context-window),
[caching](https://code.claude.com/docs/en/prompt-caching),
[costs](https://code.claude.com/docs/en/costs) and
[checkpoint limits](https://code.claude.com/docs/en/checkpointing#limitations).

## Reviewer Subagents

Reviewer source files are in reviewers/. Run `python scripts/generate_agents.py` after edits
to synchronize .claude/agents/. These native Code agents do not become Projects agents.
Use one focused review when consequential risk or the user requires it.

These generated reviewers have only `Read, Grep, Glob`, `model: opus` and
`maxTurns: 15`. The caller supplies scope, acceptance criteria, relevant diff/file
paths and actual verification evidence (command, cwd, exit status and useful
failure output). A regular non-fork subagent does not inherit the parent's
conversation or already-read files. Reviewers cannot run Git or tests; missing
evidence belongs in Validation Gaps, not an assumed PASS. The parent applies
accepted fixes and verifies them without automatically spawning another review.
The fixed model is retained; no cheaper-model quality or latency gain is measured.

## Optional Native Execution Shapes

Reviewed against the linked official pages on 2026-10-09. Load this section only
when choosing an execution shape. Check the actual Code version, provider,
available tools and permissions first; these are host features, not FEF runtimes
or Claude Projects features. Native execution was not tested in a paid session.

| Shape | Choose when | Boundary |
|---|---|---|
| Main session | Small, sequential or tightly coupled work | Avoid delegation startup and aggregation overhead |
| [Subagent](https://code.claude.com/docs/ko/sub-agents) | One request has a self-contained subtask returning a compact result | Separate context is not a filesystem sandbox; pass required evidence explicitly |
| [Agent view](https://code.claude.com/docs/ko/agent-view) | A user manages several independent full local sessions | Research preview; each session consumes usage |
| [Agent team](https://code.claude.com/docs/ko/agent-teams) | Peers need direct discussion and coordination | Experimental, off by default; use only when ordinary delegation is insufficient |
| [Dynamic workflow](https://code.claude.com/docs/ko/workflows) | Large repeated work needs script-controlled fan-out | Executable JavaScript via `Workflow` and `/workflows`, separate from FEF Markdown procedures |

- Subagents can nest and use `SendMessage` when their tools/version permit;
  FEF reviewers' allowlist includes neither `Agent` nor `SendMessage`. Do not add
  `memory` (can enable Write/Edit) or `skills` (full preload) to make them lighter.
- Enabling `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` can turn named `Agent`
  calls into teammates in interactive sessions, even without an explicit team
  request. `-p`/SDK sessions do not create teammates. A reused definition's
  `tools` allowlist is retained, but in-process teammates gain `SendMessage` and,
  where available, `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`. This changes
  the reviewer's execution shape. Keep teams off for the normal reviewer path.
  `/resume` and `/rewind` do not restore in-process teammates. Runtime team files
  are host-managed; `.claude/teams/teams.json` is not supported configuration.
- New Agent view dispatch can use its own worktree; moving an existing session
  with `/bg` retains its working location. Confirm actual cwd, changed files and
  permissions before action. Commit/push hints are not user authorization; preserve
  work before deleting a session/worktree. `permissionMode` is not an independent
  security boundary, and worktree isolation does not authorize external effects.
- Dynamic workflows support CLI/Desktop/IDE and `-p`/SDK, subject to the account,
  provider, configuration and invocation/permission rules; Pro needs opt-in.
  They may reduce main-context load, not necessarily total tokens.
  A missing/failed fan-out result can be `null`: account for it rather than filtering
  it into apparent complete success. Restart/retry can repeat completed work while
  retaining earlier file edits; inspect state and duplicate side effects first.
  Separate stages needing fresh approval. FEF ships no executable workflow here.

Use the smallest adequate shape and measure accepted results, retries, total
usage and latency before increasing concurrency. No automatic team activation,
permission bypass, global settings changes or paid benchmark is added by this guide.

## Session Verification Reminder

The hooks in .claude/settings.json are deterministic local commands, with no model calls:

1. SessionStart captures Git HEAD and dirty-file content hashes as the baseline for this session. Resume/compact preserve it; clear establishes a new baseline.
2. PostToolUse/PostToolUseFailure on Bash or PowerShell record a recognized verification result for that session and exact worktree snapshot. They never infer success from unknown exit metadata.
3. Stop asks once for verification when the worktree changed and no successful result matches its current snapshot. stop_hook_active prevents loops.

An already-dirty read-only session is allowed. New nested files, all Git-visible file types,
deletions, renames and commits are tracked. Ignored files are outside the reminder's coverage.
Git changes made by another process during the session are also observed; ownership is not inferred.
The old shared .test-run-marker is not trusted. Session records live in ignored .claude/.verification/.

For native shell results that omit exit metadata, run the repository wrapper:

```bash
python scripts/run_verification.py -- python -m unittest discover -s tests
python scripts/run_verification.py -- python scripts/validate_repository.py
```

The wrapper invokes an argv without a shell, preserves stdout/stderr and the real exit code,
then emits a machine-readable footer tied to the argv and current snapshot. The recorder checks
the footer rather than inventing exit_code=0. Direct simple test commands are supported when
the host supplies an explicit integer exit code. Compound commands and pipelines cannot earn
success credit: their aggregate exit can hide failure.

PowerShell accepts only simple literal arguments (including quoted paths with
spaces and literal Windows backslashes). Interpolation, escapes, expressions,
comments, compound commands and other syntax remain unverified; no POSIX shell
interpretation is used for PowerShell arguments. Wrapper footer, argv and both
snapshot hashes must still match. A later edit invalidates the record.

These are reminders, not a sandbox or coverage proof. Unknown metadata, failure or an interrupted
run cannot verify a changed tree. Missing baseline/interpreter/Git, malformed state or hook errors
fail open with a diagnostic; disclose unavailable verification rather than claim a pass.
No automatic permissions, production changes or tool-output replacement is added.

The four hooks use exec-form `command: python` and `args` with the documented
`${CLAUDE_PROJECT_DIR}` placeholder, avoiding shell-dependent variable expansion
and path quoting. Check that your Claude Code version supports this current
[exec-form contract](https://code.claude.com/docs/en/hooks#exec-form-and-shell-form)
and the [PowerShell tool](https://code.claude.com/docs/en/hooks#windows-powershell-tool).
The reference does not specify an introduction version for exec form; older host
compatibility is unverified. Use an available Python executable for all four
command fields when necessary; no interpreter or host settings are installed.
Session-state writes are atomic, but concurrent external edits and native wiring require
live validation. Tests cover supplied JSON contracts and real subprocesses, not a paid Claude session.
See [hook input contracts](https://code.claude.com/docs/en/hooks).

## Output and Handoff

Search paths/symbols and relevant failure regions before reading entire files/logs.
Keep command, cwd, actual exit/failure count and useful traceback. Preserve approved raw evidence;
never turn no output or a successful filter into a test pass.
Native updatedToolOutput requires the documented response shape; plain filter stdout is not a replacement.

Create a handoff only for long/multiple-session work. Include goal, repo/HEAD, changed paths,
checks/results, limits and next action; explicitly ask the next session to read it.
The filename .claude/session-handoff.md is a convention, not automatic loading.
