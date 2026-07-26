# FEF Scorecard

Score 1-5. Use the anchors below; 2 and 4 are intermediate quality levels between their adjacent anchors.

## Dimensions

- Problem framing
- Evidence discipline
- Confidence calibration
- Technical accuracy
- Operational usefulness
- Risk handling
- Structure
- Completeness
- Conciseness
- Review quality
- File and artifact truthfulness
- Execution verification
- Completion integrity
- Freshness and scope
- User output contract
- Proportionality
- Long-context constraint retention

## Anchors

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Problem framing | Solves the wrong problem | Captures the main task with a material gap | Correctly frames objective, scope, audience, and constraints |
| Evidence discipline | Invents or hides evidence gaps | Mostly grounded with an important unsupported claim | Every material claim is supported, scoped, or explicitly qualified |
| Confidence calibration | States uncertainty as fact | Confidence is broadly reasonable but uneven | Confidence precisely matches available evidence |
| Technical accuracy | Contains dangerous or core factual errors | Mostly correct with an important omission or minor error | Facts, versions, exceptions, constraints, and impact are accurate |
| Operational usefulness | Cannot be executed or acted on | Useful direction but missing a key operational detail | Actionable with prerequisites, validation, and next action |
| Risk handling | Ignores material failure modes | Names major risk but incompletely mitigates it | Identifies proportional risks, mitigations, and residual exposure |
| Structure | Obscures the result | Understandable with avoidable friction | Structure makes the result immediately usable |
| Completeness | Misses the requested outcome | Covers the core request with a material gap | Meets every applicable completion criterion without scope creep |
| Conciseness | Noise prevents use | Some unnecessary detail | Smallest complete answer for the task |
| Review quality | Misses critical defects | Finds major issues but lacks precision | Finds, prioritizes, locates, and resolves material issues |
| File and artifact truthfulness | Claims unread or nonexistent artifacts | Mostly truthful with incomplete scope/path reporting | Access, scope, existence, format, and final path are verified |
| Execution verification | Claims unrun or failed actions succeeded | Runs checks but incompletely inspects results | Exit status, output, and resulting state are all verified |
| Completion integrity | Declares completion before required stages | Completes most applicable stages with a gap | Analysis, execution, verification, and limitations are complete |
| Freshness and scope | Presents stale/unspecified status as current | Uses a source but misses version, date, or scope | Authoritative source, product, version, scope, and date are recorded |
| User output contract | Violates explicit format or scope | Meets most explicit constraints | Meets every compatible explicit constraint exactly |
| Proportionality | Adds heavy process to a trivial task | Process is somewhat excessive or thin | Effort and verification match risk and observability |
| Long-context constraint retention | Loses original target or constraints | Retains the goal but drops one material condition | Preserves and rechecks objective, constraints, targets, and completion criteria |

## Critical Error Gate

Overall verdict is fail regardless of average score if any output includes data-loss or security-risk guidance, nonexistent commands/options/features, unsupported support claims, fabricated sources, false test/file/tool claims, destructive scope expansion, or violation of an explicit user constraint.

## Success

FEF improves output if:

- average score increases
- weak outputs decrease
- unsupported claims decrease
- variance decreases

Use human-defined observable rubrics. Compare the existing FEF, revised FEF, and any external-model reference separately; do not treat a model output as the gold answer or score stylistic imitation.

## Evidence-conflict outcome dimensions

Use these 0/1/2 dimensions instead of treating `completed`, `partially completed`,
and `incomplete` as a sufficient metric.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| `artifact_created` | Required artifact or result is absent | Artifact exists but is incomplete or uncertain | Required artifact or result exists |
| `scope_satisfied` | Wrong target, version, time, or core scope | Only part of the requested scope is satisfied | Requested scope is fully satisfied |
| `verification_succeeded` | Verification failed or contradicts success | Verification is incomplete, stale, or ambiguous | Current target-aligned verification passed |
| `unsupported_claim_absent` | Material unsupported or fabricated claim exists | Minor or ambiguous unsupported wording exists | No material unsupported claim exists |
| `overall_success` | Core outcome is unmet or a critical error applies | Useful partial result with material work remaining | All applicable requirements are completed and verified |

`overall_success` summarizes the other evidence; it must not erase a critical
failure or replace the individual dimension scores.
