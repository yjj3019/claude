# Pack-Level Ablation Protocol

> **⚠️ KNOWN FLAW (found 2026-08-05, see `PROGRESS.md`'s CORRECTION entry and `docs/reviews/2026-08-05-fable-critical-review.md`, finding C1): the "Kernel-only (K)" arm below does NOT work as designed.** Running either prompt inside this repository's working directory (interactively or via an Agent-tool subagent) auto-loads `CLAUDE.md`/`AGENTS.md` regardless of which prompt file is pasted, so the K arm never actually runs kernel-only. A results tie under this protocol is **not valid evidence** that the pack layer adds nothing — both arms had it loaded. Do not re-run this protocol as written. A valid version needs either (a) a working directory with no project `CLAUDE.md` at all, or (b) direct API calls with only the bare prompt text as input, no Claude Code project context. The rest of this document is left unedited for the historical record of what was (incorrectly) run on 2026-08-04/05; treat "Kernel-only" throughout as aspirational, not achieved.

DIAGNOSTIC-D (`docs/opus5-diagnostic-findings.md`) found no measured accuracy/conciseness gain from the full FEF pack layer over Kernel-only, on 5 simple evidence-judgment scenarios. The pack layer (modules/domains/policies/reviewers/workflows, ~45 files) has not been re-tested since, and it is the load-bearing question behind `PROGRESS.md`'s Critical finding from the 2026-08-04 architecture review: an unmeasured layer is being maintained at full cost. This document fixes the comparison protocol before any run, so the merge/prune decision is mechanical, not post-hoc.

This is a different instrument from the existing Kernel rule ablation (`PROGRESS.md` Next Session #2, rules 1/8/12/17): that one asks *which kernel rules are redundant*; this one asks *does the pack layer above the kernel earn its cost at all*, using the 8 mechanical fixture-mode Golden Tests instead of DIAGNOSTIC-D's 5 manually-scored scenarios.

## Arms

- **Kernel-only (K)**: prompt the model with the test's `*-baseline.md` file (e.g. `tests/prompts/GT012-baseline.md`) only — no loading-map, no pack files, Kernel behavior only (this is the existing baseline-prompt family, already used by the coding-mode Golden Tests as fixtures).
- **Full FEF (F)**: prompt the model with the matching `*-fef.md` file (e.g. `tests/prompts/GT012-fef.md`), which invokes "FEF coding behavior from the active runtime harness and Evidence policy" — i.e. the full autoload path (Kernel + `modules/Coding.md` + `workflows/CodingWorkflow.md` + `policies/FileHandling.md`/`ToolExecution.md`, per the `coding` route in `config/routes.json`).

Both prompt families already exist for all 8 fixture tests (GT012-014, GT026-030) — no new prompt authoring needed.

## Tasks and Runs

- Tasks: the same 8 mechanical fixture Golden Tests used by CI (GT012, GT013, GT014, GT026, GT027, GT028, GT029, GT030).
- Runs: N per arm per task, fixed before starting (recommended N=3, matching the Skills A/B protocol's N; raise to N=5 only if time allows — do not raise N after seeing partial results).
- Execution: manual interactive Claude Code sessions (per the 2026-08-04 model-execution decision), same model for both arms, record model name per run. Each run starts from a clean fixture copy (`tests/fixtures/GT0NN-code/`) so runs don't contaminate each other.

## Scoring

For each run, copy the model-edited fixture directory and score mechanically — identical to the Skills A/B protocol:

```text
python scripts/run_golden_test_coding.py --test 0NN --edited-dir <copy>
```

Primary metric per arm: mechanical gate pass rate (exit 0 rate) over all runs. Secondary: `mechanical_score_cap` distribution and cap reasons (e.g. sibling-caller misses, test-file tampering) — these distinguish *why* an arm failed, not just whether it did.

## Decision Rule (fixed in advance)

- **Prune the pack layer for coding tasks** if K's pass rate >= F's pass rate (non-inferiority) and K shows no failure mode that F does not also show. This would confirm DIAGNOSTIC-D's finding on a second, mechanically-scored instrument and justify deleting or demoting `modules/Coding.md` + `workflows/CodingWorkflow.md` + the coding route's optional-Freshness note.
- **Keep the pack layer** if F's pass rate is meaningfully higher, or if F avoids a failure mode K exhibits (e.g. K misses sibling-caller scans more often — `modules/Coding.md`'s explicit instruction to scan callers is a plausible mechanism for exactly that gap). In this case, follow up by testing which *specific* pack drives the gain (module vs workflow vs policies) before assuming the whole layer is load-bearing.
- Ties on pass rate: prefer K (smaller context cost, per the same reasoning DIAGNOSTIC-D and the Skills A/B protocol both used).
- This result is scoped to coding tasks only. It does not generalize to other routes (proposal, RCA, architecture review, etc.) without a separate run — say so explicitly in the writeup rather than extrapolating.

## Recording

- Raw model outputs: local only, do not commit transcripts (same convention as Skills A/B — `.local/pack-ablation/` or equivalent, git-ignored).
- Committed summary: one JSON per batch under `tests/results/pack-ablation/` with run counts, per-test exit codes, and cap reasons — no response text.
- Writeup goes in `docs/` alongside `docs/opus5-diagnostic-findings.md`, cross-referencing DIAGNOSTIC-D and stating whether this run confirms, contradicts, or narrows its conclusion.
