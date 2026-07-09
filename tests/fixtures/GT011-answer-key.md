# GT011 Answer Key

Use this key to score `GT011-proposal.md`.

## Seeded Issues

| ID | Type | Location | Expected Finding | Severity |
|---|---|---|---|---|
| I1 | Internal contradiction | Executive Summary vs Solution Architecture | Platform version is 4.12 in the executive summary but 4.13 in architecture/sizing. | Major |
| I2 | Internal contradiction | Operations Model | Fully disconnected operation conflicts with real-time telemetry streaming to vendor cloud. | Critical |
| I3 | Requirement coverage gap | Requirements Table R5 + Appendix | Disaster recovery is required but deferred until after go-live. | Critical |
| I4 | Requirement coverage gap | Requirements Table R7 + Operations Model/Appendix | Existing monitoring integration is required but marked not applicable/excluded. | Major |
| I5 | Terminology/version/number inconsistency | Executive Summary + Solution Architecture | Platform version inconsistency: 4.12 vs 4.13. | Major |
| I6 | Terminology/version/number inconsistency | Solution Architecture + Appendix | Workload count inconsistency: 120 vs 150. | Major |
| I7 | Unsupported claim | Executive Summary + Risk and Support Model | “No customer-side downtime” / “no service interruption” is asserted without workload HA evidence. | Critical |
| I8 | Unsupported claim | Security Model | “Government-grade security certification coverage” and “all applicable public-sector audit requirements” are undefined and unsupported. | Critical |
| I9 | Roadmap/scope mismatch | Roadmap + Appendix | 16-week migration plan depends on customer middleware remediation that is outside scope. | Major |
| I10 | Hidden risk/dependency | Appendix vs Main Body | Middleware remediation dependency is hidden in appendix and absent from main risks. | Major |

## Scoring Notes

- Full credit requires issue-specific findings, not generic consistency advice.
- A response may combine I1/I5 or I3/DR risk, but it must preserve both the contradiction/gap and the affected proposal locations.
- Missing I2 or I8 should materially reduce the score because both are submission-blocking.
