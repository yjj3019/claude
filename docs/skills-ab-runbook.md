# Skills A/B Execution Runbook

Procedural companion to `docs/skills-ab-protocol.md` (which fixes the decision rule; this file only describes mechanics and changes no criteria).

## One-Time Setup

```text
git clone git@github.com:yjj3019/claude.git ~/ab/arm-a && cd ~/ab/arm-a && git checkout main
git clone git@github.com:yjj3019/claude.git ~/ab/arm-b && cd ~/ab/arm-b && git checkout experiment/skills-migration
```

Run all helper commands from the experiment-branch checkout (e.g. `~/Claude/fef` on `experiment/skills-migration`).

## Per-Session Loop (repeat per arm x test x run)

1. `python3 scripts/run_skills_ab.py prepare --arm A --arm-root ~/ab/arm-a --test 012`
   (resets the fixture in the arm clone and prints the exact prompt)
2. Open a FRESH Claude Code session with the arm clone as the working directory and paste the printed prompt. Let it finish; do not coach it. Note whether an `fef-*` skill visibly triggered.
3. `python3 scripts/run_skills_ab.py collect --arm A --arm-root ~/ab/arm-a --test 012 --run 1 --batch BATCH-1 --model <model-name> --skill-triggered yes|no|unknown|n/a`
   (copies the edited fixture to `.local/skills-ab/`, scores it mechanically, appends to `tests/results/skills-ab/BATCH-1.json`; duplicate arm/test/run records are refused)

Use `--skill-triggered n/a` for arm A (no skills exist on main).

## Recommended Order

Alternate arms per test to spread any model drift: A/GT012 run1, B/GT012 run1, A/GT013 run1, ... then run2 across all, then run3. 8 tests x 3 runs x 2 arms = 48 sessions.

## Decision

`python3 scripts/run_skills_ab.py report --batch BATCH-1` prints per-arm pass rates, per-test breakdown, and applies the pre-registered rule (MERGE-B eligible / REJECT-B / INSUFFICIENT). The script never merges; the merge itself stays a human PR action, and transcripts plus `skill_triggered` observations must be reviewed per protocol before merging.

## Committing Results

Commit only `tests/results/skills-ab/*.json` (counts, exit codes, cap reasons — no response text). `.local/skills-ab/` stays untracked.
