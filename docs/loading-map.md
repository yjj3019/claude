# FEF Loading Map

This file selects task-specific FEF packs. It is a routing table, not a new reasoning layer.

Here, `workflows/` means Markdown task procedures loaded as prompts, not executable Claude Code `.claude/workflows/` dynamic workflows.

## Load Limits

Maximum load per task:

- Module: 1
- Domain: up to 2
- Workflow: 1
- Reviewer: 1
- Policies: up to 3

Simple low-risk questions may skip this map and use the Kernel only. Select at most one Reviewer file per artifact. Run it at most once, only after a draft exists. Do not pass Reviewer output or the revised artifact through another Reviewer. Do not add new permanent layers; add capabilities as files inside existing directories.

## Task Map

| Task Type | Module | Domain | Workflow | Reviewer | Policies |
|---|---|---|---|---|---|
| RHEL proposal | `modules/Proposal.md` | `domains/RHEL.md`; optional `domains/EnterpriseArchitecture.md` | `workflows/ProposalWorkflow.md` | `reviewers/ProposalReviewer.md` | `policies/Writing.md`; `policies/Evidence.md`; `policies/Review.md` |
| Proposal consistency check | `modules/Proposal.md` | Relevant domain only | `workflows/ProposalWorkflow.md` | `reviewers/ProposalConsistencyReviewer.md` | `policies/Writing.md`; `policies/Evidence.md`; `policies/Review.md` |
| RHEL operations manual | `modules/Manual.md` | `domains/RHEL.md`; optional `domains/Linux.md` | `workflows/ManualWorkflow.md` | `reviewers/DocumentationReviewer.md` | `policies/Writing.md`; `policies/Evidence.md`; `policies/Review.md` |
| Linux/RHEL RCA | `modules/RCA.md` | `domains/RHEL.md`; optional `domains/Linux.md` | `workflows/RCAWorkflow.md` | `reviewers/TechnicalReviewer.md` | `policies/Evidence.md`; `policies/Thinking.md`; `policies/Review.md` |
| OpenShift architecture review | `modules/Architecture.md` | `domains/OpenShift.md`; optional `domains/Kubernetes.md` | `workflows/ArchitectureWorkflow.md` | `reviewers/ArchitectureReviewer.md` | `policies/Thinking.md`; `policies/Evidence.md`; `policies/Review.md` |
| Technical research brief | `modules/Research.md` | Relevant domain only | `workflows/ResearchWorkflow.md` | Optional; use only for external deliverables | `policies/Evidence.md`; `policies/Freshness.md`; optional `policies/Calibration.md` |
| Technical blog post | `modules/Blog.md` | Relevant domain only | Optional `workflows/ResearchWorkflow.md` for source-heavy posts | Optional `reviewers/TechnicalReviewer.md` for technical claims | `policies/Writing.md`; `policies/Evidence.md`; optional `policies/Freshness.md` |
| Prompt review | `modules/PromptEngineering.md` | None | `workflows/PromptWorkflow.md` | `reviewers/PromptReviewer.md` | `policies/Thinking.md`; `policies/Review.md`; optional `policies/Evidence.md` |
| Code modification | `modules/Coding.md` | Relevant domain only when product-specific behavior matters | `workflows/CodingWorkflow.md` | Optional `reviewers/CodeChangeReviewer.md` for substantial or high-risk changes | `policies/FileHandling.md`; `policies/ToolExecution.md`; optional `policies/Freshness.md` |
| File-backed technical analysis (manual-selection only; no keyword route) | `modules/Research.md` | Relevant domain only | None | Optional `reviewers/TechnicalReviewer.md` for high-risk deliverables | `policies/FileHandling.md`; `policies/Evidence.md`; optional `policies/Review.md` |
| Current-version research | `modules/Research.md` | Relevant domain only | `workflows/ResearchWorkflow.md` | Optional; use only for external deliverables | `policies/Evidence.md`; `policies/Freshness.md`; `policies/Calibration.md` |

## Selection Rules

1. Start with the user task, not the available files.
2. Load the smallest set that can produce an accurate, reviewable answer.
3. Prefer one domain. Add a second domain only when the task crosses a real product or platform boundary.
4. Use reviewers for external-facing artifacts, high-risk technical recommendations, substantial code changes, or user-requested review.
5. Skip workflows for short rewrites, definitions, and low-risk answers.
6. Never select more than one reviewer. Use a combined reviewer when a task requires multiple review dimensions.
7. If a required pack is missing, follow the missing-pack behavior in the repository `CLAUDE.md`; do not silently substitute another pack.
8. For proposal work, select `ProposalReviewer` for general proposal quality, `TechnicalReviewer` when technical claims are the primary review target, or the combined `ProposalConsistencyReviewer` for the mapped consistency-check task. Never load two of them for one artifact.

## Policy Classes

- Integrity Policies: Evidence, FileHandling, Freshness, ToolExecution, and selected safety or security rules. These preserve truthful evidence, execution, and risk boundaries.
- Preference Policies: Writing, Review, Calibration, Thinking, and Decision. Explicit user output constraints override these defaults.

## Policy Selection Rules

Load no policy by default unless the task trigger requires it.

| Trigger | Required policy |
|---|---|
| External factual or technical claims | `policies/Evidence.md` |
| Current, version-sensitive, lifecycle, CVE, support, subscription, or policy claims | `policies/Freshness.md` |
| Reading, modifying, comparing, generating, or validating files | `policies/FileHandling.md` |
| Executing commands, tests, builds, deployments, or tool actions | `policies/ToolExecution.md` |
| High-impact deliverable requiring a formal review pass | `policies/Review.md` |

Maximum policies per task: 3. When more than three triggers apply:

1. Preserve policies tied to observable execution risk.
2. Prefer a selected Workflow or Reviewer for task-specific checks.
3. Do not load a policy whose rules are already fully enforced by the selected Workflow or Reviewer.
4. Do not create wrapper policies merely to bypass the policy limit.
