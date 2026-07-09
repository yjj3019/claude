# GT011 Fixture: Proposal Excerpt with Seeded Consistency Issues

## Executive Summary

Acme CloudOps proposes a 12-month modernization program to standardize the customer's application platform, reduce operational risk, and improve audit readiness.
The proposal covers all eight requirements in the RFP and can be delivered with no customer-side downtime.
The solution is based on Acme Enterprise Platform 4.12 and includes 24x7 premium support for all production and non-production systems.

## Requirements Table

| ID | Requirement | Proposal Response |
|---|---|---|
| R1 | Standardize application runtime across departments | Addressed in Solution Architecture |
| R2 | Provide migration plan for 120 workloads | Addressed in Roadmap |
| R3 | Support disconnected network operation | Addressed in Operations Model |
| R4 | Provide role-based access control and audit logging | Addressed in Security Model |
| R5 | Provide disaster recovery design | To be finalized during implementation |
| R6 | Provide training and handover | Addressed in Support Model |
| R7 | Integrate with existing monitoring | Not applicable |
| R8 | Provide fixed delivery schedule and staffing plan | Addressed in Roadmap |

## Solution Architecture

The proposed architecture uses Acme Enterprise Platform 4.13 as the standard runtime for all departments.
The platform will be deployed in two data centers with a shared management plane and a single centralized logging stack.
The design supports online migration of all 120 workloads with no service interruption.

The executive summary states the platform version as 4.12, but the architecture diagrams and sizing assumptions use 4.13.
The proposal assumes 120 workloads in the migration plan and 150 workloads in the sizing appendix.

## Operations Model

The environment will operate in a fully disconnected network with no outbound internet access.
Operational insights will be delivered through Acme Cloud Insights with real-time telemetry streaming to the vendor cloud service.
Patch packages will be synchronized monthly through a controlled import process.

Existing customer monitoring integration is excluded from scope and will be handled after go-live.

## Security Model

The platform provides government-grade security certification coverage and ensures compliance with all applicable public-sector audit requirements.
Role-based access control, centralized audit logs, and encryption at rest are included.
The exact certification requirement is not listed in the RFP or appendix.

## Roadmap and Staffing

The project will complete in 16 weeks using two full-time engineers and one project manager.
Phase 1 covers assessment and design.
Phase 2 covers platform build.
Phase 3 covers migration of 120 workloads.
Phase 4 covers training and handover.

The assumptions appendix states that customer application teams must remediate unsupported middleware before migration and that this remediation is outside Acme scope.

## Risk and Support Model

Acme will provide 24x7 premium support for production systems.
Non-production environments are covered by business-hours support.
Major migration risks are expected to be low because all workload migration will be online and automated.

## Appendix: Assumptions and Exclusions

- Sizing assumes 150 workloads, including 30 future workloads.
- Customer application teams are responsible for middleware remediation before migration.
- Monitoring integration with the customer's existing toolchain is excluded.
- Disaster recovery architecture will be designed after production go-live.
- Non-production systems receive business-hours support only.
