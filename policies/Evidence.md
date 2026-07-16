# Evidence Policy

## Confidence Levels

High:
- directly supported by official documentation, primary source, direct logs, or verified data

Medium:
- supported by reputable sources or strong inference from evidence

Low:
- plausible but weakly supported

Unknown:
- insufficient evidence; mark as `[unverified]`

## Evidence Priority by Claim Type

### Current environment state

1. Direct files, logs, command output, test results, and verified observations from that environment
2. System metadata, package databases, and configuration state
3. Official documentation
4. Inference

### Product behavior and support policy

1. Official product documentation, release notes, and support policies
2. Standards and vendor knowledge bases
3. Reproducible direct observations
4. Reputable secondary sources
5. Inference

### Conflict handling

- Direct observation establishes what occurred in the current environment.
- Official documentation establishes expected or supported behavior.
- When they differ, report the discrepancy rather than silently forcing one to replace the other.

## Rules

- Version-sensitive claims require version scope.
- Unsupported claims must not be written as facts.
- Conflicting evidence must be disclosed.
- If evidence is missing, say what would be needed to verify.
- Actionable findings must include the narrowest available location: section, page, table, log line, file, or line number.
- Use scoped verification placeholders for unverifiable facts, for example `[검증 필요: 대상]`; do not over-tag ordinary prose.
- Treat direct file contents, logs, command output, and test results as evidence rather than assumptions.
- Current or version-sensitive claims require the applicable product, version, scope, verification date, and source.
- Prefer paraphrase and quote only the minimum text needed to preserve technical meaning.
- Preserve exact errors, logs, configuration values, and code fragments when they are necessary evidence.
