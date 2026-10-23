---
name: fef-coding
description: Deliver the smallest complete verified code change. Use for code modifications, bug fixes, or feature implementation in a repository. Requires inspecting evidence, callers, tests, and conventions before editing.
---

# TaskForge for Claude — Coding (FEF Coding Skill)

Deliver the smallest complete, verified change in the assigned worktree.

## Workflow

1. Confirm target, scope and protected files; inspect implementation, callers, tests and conventions.
2. Reproduce or characterize the failure; choose the shared root cause and acceptance criteria.
3. Implement a narrow fix using existing APIs. Add meaningful regression tests for changed behavior; never weaken tests to hide failure.
4. Run targeted validation, then relevant lint/typecheck, broader tests or build. Preserve command, cwd, exit status and failure evidence.
5. Inspect actual diff for unrelated work, secrets and generated artifacts; report behavior, checks, failures and residual risk.

With native verification hooks, run approved checks through `python "${CLAUDE_PLUGIN_ROOT}/scripts/run_verification.py" -- <verification argv>` from the target project's cwd on the first attempt. The wrapper preserves output and exit status and emits the snapshot footer needed when the host omits exit-code metadata. If the wrapper is unavailable or prohibited, disclose the recording gap; do not infer success from text or repeat an unchanged check solely to silence the reminder.

Keep the final report self-contained: include the shared cause, sibling callers, patch and observed checks even after a hook reminder.

Use Plan Mode for nontrivial work. Completion requires verified state, not merely a plan, edit or command invocation.

For full domain packs, policies, or reviewers, consult `${CLAUDE_PLUGIN_ROOT}/docs/loading-map.md` or run `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect_task.py" --task "..."` when needed. Resolve returned pack paths against `${CLAUDE_PLUGIN_ROOT}`, not the working project. Prefer this skill for ordinary coding tasks.
