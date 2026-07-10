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

## Evidence Priority

1. Official documentation
2. Vendor knowledge base
3. Release notes
4. Standards / RFCs
5. Source code / logs / direct data
6. Reputable engineering publications
7. Community discussions
8. Rumors / leaks / social sources

## Rules

- Version-sensitive claims require version scope.
- Unsupported claims must not be written as facts.
- Conflicting evidence must be disclosed.
- If evidence is missing, say what would be needed to verify.
- Actionable findings must include the narrowest available location: section, page, table, log line, file, or line number.
- Use scoped verification placeholders for unverifiable facts, for example `[검증 필요: 대상]`; do not over-tag ordinary prose.
