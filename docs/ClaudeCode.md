# Claude Code Guide

Start Code in the target repository. Its native discovery loads project instructions;
a host skill copy does not replace the target project's CLAUDE.md.
FEF workflows are Markdown procedures, not executable .claude/workflows.

## Context and Execution

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
2. PostToolUse/PostToolUseFailure on Bash record a recognized verification result for that session and exact worktree snapshot. They never infer success from unknown exit metadata.
3. Stop asks once for verification when the worktree changed and no successful result matches its current snapshot. stop_hook_active prevents loops.

An already-dirty read-only session is allowed. New nested files, all Git-visible file types,
deletions, renames and commits are tracked. Ignored files are outside the reminder's coverage.
Git changes made by another process during the session are also observed; ownership is not inferred.
The old shared .test-run-marker is not trusted. Session records live in ignored .claude/.verification/.

For native Bash results that omit exit metadata, run the repository wrapper:

```bash
python scripts/run_verification.py -- python -m unittest discover -s tests
python scripts/run_verification.py -- python scripts/validate_repository.py
```

The wrapper invokes an argv without a shell, preserves stdout/stderr and the real exit code,
then emits a machine-readable footer tied to the argv and current snapshot. The recorder checks
the footer rather than inventing exit_code=0. Direct simple test commands are supported when
the host supplies an explicit integer exit code. Compound commands and pipelines cannot earn
success credit: their aggregate exit can hide failure.

These are reminders, not a sandbox or coverage proof. Unknown metadata, failure or an interrupted
run cannot verify a changed tree. Missing baseline/interpreter/Git, malformed state or hook errors
fail open with a diagnostic; disclose unavailable verification rather than claim a pass.
No automatic permissions, production changes or tool-output replacement is added.

Hook paths use CLAUDE_PROJECT_DIR and `python`. Check interpreter and native shell support in
your actual installation; use the environment-appropriate Python command when necessary.
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
