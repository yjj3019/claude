# FEF Loading Map

This file selects task-specific FEF packs. It is a routing table, not a new reasoning layer.

## Load Limits

Maximum load per task:

- Module: 1
- Domain: up to 2
- Workflow: 1
- Reviewer: 1
- Policies: up to 3

Simple low-risk questions may skip this map and use the Kernel only. A reviewer runs at most once per artifact. Do not review reviewer output. Do not add new permanent layers; add capabilities as files inside existing directories.

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
| Code change | `modules/Coding.md` | Relevant domain only when product-specific behavior matters | `workflows/CodingWorkflow.md` | Optional `reviewers/CodeChangeReviewer.md` for substantial or high-risk changes | `policies/FileHandling.md`; `policies/ToolExecution.md`; optional `policies/Evidence.md` |

## Selection Rules

1. Start with the user task, not the available files.
2. Load the smallest set that can produce an accurate, reviewable answer.
3. Prefer one domain. Add a second domain only when the task crosses a real product or platform boundary.
4. Use reviewers for external-facing artifacts, high-risk technical recommendations, substantial code changes, or user-requested review.
5. Skip workflows for short rewrites, definitions, and low-risk answers.
6. Never select more than one reviewer. Use a combined reviewer when a task requires multiple review dimensions.
7. If a required pack is missing, follow the missing-pack behavior in the repository `CLAUDE.md`; do not silently substitute another pack.
