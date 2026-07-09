# Golden Test 001: RHEL Proposal

## Purpose

Evaluate whether FEF improves a RHEL public-sector proposal response compared with a baseline prompt.

## Scenario

Customer profile:

- Public-sector organization
- Migrating from CentOS 7 after EOL
- Approximately 200 Linux servers
- Restricted/disconnected network environment
- Needs an enterprise standardization proposal for RHEL 9
- Output constraint: 16-slide proposal blueprint

## RFP Excerpt

The proposal must address:

1. Migration approach from CentOS 7 to an enterprise Linux standard.
2. RHEL 9 lifecycle and support benefits.
3. Security compliance approach for public-sector operation.
4. Patch management in a disconnected network.
5. Operational automation and standard build process.
6. Comparison with community rebuild distributions.
7. Local support and escalation model.
8. Migration schedule and risk mitigation.

Intentional ambiguity:

- The RFP asks for "security certification coverage" but does not name the required certification.
- The RFP asks for "zero service interruption migration" without defining workload HA capability.

Intentional contradiction:

- The RFP requires "fully offline operation" and also asks for "real-time cloud-based operational insights."

## Baseline Prompt

```text
Create a 16-slide proposal for adopting RHEL 9 in this public-sector environment.
```

## FEF Prompt

```text
Use FEF Kernel and docs/loading-map.md for a RHEL proposal.
Apply the Proposal Module, RHEL Domain Pack, Proposal Workflow, Proposal Reviewer, and relevant Evidence/Writing/Review policies.
Create a 16-slide proposal blueprint for the scenario and RFP excerpt.
```

## Scoring Rubric

Total: 100 points.

| Dimension | Points | Measurement |
|---|---:|---|
| Ambiguity handling | 20 | Detects both ambiguous requirements; asks or states assumptions without over-questioning |
| Contradiction handling | 15 | Identifies the offline vs real-time cloud insights conflict and proposes a resolution path |
| Factual accuracy | 25 | Avoids lifecycle, support, certification, and RHEL feature errors; unsupported facts lose points |
| `[unverified]` discipline | 15 | Marks unsupported claims without excessive tagging that weakens the proposal |
| Structure completeness | 15 | Produces a coherent 16-slide blueprint with executive, technical, risk, roadmap, and support content |
| Competitive logic | 10 | Compares rebuild/clone distributions with specific, defensible enterprise criteria |

## Failure Modes

Record each occurrence:

- Accepts the contradiction without comment.
- Invents certifications, lifecycle dates, or support claims.
- Asks more than three clarifying questions before providing a usable draft.
- Overuses `[unverified]` until the proposal becomes unusable.
- Fails to produce 16 slides.
- Produces brochure-like product claims without buyer problem or operational model.

## Result Recording Template

Create result files under `tests/results/` using:

```text
tests/results/GT001-YYYYMMDD.md
```

Each result file should include:

```markdown
# GT001 Result - YYYY-MM-DD

## Run Setup

- Baseline runs: N
- FEF runs: N
- Model/environment:
- Evaluator:

## Score Summary

| Variant | Average | Std Dev | Min | Max |
|---|---:|---:|---:|---:|
| Baseline | | | | |
| FEF | | | | |

## Dimension Scores

| Dimension | Baseline Avg | FEF Avg | Delta |
|---|---:|---:|---:|
| Ambiguity handling | | | |
| Contradiction handling | | | |
| Factual accuracy | | | |
| `[unverified]` discipline | | | |
| Structure completeness | | | |
| Competitive logic | | | |

## Failure Mode Counts

| Failure Mode | Baseline Count | FEF Count |
|---|---:|---:|
| Contradiction accepted | | |
| Invented claims | | |
| Excessive questions | | |
| Excessive `[unverified]` | | |
| Slide count failure | | |
| Brochure-like output | | |

## Decision

PASS if FEF average uplift is at least +10 points and variance decreases.
Otherwise FAIL or HOLD with notes.
```

## Minimum Run Count

Run at least five baseline and five FEF outputs before treating the result as meaningful.
