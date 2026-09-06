# Simulation Round 3 — High-risk Gate, Hooks, Cold-start (2026-09-07)

Baseline: `origin/main` @ `0cbabb8`. Branch: `fix/sim-10-round3`.

## Defects fixed

| ID | Severity | Fix |
|---|---|---|
| S3-06 | P0 | `high_risk_keywords ∧ (action verbs OR non-question)`; definition/trivia guards |
| S3-07 | P0 | Segment-anchored test/validate runners; fail-closed unknown exit; gate `.md`/`.json` |
| S3-01 | P1 | Cold-start = `CLAUDE.md` + `AGENTS.md` (PROGRESS host-inject claim); slim AGENTS; budget 9000 |
| S3-09 | P1 | Default install keeps runtime docs only; installed tree passes `validate_framework.py` |
| S3-05 | P1 | `detect()` exposes `also_matched`; warn when a dropped route is high-risk |
| S3-03 | P1 | Unify `## Output` on all reviewers/*.md; validate requires it |

## P2 backlog (skipped this PR)

- Broader multi-route load / pack merge experiments
- Additional KO spacing edge cases beyond round-2
- Hook host-payload schema confirmation for Bash exit fields (fail-closed documented)

## Intentional choices

- High-risk floor remains ban-L0 / L1 min (no blanket L2) — unchanged from round-2 meta-review.
- `record_test_run.py` fail-closed when exit code unknown (prefer missing credit over false-green).
