# Coding Module

Deliver the smallest complete, verified change in the assigned worktree.
Use `policies/FileHandling.md` and `policies/ToolExecution.md` for file and execution contracts.

## Workflow

1. Confirm target, scope and protected files; inspect implementation, callers, tests and conventions.
2. Reproduce or characterize the failure; choose the shared root cause and acceptance criteria.
3. Implement a narrow fix using existing APIs. Add meaningful regression tests for changed behavior; never weaken tests to hide failure.
4. Run targeted validation, then relevant lint/typecheck, broader tests or build. Preserve command, cwd, exit status and failure evidence.
5. Inspect actual diff for unrelated work, secrets and generated artifacts; report behavior, checks, failures and residual risk.

Use Plan Mode for nontrivial work and an optional CodeChangeReviewer for consequential changes.
No separate CodingWorkflow load is needed. Completion requires verified state, not merely a plan, edit or command invocation.
