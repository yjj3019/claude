# RHEL Domain Pack

## Focus Areas

- RHEL lifecycle
- subscription model
- ELS/EUS
- Satellite
- Image Builder
- Insights
- SELinux
- firewalld
- system roles
- automation
- security compliance

## Rules

- Always specify RHEL major/minor version when relevant.
- Distinguish RHEL features from OpenShift, Ansible, and Satellite.
- Prefer Red Hat official documentation for support and lifecycle claims.
- Include supportability and operational impact.
- Mark unsupported lifecycle, certification, security, and numeric claims as `[unverified]`.

## Version-Sensitive Claims

Use explicit version scope for claims involving:

- RHEL major/minor release behavior
- EUS, ELS, E4S, or other lifecycle/support terms
- package streams, AppStream behavior, BaseOS, CRB, and repository availability
- upgrade paths such as Leapp
- kernel, crypto, SELinux, firewalld, nftables, and system role behavior

If the exact RHEL version is unknown, state the assumption before recommending.

## Lifecycle and Subscription

For lifecycle or subscription claims, verify:

- support phase and end dates
- EUS/ELS availability and applicability
- Simple Content Access and subscription management assumptions
- connected vs disconnected entitlement and repository access model

Do not generalize RHEL 8, RHEL 9, and RHEL 10 behavior without evidence.

## Public Sector Considerations

For public-sector proposals or standardization work, check whether the artifact addresses:

- procurement and support model
- security review expectations
- auditability and operational accountability
- restricted network or disconnected operations
- domestic support and escalation path
- compliance wording without inventing certifications

Certification, compliance, or public-sector eligibility claims require a source, date, and product/version scope.

## Disconnected / Restricted Network Operations

For air-gapped or restricted environments, include operational impact for:

- repository mirroring and content lifecycle
- Satellite or alternative repository management
- patch import, validation, and rollback
- ISO/image-based installation or provisioning
- Insights limitations and offline alternatives
- automation execution without external connectivity

## Security and Compliance

When relevant, distinguish and scope:

- SELinux mode and policy impact
- crypto-policies and FIPS mode assumptions
- OpenSCAP, CIS, STIG, or organizational baseline checks
- audit logging and evidence collection
- vulnerability remediation workflow
- exception handling and compensating controls

Do not imply compliance is automatic because RHEL supports a control mechanism.

## Operations and Automation

Operational recommendations should include:

- validation method
- rollback or recovery consideration
- monitoring/logging impact
- patching and maintenance workflow
- system roles or Ansible applicability
- HA Add-On, Pacemaker, kdump, tuned, and performance profile scope where relevant

## Competitive / Clone OS Positioning

When comparing RHEL with rebuild or clone distributions, avoid unsupported superiority claims.
Compare using defensible criteria such as:

- vendor support and escalation
- lifecycle and errata model
- certification ecosystem
- security response process
- enterprise tooling integration
- operational accountability

## Proposal Fact Discipline

Any numeric, lifecycle, certification, support, or competitive claim used in proposals must include:

- source URL
- source date or accessed date
- RHEL major/minor scope

Claims without this evidence must be marked `[unverified]` or removed.
The domain pack must not be used to launder unsupported proposal facts.
## Proposal Source Requirements

For RHEL proposal work, do not state lifecycle dates, EUS/ELS availability, certification coverage, FIPS/compliance status, support entitlement, or competitive claims as facts unless the proposal includes or requests verifiable source material.

Minimum acceptable source metadata:

- source URL or customer-provided source name
- accessed date or source publication date
- RHEL major/minor version scope
- claim scope and limitation

If sources are unavailable during drafting, use wording such as:

- `[unverified] This should be validated against current Red Hat lifecycle documentation.`
- `Assumption: ...; validation required before submission.`
- `Source required before customer-facing use.`

For public-sector or restricted-network proposals, also flag claims that depend on online services, external telemetry, cloud connectivity, or certification interpretation.
