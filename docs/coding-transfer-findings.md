# Coding Transfer Findings

Date: 2026-07-10

This document summarizes coding-focused transfer tests that compare observable Fable5 coding behaviors against Opus/Sonnet + FEF runs.

The goal is not personality imitation. The goal is reproducible engineering behavior: root-cause fixes, minimal diffs, existing-code reuse, sibling caller scans, and verification discipline.

## Score Summary

| Test | Behavior Tested | Fable5 | Opus+FEF | Sonnet+FEF | Result |
|---|---|---:|---:|---:|---|
| GT012 | Shared root-cause fix | 100 / 0 | 100 / 0 | 98 / 2.45 | Opus parity; Sonnet near-parity with report completeness issue |
| GT013 | Existing helper reuse | 100 / 0 | 100 / 0 | 100 / 0 | Full parity; test saturated |
| GT014 | Boundary root-cause fix | 100 / 0 | 100 / 0 | 96 / 8 | Opus parity; Sonnet HOLD due to assigned-directory verification failure |

Scores are shown as average / standard deviation.

## Findings

### 1. Opus+FEF reached parity on the current coding tests

Across GT012, GT013, and GT014, Opus+FEF matched Fable5 average score and variance:

- same shared-root-cause fixes
- same minimal patch shapes
- no dependency additions
- no test tampering
- consistent sibling caller scans
- stable before/after verification reports

Current conclusion: for these small deterministic coding fixtures, Opus+FEF reproduces the measured Fable5 coding behavior.

### 2. Sonnet+FEF reasoning is near-parity; execution verification is the weak spot

Sonnet+FEF produced correct root causes and correct patch shapes in the tested fixtures.

Observed weakness:

- GT012: some runs completed the fix but did not submit complete self-reports.
- GT014: one run reported success from a redirected worktree copy while the assigned work directory still failed tests.

Current conclusion: Sonnet's issue in this sample is not code reasoning. It is run-state verification: the final report can describe the wrong filesystem target unless the prompt requires assigned-directory diff and test verification.

### 3. GT012 and GT013 are saturated

GT012 and GT013 no longer separate Fable5, Opus+FEF, and Sonnet+FEF meaningfully.

Keep them as regression tests, not as high-discrimination benchmarks.

### 4. GT014 exposed a useful process failure

GT014 produced the first non-perfect Sonnet result. The failure was valuable because it measured an operational behavior that code-only tests miss:

- Did the patch land in the literal target directory?
- Did the final verification run against the graded artifact?
- Did self-report match the actual filesystem state?

The GT014 FEF prompt and runner protocol were tightened after this finding.

## Candidate Pattern

### Assigned Directory Verification

Trigger:
- coding tasks that use copied fixtures, scratch directories, git worktrees, or tool-managed editing environments

Minimal rule:
- Before reporting success, verify the diff and test command from the literal assigned work directory.

Evidence:
- GT014 Sonnet+FEF run F3: correct patch landed in a redirected worktree, while the assigned directory still failed tests.

Current status:
- Candidate. Added to GT014 prompt/protocol only.
- Do not promote globally until the same failure appears in another coding test or real coding task.

## Do Not Promote Yet

Do not create a broad Coding module yet.

Reasons:

- Existing coding harness already covers much of the behavior.
- GT012 and GT013 are saturated.
- GT014 found a process-specific issue, not a broad reasoning defect.
- Adding generic rules now risks prompt bloat and duplicated truth.

## Recommended Next Test

If another coding benchmark is needed, prefer GT015 with higher discrimination:

Name:
- GT015: Coding Contract Preservation

Shape:
- A small codebase where the obvious patch makes new tests pass but breaks an existing documented behavior.
- The fixture should include an existing test or README contract that must remain true.
- Score whether the model preserves both the bug fix and the prior contract.

Target behaviors:

- reads existing tests/docs before patching
- avoids overfitting to the new failing case
- preserves backward-compatible behavior
- verifies full test suite, not only the new failure
- avoids broad rewrites

Do not create GT015 until there is a concrete need to distinguish models further.
