# Loading Map

Load only files relevant to the task. Simple, low-risk work uses the inlined Kernel.
For mapped work, preview with `python scripts/detect_task.py --task "..."`; do not also load this map unless manual selection or clarification is needed.

## Load Limits

Module 1; Domain ≤2; Workflow 1; Reviewer 1; Policies ≤3.
Required Integrity Policies follow triggers; never trim them to make a route look lighter.

## Task Map

| Task Type | Module | Domain | Workflow | Reviewer | Policies |
|---|---|---|---|---|---|
| RHEL proposal | `modules/Proposal.md` | `domains/RHEL.md`; optional `domains/EnterpriseArchitecture.md` | `workflows/ProposalWorkflow.md` | `reviewers/ProposalReviewer.md` | `policies/Writing.md`; `policies/Evidence.md`; `policies/Review.md` |
| Proposal consistency check | `modules/Proposal.md` | Relevant domain only | `workflows/ProposalWorkflow.md` | `reviewers/ProposalConsistencyReviewer.md` | `policies/Writing.md`; `policies/Evidence.md`; `policies/Review.md` |
| RHEL operations manual | `modules/Manual.md` | `domains/RHEL.md`; optional `domains/Linux.md` | `workflows/ManualWorkflow.md` | `reviewers/DocumentationReviewer.md` | `policies/Writing.md`; `policies/Evidence.md`; `policies/Review.md` |
| Linux/RHEL RCA | `modules/RCA.md` | `domains/RHEL.md`; optional `domains/Linux.md` | `workflows/RCAWorkflow.md` | `reviewers/TechnicalReviewer.md` | `policies/Evidence.md`; `policies/Thinking.md`; `policies/Review.md` |
| OpenShift architecture review | `modules/Architecture.md` | `domains/OpenShift.md`; optional `domains/Kubernetes.md` | `workflows/ArchitectureWorkflow.md` | `reviewers/ArchitectureReviewer.md` | `policies/Thinking.md`; `policies/Evidence.md`; `policies/Review.md` |
| Technical research brief / Current-version research | `modules/Research.md` | Relevant domain only | None (procedure in module) | None | `policies/Evidence.md`; `policies/Freshness.md`; `policies/Calibration.md` |
| Technical blog post | `modules/Blog.md` | Relevant domain only | `workflows/ResearchWorkflow.md` | `reviewers/TechnicalReviewer.md` | `policies/Writing.md`; `policies/Evidence.md`; optional `policies/Freshness.md` |
| Prompt review | `modules/PromptEngineering.md` | None | `workflows/PromptWorkflow.md` | `reviewers/PromptReviewer.md` | `policies/Thinking.md`; `policies/Review.md`; optional `policies/Evidence.md` |
| Code modification | `modules/Coding.md` | Relevant domain only when product-specific behavior matters | None (procedure in module) | optional `reviewers/CodeChangeReviewer.md` for consequential changes | `policies/FileHandling.md`; `policies/ToolExecution.md`; optional `policies/Freshness.md` |
| File-backed technical analysis (manual-selection only; no keyword route) | `modules/Research.md` | Relevant domain only | None | Optional `reviewers/TechnicalReviewer.md` for high-risk deliverables | `policies/FileHandling.md`; `policies/Evidence.md`; optional `policies/Review.md` |
| Knowledge-governance audit (manual-selection only; no keyword route) | `modules/Research.md` | None | None | Optional `reviewers/DocumentationReviewer.md` for external-facing guidance | `policies/FileHandling.md`; `policies/Evidence.md`; optional `policies/Freshness.md` |
| Executive summary (manual-selection only; no keyword route) | `modules/ExecutiveSummary.md` | Relevant domain only | None | Optional `reviewers/DocumentationReviewer.md` for external-facing summaries | `policies/Writing.md`; optional `policies/Decision.md` when the summary carries a recommendation |
| Meeting notes (manual-selection only; no keyword route) | `modules/Meeting.md` | None | None | None | `policies/Writing.md` |
| Presentation (manual-selection only; no keyword route) | `modules/Presentation.md` | Relevant domain only | Optional `workflows/ResearchWorkflow.md` for source-heavy decks | Optional `reviewers/DocumentationReviewer.md` | `policies/Writing.md`; optional `policies/Evidence.md` |
| Security-focused design/change review | None | Relevant domain only | None | `reviewers/SecurityReviewer.md` | `policies/Evidence.md`; optional `policies/ToolExecution.md` |
| AI infrastructure or vehicle telemetry task (manual-selection only; no keyword route) | Relevant module for the task | `domains/AI.md` or `domains/Tesla.md` as applicable | Relevant workflow for the task | Relevant reviewer for the task | Relevant policies for the task |

`domains/Ansible.md` and `domains/Satellite.md` are keyword-detected independently of task type (see `config/routes.json`, whose `domains` list applies across every route) and are not tied to a specific Task Map row; combine either with the task's listed domain when the task text names Ansible or Satellite, subject to the domain load limit above.

## Selection Rules

- Start from the requested outcome. Coding and Research modules include their workflow; compatibility entries need no second load.
- Select relevant product domains only. RHEL subsumes Linux; OpenShift subsumes Kubernetes.
- Ansible/Satellite keywords apply across routes. Domain overflow keeps two by keyword hits then mention order and warns about every dropped domain; if a dropped domain is required, narrow/re-detect.
- Review is optional unless requested or consequential risk requires it; use one reviewer after a draft, never review loops.
- Weak coding fallback keywords require code evidence. Unmapped high-risk tasks receive Evidence plus a warning, never a silently safe Kernel-only result.
- Missing required pack: report the gap and limit work safely. Optional missing material matters only if it changes confidence.

## Policy Classes

Integrity: Evidence, FileHandling, Freshness, ToolExecution and applicable safety/security. User instructions override preference defaults when integrity holds.

## Policy Selection Rules

| Trigger | Required policy |
|---|---|
| External factual/technical claims | `policies/Evidence.md` |
| Current/version-sensitive/support/CVE claims | `policies/Freshness.md` |
| Reading/modifying/generating files | `policies/FileHandling.md` |
| Commands/tests/builds/tool actions | `policies/ToolExecution.md` |
| Formal review | `policies/Review.md` |
| Recommendation requiring trade-offs | `policies/Decision.md` |

At most three: prioritize execution risk and avoid duplicating rules already covered by the selected workflow/reviewer. If necessary safety contracts cannot fit, narrow the task rather than silently drop them.
