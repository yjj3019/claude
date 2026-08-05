# Architecture Review — 10 Independent Passes (2026-08-04)

**Provenance note (added 2026-08-05, per an external review's finding — see `2026-08-05-fable-critical-review.md` M4):** this is a *consolidated synthesis*, written by the orchestrating session from 10 independent `architecture-reviewer` subagent outputs, not the raw agent transcripts themselves. The raw outputs were not committed to the repository when the review ran — only this summary and the commit message of `2db68f1` referenced the findings, which is a real evidence-discipline gap (no `file:line`-anchored artifact existed until this file was added retroactively). Treat the consensus counts below as the orchestrator's tally of what it read across 10 agent responses, not as independently re-verifiable from this file alone. 5 of the 10 spawned passes returned only a brief tool-use preamble with no final report (background/resource contention); 5 returned full reports. The 5 stalled passes were later resumed via `SendMessage` and all completed (see the session transcript for the two additional full reports obtained that way, not reproduced verbatim here).

## Scope

Target: `C:\AI-Codding\claude\Tunning\claude` (the FEF framework itself — kernel/policies/modules/domains/reviewers/workflows layering, `config/routes.json` routing, validation scripts). Each pass was given the same brief (layering architecture summary) and asked to judge fitness, operational risk, extensibility, and maintainability, independently, in parallel, without seeing other passes' output.

## Consensus findings (ranked by how many of the completed passes raised each one)

### Critical — full or near-full consensus

**No measured benefit, full cost still carried.** `PROGRESS.md`'s DIAGNOSTIC-D entry ("No FEF accuracy or conciseness improvement was observed over baseline... Kernel-only configuration is the recommended default") was cited by every completed pass as the load-bearing risk: ~45 pack files, 25+ scripts, and CI machinery are maintained against an unfalsified benefit hypothesis. Recommendation across passes: freeze new packs pending an ablation.

### Major — raised by most/all completed passes

- **Route tie-breaking is undeclared array-order dependence.** `scripts/lib/routing.py` breaks ties on `(match_count, -index)`; `config/routes.json`'s array order is load-bearing but documented nowhere. `README.md`'s "proposal beats research" example is explained by index position, not stated intent.
- **Shadowing validation checks only each route's first keyword.** `scripts/validate_routes.py` sampled `route["keywords"][0]`; the remaining keywords (up to ~20 per route) had no CI coverage.
- **`docs/loading-map.md` ↔ `config/routes.json` content drift, uncaught by any validator.** Three concrete mismatches found: `CodeChangeReviewer` (prose said "optional", config always loaded it), `ResearchWorkflow`/`TechnicalReviewer` on the blog route (same pattern), and a split `Calibration` policy requirement across two loading-map rows mapped to one route.
- **Fable benchmark (declared closed/diagnostic-only) still hard-gated CI.** `.github/workflows/validate.yml` and `scripts/validate_repository.py` failed the whole build on Fable schema issues despite `PROGRESS.md` recording the workstream as closed.
- **Hook commands used `python3`**, unverified against this Windows/PowerShell-primary workspace; multiple passes flagged this as a plausible silent-failure point given the hooks fail open.
- **`record_test_run.py` recorded a marker for any test-shaped command string, regardless of exit code** — a failing test run counted as "verified."
- **Korean keyword substring matching without word boundaries.** `"커널"` (RHEL domain keyword) matched this framework's own "kernel" discussions; `"운영"` (a high-risk keyword) over-fired on `"운영체제"`/`"운영 매뉴얼"`.
- **Domain selection cap (2) with only 2 subsumption pairs defined**, producing hard routing failures on realistic multi-domain tasks (e.g. RHEL+Ansible+Satellite) with no priority-based fallback.

### Minor / Suggestion (raised by 2+ passes)

- Orphan-pack detection is advisory-only and satisfiable by a bare backtick mention in prose, not actual reachability.
- README's documented local validation command is weaker than what CI actually runs.
- Cross-layer duplication (the same "find shared root cause, verify before completing" rule restated near-verbatim in kernel rules, `modules/Coding.md`, `workflows/CodingWorkflow.md`, `reviewers/CodeChangeReviewer.md`) — a maintenance liability more than a correctness bug.
- `routing.py` (the single most behavior-determining file) had no dedicated unit test file at the time of review.

## Disposition

Items 2 through 8 in the Major list above were fixed in commit `2db68f1` the same day (priority field, full-keyword shadowing check, loading-map content-drift guard, Fable CI decoupling, `python3`→`python`, exit-code check on the test-run hook, Korean keyword narrowing). The Critical item (no measured benefit) was the direct motivation for the pack-ablation experiment that followed — see `PROGRESS.md`'s pack-ablation entries and, critically, the **2026-08-05 correction** noting that experiment's own confound (both ablation arms ran with this repo's `CLAUDE.md` auto-loaded regardless of prompt, so the resulting tie is not valid evidence either way).
