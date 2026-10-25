# Coding Module

Deliver the smallest complete, verified change in the assigned worktree.
Use `policies/FileHandling.md` and `policies/ToolExecution.md` for file and execution contracts.

## Change Discipline

- Implement only the current acceptance criteria. Reuse existing code; add features, options or abstractions only when the current task needs them. Preserve input validation and failure handling at trust boundaries.
- Before introducing custom code or a new dependency, compare existing project abstractions, standard-library/platform features, and installed dependencies, in that order. Preserve required behavior, compatibility, security and accessibility when choosing.
- Remove imports, variables or helpers made unused by your change. Leave pre-existing unrelated unused code in place and report it separately.

## Workflow

1. Confirm target, scope and protected files; inspect implementation, callers, tests and conventions.
2. Reproduce or characterize the failure; choose the shared root cause and acceptance criteria.
3. Implement a narrow fix using existing APIs. Add meaningful regression tests for changed behavior; never weaken tests to hide failure.
4. Run targeted validation, then relevant lint/typecheck, broader tests or build. Preserve command, cwd, exit status and failure evidence.
5. Inspect actual diff for unrelated work, secrets and generated artifacts; report behavior, checks, failures and residual risk.

For changes to guards, persistence or tool orchestration, exercise a relevant success and rejection or failure case through the connected path. Cover affected supported path/shell variants and interactions between defaults and explicit overrides. Mocked or simulated orchestration alone does not establish host or model behavior.

Before claiming verification, confirm the command exercised the intended behavior and inspect the final result summary. Report executed, failed and skipped counts when the tool provides them; zero tests, all-skipped runs or a successful setup command do not verify the acceptance criteria. Preserve the full log separately from an abbreviated report, without exposing secrets.

Use Plan Mode for nontrivial work and an optional CodeChangeReviewer for consequential changes.
No separate CodingWorkflow load is needed. Completion requires verified state, not merely a plan, edit or command invocation.

## Long-Running Changes

- Split substantial work into bounded outcomes with acceptance criteria; keep the current stage and evidence in the project's existing progress record. Small changes need no phase files.
- Connect each completion claim to the requirement, actual command or inspected artifact, target worktree state, and observed result. A successful process exit alone does not prove the requested behavior occurred.
- After a fix, run the affected checks again; earlier evidence does not validate a changed artifact. Keep failed runs alongside later results, including flaky failures and skipped checks.
- Retry only after a changed hypothesis or implementation. After three failures with the same cause, stop repeating and report attempts, evidence, blocker and next diagnostic action; do not relax a check to obtain a pass.
- When independent verification is warranted and available, provide the criteria, actual diff and raw evidence. Separate review context can reduce shared assumptions but does not guarantee correctness. Keep the main agent responsible for the decision.
