# FEF Loading Map

This file selects task-specific FEF packs. It is a routing table, not a new reasoning layer.

## Load Limits

Maximum load per task:

- Module: 1
- Domain: up to 2
- Workflow: 1
- Reviewer: 1
- Policies: up to 3

Simple low-risk questions may skip this map and use the Kernel only.
Reviewer runs at most once per artifact. Do not review reviewer output.
Do not add new permanent layers; add new capability as files inside existing directories.

## Task Map

| Task Type | Module | Domain | Workflow | Reviewer | Policies |
|---|---|---|---|---|---|
| RHEL proposal | `modules/Proposal.md` | `domains/RHEL.md`; optional `domains/EnterpriseArchitecture.md` | `workflows/ProposalWorkflow.md` | `reviewers/ProposalReviewer.md` | `policies/Writing.md`; `policies/Evidence.md`; `policies/Review.md` |
| RHEL operations manual | `modules/Manual.md` | `domains/RHEL.md`; optional `domains/Linux.md` | `workflows/ManualWorkflow.md` | `reviewers/DocumentationReviewer.md` | `policies/Writing.md`; `policies/Evidence.md`; `policies/Review.md` |
| Linux/RHEL RCA | `modules/RCA.md` | `domains/RHEL.md`; optional `domains/Linux.md` | `workflows/RCAWorkflow.md` | `reviewers/TechnicalReviewer.md` | `policies/Evidence.md`; `policies/Thinking.md`; `policies/Review.md` |
| OpenShift architecture review | `modules/Architecture.md` | `domains/OpenShift.md`; optional `domains/Kubernetes.md` | `workflows/ArchitectureWorkflow.md` | `reviewers/ArchitectureReviewer.md` | `policies/Thinking.md`; `policies/Evidence.md`; `policies/Review.md` |
| Technical research brief | `modules/Research.md` | Relevant domain only | `workflows/ResearchWorkflow.md` | Optional; use only for external deliverables | `policies/Evidence.md`; optional `policies/Calibration.md` |
| Prompt review | `modules/PromptEngineering.md` | None | `workflows/PromptWorkflow.md` | `reviewers/PromptReviewer.md` | `policies/Thinking.md`; `policies/Review.md` |

## Selection Rules

1. Start with the user task, not the available files.
2. Load the smallest set that can produce an accurate, reviewable answer.
3. Prefer one domain. Add a second domain only when the task crosses a real product or platform boundary.
4. Use reviewers for external-facing artifacts, high-risk technical recommendations, or user-requested review.
5. Skip workflows for short rewrites, definitions, and low-risk answers.
6. If the required pack is missing, stop and report the missing file instead of silently substituting another pack.
