# Manual Ablation Runbook (Pack Ablation + Skills A/B)

Literal step sequence for the two experiments decided on 2026-08-04 (`PROGRESS.md` Next Session #0/#1/#2a). This file is the checklist; the decision rules and rationale live in `docs/pack-ablation-protocol.md` (this repo) and `skills-ab-protocol.md` (on the `experiment/skills-migration` branch, not `main` — check that branch out to read it) — do not duplicate them here, and do not deviate from them after seeing partial results.

Both experiments reuse the same scorer and the same result-file convention, so the loop below is shared. Run pack ablation first — it needs no branch switching and directly re-tests DIAGNOSTIC-D.

## Per-run loop (repeat for each test x arm x run)

1. Copy the pristine fixture so the run doesn't contaminate later runs. Substitute the test ID (e.g. `012`) for `<id>`:
   ```
   cp -r tests/fixtures/GT<id>-code tests/fixtures/GT<id>-code.run
   ```
2. Open a **fresh** Claude Code session (new window/conversation — not a continuation of a prior run, so the model can't recall the previous arm's fix).
   - Pack ablation: stay on `main` for both arms; the arm is selected entirely by which prompt file you paste (see step 3).
   - Skills A/B: check out the arm's branch first (`main` for control, `experiment/skills-migration` for treatment) in that session's working copy.
3. Paste the exact contents of the arm's prompt file as the task (e.g. for test 012: `tests/prompts/GT012-baseline.md` or `tests/prompts/GT012-fef.md`, same naming for every other test ID):
   - Pack ablation Kernel-only / Skills A/B control: the `*-baseline.md` prompt.
   - Pack ablation Full FEF / Skills A/B treatment: the `*-fef.md` prompt.
   - Point the model at the `.run` copy from step 1, not the original.
4. Let the session run to completion. Note the model name Claude Code reports for that session.
5. Skills A/B only: read the transcript and record whether the coding skill visibly triggered (yes/no/unknown).
6. Score mechanically, substituting the same test ID and the `.run` copy path:
   ```
   python scripts/run_golden_test_coding.py --test <id> --edited-dir <path-to-the-.run-copy>
   ```
7. Append one run entry to the batch JSON (start from `tests/results/pack-ablation/RESULT.example.json` or `tests/results/skills-ab/RESULT.example.json`) with `mechanical_score_cap`, `cap_reasons`, and the scorer's own `exit_code` (its process exit status, not a recomputed threshold).
8. Delete the `.run` copy so it doesn't get committed or reused.

## Coverage

- Pack ablation: 8 tests (GT012, GT013, GT014, GT026-030) x 2 arms x N runs (N fixed before starting, recommended 3) = 48 runs at N=3.
- Skills A/B: same 8 tests x 2 arms x N runs = 48 runs at N=3.

## After all runs for an experiment

1. Fill in `pass_rate` per arm (exit_code==0 count / total runs) in that experiment's batch JSON.
2. Apply the pre-registered decision rule from the matching protocol doc — do not re-derive a new rule from the results.
3. Commit the batch JSON under `tests/results/<experiment>/` (no response text, per both protocols).
4. Write the outcome into `PROGRESS.md` and, for pack ablation, cross-reference `docs/opus5-diagnostic-findings.md` (does this confirm, contradict, or narrow DIAGNOSTIC-D?).
