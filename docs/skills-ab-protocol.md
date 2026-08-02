# Skills-Migration A/B Protocol

Branch `experiment/skills-migration` replaces the prompt-driven Autoload Protocol with native Claude Code skills generated from `config/routes.json` (`scripts/generate_skills.py`, `.claude/skills/fef-*`). This document fixes the comparison protocol before any model run, so the merge decision is mechanical.

## Arms

- **Control (A)**: `main` - loading-map routing via CLAUDE.md Autoload Protocol.
- **Treatment (B)**: this branch - native skill triggers; loading-map demoted to manual fallback.

## Tasks and Runs

- Tasks: the 8 mechanical fixture Golden Tests (GT012, GT013, GT014, GT026, GT027, GT028, GT029, GT030), baseline prompts (the `GT<id>-baseline` files under `tests/prompts/`).
- Runs: N per arm per task, decided before starting (recommended N=3; N=5 if time allows). Same model and settings for both arms; record model name per run.
- Execution: Claude Code interactive sessions in a fresh clone of the respective arm. API execution is invalid for arm B because native skill triggering does not fire outside Claude Code.

## Scoring

For each run, copy the model-edited fixture directory and score mechanically:

```text
python scripts/run_golden_test_coding.py --test 0NN --edited-dir <copy>
```

Primary metric per arm: mechanical gate pass rate (exit 0 rate) over all runs. Secondary: distribution of `mechanical_score_cap` and cap reasons.

## Decision Rule (fixed in advance)

- **Merge B** only if B's pass rate >= A's pass rate (non-inferiority) AND no new failure mode appears only in B (e.g., skills fail to trigger on a task where loading-map routed correctly).
- **Reject B** if B's pass rate is lower, or skills mis-trigger/over-trigger in ways the transcript shows.
- Ties on pass rate: prefer B (simpler runtime, native progressive disclosure) per DIAGNOSTIC-D's evidence that prompt-layer routing adds no measured gain.

## Recording

- Raw model outputs: local only (`.local/skills-ab/`, git-ignored by `work/` conventions); do not commit transcripts.
- Committed summary: one JSON per batch under `tests/results/skills-ab/` with run counts, per-test exit codes, and cap reasons; no response text.
- Skill-trigger observation per run: record whether the expected `fef-coding` skill visibly triggered (yes/no/unknown from transcript).

## Regeneration Discipline

`config/routes.json` remains the single source of truth. After any route change, run `python scripts/generate_skills.py` and commit the regenerated skills; `tests/test_generate_skills.py` fails CI on drift.
