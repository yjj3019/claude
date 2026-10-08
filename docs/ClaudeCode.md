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
