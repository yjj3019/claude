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
