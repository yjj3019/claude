# SESSION_LOG.md — claude(FEF) project session history (append-only, never overwrite)

## Session backup: 2026-08-05 (`claude/Tunning/claude` FEF — architecture review, pack-ablation, Fable deletion)

Target: `C:\AI-Codding\claude\Tunning\claude` (FEF, independent git repo, `github.com/yjj3019/claude`)

### Completed
- **10 independent architecture reviews** (architecture-reviewer subagents run in parallel) converged on multiple Critical/Major findings, fixed in one batch in `2db68f1`: route tie-break moved from implicit array order to an explicit `priority` field; `validate_routes.py`'s keyword-shadowing check widened from checking only the first keyword to checking all of them; fixed 3 real `loading-map.md`↔`routes.json` mismatches plus added a regression validator (`check_row_mandatory_packs`); decoupled the Fable CI hard gate to continue-on-error; hook `python3`→`python`; fixed two Korean-keyword false positives (`"커널"` over-matching into RHEL-domain content, `"운영"` over-firing).
- **Pack-ablation experiment** (kernel-only vs full-FEF, 8-9 coding golden tests × N=3, 54 runs total — GT012-014, GT026-031): result was a complete tie (24/24 vs 24/24, later 3/3 vs 3/3 on GT031). Mix of manual sessions and Agent-tool subagent automation (explicit user approval).
- **Experimental design flaw found and corrected**: an independently run **critical review by the Fable5 model** found a fatal confound (C1) — both arms ran inside this repository, so `CLAUDE.md`/`AGENTS.md` were auto-injected regardless of arm, meaning the "kernel-only" arm was never actually kernel-only. **Reproduced directly in this session**: a subagent given only the single line "Fix the bug." refused to guess and cited this repo's own `AGENTS.md` §6 ("no unilateral assumptions") — confirming auto-injection. Recorded as a CORRECTION at the top of `PROGRESS.md`, inserted an `"INVALID"` field directly into both result JSON files, and added no-rerun warning banners to the protocol/runbook docs. **The "54-run tie = no FEF pack-layer effect" conclusion is void** — the real open question (a valid re-run) has to happen outside this repository (an environment with no `CLAUDE.md`, or direct API calls); not started by the user.
- **Follow-ups**: fixed `SecurityReviewer` being unreachable by routing (added a new `security_review` route); strengthened the invalid-experiment-data markers; committed 2 review artifacts under `docs/reviews/` (the consolidated 10x review and the full Fable review — previously these existed only as prose in `PROGRESS.md` with no backing file).
- **Deleted the entire Fable benchmark subsystem** (destructive action, asked for and got explicit user confirmation first): 16 scripts + 1 lib, 18 tests, 11 config files, 5 docs, 1 results directory — 116 files, 11,159 lines. Also cleaned up the CI job, the `validate_repository.py` import, and dangling references in `CLAUDE.md`/`README.md`/`scripts/README.md`. Side effect found: `docs/releases/v1.1.1.md` (a frozen release note) referenced deleted docs and failed validation — fixed by excluding `docs/releases/` from that scan rather than editing the historical record.
- **Final Fable5 repository review**: 0 Critical/Major, everything from today re-verified (direct command execution). 2 Minor items fixed immediately (a stale "ahead of origin" claim in `PROGRESS.md`, marking a resolved backlog item).
- **Routing priority decision applied**: user decided `architecture_review` should win the `coding` vs `architecture_review` tie-break → re-sequenced `config/routes.json` priorities (`architecture_review` 7→2, with `proposal`/`research`/`manual`/`prompt_review` each shifting down by 1). Because it's a single linear ranking, this relationship couldn't be isolated — the side effect (architecture_review now also wins against proposal/research/manual/prompt_review) was disclosed up front before applying; no regressions found.

### In progress / candidates for the next session (all need a user decision or manual work — not pursued further this session)
- **A valid pack-ablation re-run**: needs a genuine `CLAUDE.md`-free environment or direct API calls (confirmed not reproducible inside this repo).
- **Skills-migration A/B**: `experiment/skills-migration` branch is built; needs up to 48 manual Claude Code sessions, not started.
- **Kernel rule ablation** (rules 1/8/12/17): not started, pending a decision on execution method.
- **Non-coding route evaluation methodology**: explicitly deferred (designing a new scoring methodology is a large separate project).

### Runtime snapshot
- Branch/Path: `main` · `C:\AI-Codding\claude\Tunning\claude`
- Final commit: `e5471ae` (fully synced with `origin/main`, `git status` clean)
- Recent commit flow: `2db68f1` (hardening) → several pack-ablation data commits → `3b596df` (CORRECTION) → `8e67771`/`9445680` (Fable review follow-ups) → `743b9bd` (Fable deletion) → `0dc71cf` (final-review polish) → `e5471ae` (priority fix)
- Active errors: none. `python -m unittest discover -s tests` — all 43 green (158→43 after the Fable deletion); `validate_repository.py`/`validate_routes.py` (10 routes) pass.
- Last command: `git push origin main` (`0dc71cf..e5471ae`), succeeded.

### Handoff notes
- **Key lesson from this session**: Claude Code (and Agent-tool subagents) always auto-inject a working directory's `CLAUDE.md`/`AGENTS.md` regardless of prompt content — designing an "on/off" comparison by varying only the prompt inside this same repository is fundamentally impossible. Keep this in mind when designing similar A/B experiments in other projects.
- Cross-checking with an independent model (Fable5) caught a real, significant self-inflicted flaw this time — validates the pattern of a final cross-model review before committing to an important experimental conclusion.
- The FEF repository's own detailed history lives in that repo's `PROGRESS.md` (top 5 entries under Current Status) and `docs/reviews/` (2 files) — that's the starting point for the next session.
