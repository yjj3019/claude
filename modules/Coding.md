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

## Long-Running Changes

- Split substantial work into bounded outcomes with acceptance criteria; keep the current stage and evidence in the project's existing progress record. Small changes need no phase files.
- Connect each completion claim to the requirement, actual command or inspected artifact, target worktree state, and observed result. A successful process exit alone does not prove the requested behavior occurred.
- After a fix, run the affected checks again; earlier evidence does not validate a changed artifact. Keep failed runs alongside later results, including flaky failures and skipped checks.
- Retry only after a changed hypothesis or implementation. After three failures with the same cause, stop repeating and report attempts, evidence, blocker and next diagnostic action; do not relax a check to obtain a pass.
- When independent verification is warranted and available, provide the criteria, actual diff and raw evidence. Separate review context can reduce shared assumptions but does not guarantee correctness. Keep the main agent responsible for the decision.
