# Claude Code Guide

Start Code in the target repository. Its native discovery loads project instructions;
a host skill copy does not replace the target project's CLAUDE.md.
TaskForge for Claude (formerly FEF) is maintained by yjj3019. It is independent
of Anthropic and is not an official, sponsored or endorsed Anthropic product.
Its workflows are Markdown procedures, not executable .claude/workflows.

<a id="product-name-and-retained-identifiers"></a>
## Product name and migration

**TaskForge for Claude**, formerly **FEF (Framework for Engineering Excellence)**,
uses the following native identities starting with plugin 3.0.0:

| Surface | Current contract |
|---|---|
| Native installation | `taskforge-for-claude@taskforge-marketplace` |
| Native skills | `/taskforge-for-claude:coding`, `/taskforge-for-claude:rca` |
| Reviewer namespace | `taskforge-for-claude:`; reviewer file names unchanged |
| Generated distribution | `plugins/taskforge-for-claude/` |
| Legacy standalone pack | `fef-claude/`, `name: fef-claude`, `/fef-claude` unchanged |
| Installer configuration | Existing options, `FEF_SIBLING_ROOTS`, `FEF_SIBLING_PARENT`, `.fef-manifest.json` unchanged |
| Verification | `.claude/.verification/`, state v1, `FEF_VERIFY_RESULT=` and failure markers unchanged |

This is a public native-interface change, not just a display-name update.
Former qualified calls are not aliases. Update saved prompts, automation,
permission rules and reviewer references using the migration section below.
The standalone installer remains separate to preserve installed data and callers.
Editing this clone does not update a user's installed cache or publish a release.

Naming review, 2026-10-23: public search surfaced a separate
[taskforge listing](https://claudecodemods.dev/mods/taskforge); uniqueness and
trademark permission are not established. See the
[Anthropic trademark guidelines](https://www.anthropic.com/legal/trademark-guidelines).
No Anthropic logo was added. Licensing scope and third-party exclusions are unchanged.

### Local validator advisories

Claude Code 2.1.310 accepts the current marketplace and generated plugin manifests
with exit 0, but warns that the approved `taskforge-for-claude` name may read as
an Anthropic-owned plugin. The independent-project disclaimer does not remove
that warning or establish trademark permission. The directory check also reports
a missing listing icon; no icon is added by this change. These are recorded
advisories, not a security review, directory approval or proof of installed behavior.

## Native Skills and Plugin

This repository now includes a Claude Code plugin manifest (`.claude-plugin/plugin.json`) and example native Skills under `skills/`:

- `skills/coding/SKILL.md` — ordinary code changes (smallest verified change).
- `skills/rca/SKILL.md` — evidence-based root-cause analysis.
- `skills/ai-delegation-loop/` is retained only in the source archive; it is not a distributable native skill while permission is unresolved.

To install as a plugin (recommended for reuse across projects):

```bash
/plugin marketplace add yjj3019/claude
/plugin install taskforge-for-claude@taskforge-marketplace
```

For a local native session, load only `--plugin-dir ./plugins/taskforge-for-claude`.
Do not load the source clone root as a distributable plugin: the preserved archive
under `skills/` can still be discovered there, and a manifest `skills` field adds
to the default scan rather than excluding other source folders. Native Skills are discovered by name + description and load their body on demand. Prefer them for matching tasks; fall back to `scripts/detect_task.py` or the loading map for complex multi-pack routes.

### Plugin validation and compatibility

Original FEF contributions have the scoped MIT grant in `LICENSE`.
DelegationLoop, external source material and historical records remain excluded;
redistribution clearance is unresolved. Package metadata does not claim a
whole-package license. Since 2.0.0 the native payload excludes the delegation skill.
Version 3.0.0 changes native identities; hooks, authorization and verification state v1 remain intact.

The append-only plugin rename history is:

```json
{"fef-claude": "fef-engineering", "fef-engineering": "taskforge-for-claude"}
```

The [official renames mechanism](https://code.claude.com/docs/en/plugins/host-marketplace#migrate-users-with-a-renames-map)
resolves plugin-name chains and can rewrite scoped `enabledPlugins` and
`pluginConfigs` keys. It does not establish automatic migration between different
marketplace registrations, skill calls or arbitrary plugin-owned data. Explicit
installation is required to populate a renamed Git/URL plugin cache. Managed
settings require an administrator update.

#### Preserve, verify in isolation, then cut over

1. Record every installed old copy's source, version and enabled scope, including
   aliases such as `fef-engineering@synced`. Preserve the applicable settings and
   an independently usable old payload. Back up any custom plugin-owned data
   without exposing credentials. Do not uninstall or delete registrations/caches
   as a migration shortcut; uninstall can remove saved data.
2. Check the new payload first in a separate, temporary Claude configuration and
   project. For uncommitted work use this clone's absolute local marketplace path;
   GitHub still serves the published revision. Check discovery and hook loading
   without sharing the active installation's settings, state or plugin data.
3. Register `taskforge-marketplace` in the intended scope, without installing
   the new plugin into the active configuration yet. If the host
   rejects registration because the same source is already registered, **stop**
   with the old registration/cache intact. Resolve that host-specific conflict
   before cutover; no cross-marketplace migration is assumed here.
4. After the isolated check, disable **all applicable old copies** and confirm
   their scopes before installing `taskforge-for-claude@taskforge-marketplace`
   into the active configuration: installation may enable it immediately. Do not
   run both hook sets in a normal project session. Review
   scoped `pluginConfigs`, permission rules, reviewer references and custom data
   individually; do not blindly copy old namespace keys or secrets.
5. Restart the session. Check the two new skills, reviewers and hooks, then perform
   a small relevant verification in a disposable project. Retain the old payload
   and settings for rollback; disable the new copy before re-enabling the old one.

| Former call | Current call |
|---|---|
| `/fef-engineering:fef-coding`, `/fef-claude:fef-coding` | `/taskforge-for-claude:coding` |
| `/fef-engineering:fef-rca`, `/fef-claude:fef-rca` | `/taskforge-for-claude:rca` |
| Old native `ai-delegation-loop` calls | Unavailable since 2.0.0 pending clearance |

Verification records stay in the consuming repository's `.claude/.verification/`,
keyed by session ID. The hooks do not use `CLAUDE_PLUGIN_DATA` or plugin-specific
user options. Host-managed cache and `${CLAUDE_PLUGIN_DATA}` paths depend on plugin
identity; this project does not migrate user data stored there. See
[plugin storage](https://code.claude.com/docs/en/plugins/manifest-reference#environment-variables).
Repository edits do not alter real user settings, credentials or installed data.

Historical observation only: the 2026-10-18 isolated Claude Code 2.1.302 fixture
verified the earlier single-marketplace `fef-claude` → `fef-engineering` rename
without model calls. That result does not prove the new marketplace transition,
current CLI behavior, old-command aliases or arbitrary data migration.

### Generated native distribution

The marketplace installs `plugins/taskforge-for-claude/`, generated from canonical
runtime files. The self-contained payload includes Skills, reviewer agents,
hooks, scripts, Kernel, packs and runtime docs; it excludes root `CLAUDE.md`,
marketplace metadata, local verification state and historical model evidence.
Delegation files are excluded. See [clearance](third-party-clearance.md) and
[skill versioning](skill-versions.md). Keep this generated directory in
the distributed repository; Git-based installation does not build it for users.

From the source clone, regenerate after changing runtime inputs:

```sh
python scripts/build_plugin.py
python scripts/build_plugin.py --check
claude plugin validate .claude-plugin/marketplace.json
claude plugin validate plugins/taskforge-for-claude
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
For local plugin development, use `claude --plugin-dir ./plugins/taskforge-for-claude`.
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
run cannot verify a changed tree. Once a recognized attempt loads its session state, the recorder
persists invalidation of any previous pass before collecting its snapshot or processing the result.
A later snapshot, result-processing or final-write error therefore leaves that attempt unverified.
State-write failures also leave a session-specific `.failed` marker beside the version-1 JSON.
Stop checks that marker before loading the baseline or accepting an earlier pass, and blocks once
with a storage-error reason even if the first baseline or invalidation write failed. A successful
state save clears the marker; resume with an existing baseline preserves it. Other sessions and
the JSON schema are unchanged. Clearing or recreating a missing baseline still establishes a new
baseline at that time; this does not prove verification of changes before that baseline.
Missing baseline/interpreter/Git, malformed state without a failure marker, or unrelated hook
errors still fail open with a diagnostic. Repository lookup failure or an unwritable marker can
prevent durable error reporting; the recorder cannot guarantee persistence when storage itself
is unavailable. State/marker recovery assumes sequential hooks, not concurrent atomic writers.
Git timeout diagnostics include only a fixed operation label (repository, status, head or index)
for exact known commands, never arguments, paths or exception text. These labels do not establish
the cause of an operating-system delay. Disclose unavailable verification rather than claim a pass.
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
