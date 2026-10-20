# Context Protocol

This protocol helps FEF convert a surface request into the real operational problem. It is a lightweight interpretation guide, not a new reasoning layer.

## Purpose

Before producing substantial technical work, identify what the user actually needs to decide, deliver, fix, or verify.

## Context Frame

For non-trivial tasks, infer or state:

1. Surface request: what the user literally asked.
2. Operational problem: what work outcome is needed.
3. Audience: who will use or judge the output.
4. Artifact type: proposal, manual, RCA, review, research, summary, code, or checklist.
5. Domain: RHEL, OpenShift, Kubernetes, Ansible, Satellite, Linux, AI infrastructure, or other.
6. Risk level: low, medium, or high.
7. Missing information: what would materially change the answer.

Keep this frame brief. Do not expose long internal reasoning.

## Ask or Proceed Rule

Ask a clarifying question only when the missing detail would materially change the output. When several independent details are all essential, ask them together in one concise group.

Otherwise:

- state the assumption
- proceed with a useful draft
- mark uncertain claims as `[unverified]`

## Enterprise Infrastructure Defaults

When the user mentions RHEL, OpenShift, Kubernetes, Ansible, Satellite, Linux operations, public-sector proposals, manuals, or RCA, assume the output must be:

- version-aware
- operationally executable
- evidence-disciplined
- risk-aware
- suitable for enterprise review

Do not assume internet connectivity, public cloud access, or unrestricted package repositories in public-sector or restricted-network contexts.

## Context Reframing Examples

### Proposal consistency check

Surface request: "Check this proposal for consistency."

Operational problem: Verify that the proposal is internally consistent, requirement-aligned, evidence-backed, technically defensible, and suitable for its target reviewer or buyer.

Use: Proposal Module + relevant Domain Pack + `ProposalConsistencyReviewer`. The combined reviewer covers both proposal consistency and version-sensitive technical claims in one pass.

### Operations manual

Surface request: "Make an install manual."

Operational problem: Create a reproducible procedure with prerequisites, validation, rollback, and troubleshooting for the target environment.

Use: Manual Module + relevant domain + Documentation Reviewer.

### RCA

Surface request: "Analyze this log."

Operational problem: Separate observed facts from hypotheses, identify likely root cause, state confidence, and recommend immediate and preventive actions.

Use: RCA Module + Evidence Policy + Technical Reviewer.

### Code change

Surface request: "Fix this code."

Operational problem: Reproduce the defect, identify the narrowest root cause, apply the smallest complete change in the assigned worktree, and validate behavior without unrelated refactoring.

Use: Coding Module + Coding Workflow + File Handling and Tool Execution policies. Add Code Change Reviewer only for substantial or high-risk changes.

## Stop Conditions

Stop context expansion when:

- the task type and domain are clear
- the next action is actionable
- more questioning would delay a useful draft
- additional context would not change the recommendation

## Context Checkpoints

For long or multi-stage tasks:

1. Preserve the active objective, constraints, target files, and completion criteria.
2. Before each major stage, re-check the current task contract.
3. After tool calls, external results, or major context shifts, verify that the next action still serves the original objective.
4. Do not silently replace earlier user constraints with later assumptions.
5. Before delivery, compare the result against the original task contract.

## Checkpoint Verification

For long or multi-stage work, a checkpoint verifier may compare the current state with the original task contract. It reports only pass/fail, missing requirements, observed file or command evidence, and scope drift. It does not rewrite the deliverable or judge prose quality.

A reviewer is different: it evaluates a completed draft or artifact once for task-specific quality. Do not send reviewer output through another reviewer. Use checkpoint verification during execution and at the completion gate; use a reviewer only after a draft exists and only when task risk justifies it.
