# Freshness Policy

## Trigger

Load this policy when claims depend on current versions, lifecycle, CVE status, support matrices, product policy, subscription rules, regulations, pricing, or release state.

## Purpose

Prevent outdated or version-ambiguous claims in time-sensitive engineering work.

## Verification Triggers

Use current official sources or the best available primary evidence when the task involves:

- product lifecycle, end-of-life, support phase, subscription, or release schedule
- CVE status, affected versions, fixed versions, errata, or mitigation status
- support matrices, certified configurations, interoperability, or compatibility
- package, kernel, Kubernetes, OpenShift, RHEL, API, or library version behavior
- laws, regulations, standards, prices, licensing, or vendor policy
- a product, feature, model, or term that is not confidently recognized
- wording such as current, latest, recently, today, supported, available, or deprecated

## Required Scope

For version-sensitive claims, record the narrowest relevant scope:

- product and edition
- major and minor version when relevant
- platform or architecture when relevant
- verification date for current-state claims
- source or evidence location

## Rules

- Prefer official lifecycle pages, release notes, errata, security advisories, support matrices, and product documentation.
- Do not infer current support status from an old document or community discussion.
- When current verification is unavailable, state the limitation and mark the claim `[unverified]`; do not present remembered status as current fact.
- If the user explicitly prohibits external lookup, respect that constraint and identify which claims remain unverified.
- Distinguish current support policy from observed technical behavior.
- Freshness determines when to verify. `policies/Evidence.md` determines which evidence to trust.
