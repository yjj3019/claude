# Project Progress

## Current Status

- Updated: 2026-07-27 KST
- Branch: `main`
- Remote state: pushed through `0781297` ("feat: add tool-safe Opus 5 diagnostics" — DIAGNOSTIC-C safety hardening: `maximum_tool_calls: 0` constraint, offline-evidence prompt banner, PRIVATE-004 destructive-command warning, opt-in Opus 5 variant, validated `variant_ids` handling)
- **DIAGNOSTIC-C: frozen.** One smoke run could not have its served model independently confirmed from the chat surface — no further DIAGNOSTIC-C execution until model identity for a run can actually be verified, not just assumed from UI selection.
- **DIAGNOSTIC-D (Opus 5 vs Opus 5 + FEF): closed.** 10/10 runs collected (5 scenarios × baseline/FEF), served model confirmed per run, no fallback, `tool_calls: 0` on every run. Semantically correct 10/10. Automatic (lexical) pass 9/10; the one manual-review case was a missing exact required substring ("남아") in an otherwise semantically correct response — a lexical-scorer limitation, not a semantic failure. Hard failures: 0. **No FEF accuracy or conciseness improvement was observed over baseline on this sample**; for simple evidence-judgment tasks a Kernel-only configuration is the recommended default. `diagnostic_only`, not usable as formal promotion evidence. Full writeup: `docs/opus5-diagnostic-findings.md`.
- **DIAGNOSTIC-E (Opus 5 Kernel-only `O5-K` vs Opus 5 + FEF `O5-F`): prepared, not executed.** Design doc: `docs/kernel-vs-fef-experiment.md`. Reuses the existing `v3` corpus unchanged (no new dataset version) via a code-level `O5-K` variant and a repeated-repetitions path added for diagnostic-only plans. 5 scenarios × 2 conditions × 3 repetitions = 30 runs, 10 artifacts, 30 exported copy/paste prompts, `diagnostic_only: true`, `maximum_tool_calls: 0`. Plan and prompt hashes verified consistent; `repository_commit` matches HEAD `3eed56e`. Model responses collected: 0/30 — not yet run. `diagnostic_only`, not usable as formal promotion evidence.
- **Repo-wide review + fixes applied (2026-07-27)**, via 3 parallel review agents (code-reviewer, ponytail-audit, doc-consistency-checker) then direct implementation, all verified against `python -m unittest discover -s tests` (103/103 pass) + all 4 CI validator scripts (`validate_repository.py`, `validate_routes.py`, `run_golden_tests.py --validate-only`, `validate_fable_benchmark.py --validate-only`):
  - Fixed a real bug in `scripts/preflight_fable_private.py`: `canaries`/`actual_canary_hashes` were unset before use if manifest binding failed early (`UnboundLocalError`, uncaught) — initialized before the first `try`; added regression test `test_malformed_manifest_entry_fails_structured_not_nameerror` (confirmed it reproduces pre-fix via `git stash`).
  - Deleted 6 truly orphaned packs unreferenced anywhere in the repo (confirmed by both the ponytail audit and the doc-consistency check, plus `validate_repository.py`'s own orphan warning): `domains/AI.md`, `domains/Tesla.md`, `modules/ExecutiveSummary.md`, `modules/Meeting.md`, `modules/Presentation.md`, `reviewers/SecurityReviewer.md` (+ regenerated `.claude/agents/` via `scripts/generate_agents.py` to drop the now-stale `security-reviewer.md`). **Kept** `policies/Decision.md` — ponytail flagged it too, but it's named in both `CLAUDE.md`'s and `loading-map.md`'s "Preference Policies" taxonomy, just with no Task Map row yet; deleting it would desync that list, so it was restored.
  - Reconciled `docs/loading-map.md` vs `config/routes.json` domain coverage: added `domains/EnterpriseArchitecture.md` (existed as a file, was in loading-map.md prose but missing from `routes.json`'s global domain list, so it could never actually be keyword-selected) to `routes.json`; added a note documenting that `domains/Ansible.md`/`domains/Satellite.md` are keyword-detected across every route (not row-scoped) since a Task Map cell can't list them without tripping `validate_framework.py`'s 2-domain-per-row limit.
  - Updated `loading-map.md` wording for 3 rows (`Code modification`, `Technical blog post`, `Technical research brief`) where `routes.json` always includes a reviewer/workflow/policy that the prose called "optional" — picked doc-matches-code over adding unused conditional-loading logic to `routes.json`/`detect_task.py`.
  - Consolidated a duplicated `SHA256` regex (7 files) and `contained(path, root)` path-safety check (5 files) into new `scripts/lib/fable_common.py`, ~120 duplicated lines removed. Left `validate_fable_holdout.py`'s `validate_artifact`/`resolve_bound_file` and `import_fable_response.py`'s differently-shaped `contained_file` un-merged (real but smaller wins, higher risk of behavior drift for the time available).
  - Updated `CHANGELOG.md` Unreleased section for the diagnostic-work commits (`f4cba68`..`356aa14`) that were undocumented, plus this pass.
  - **Not done** (flagged, not silently dropped): no test added for `scripts/sync_kernel.py` or `scripts/lib/routing.py`; the `validate_fable_holdout.py`/`validate_fable_semantic_evidence.py` `resolve_bound_file` duplication; inconsistent try/except file-I/O error handling across ~5 CLI scripts (`score_fable_smoke.py`, `evaluate_fable_gate.py`, `calculate_fable_reliability.py`, `analyze_fable_results.py`, `sync_kernel.py`) that crash with a raw traceback instead of a structured error on corrupt input.
  - **Not committed/pushed** — awaiting user decision.
- Fable benchmark: contract, Golden Tests, framework, and PILOT-A freshness valid; 98 unit tests pass
- Implemented: private holdout v1.1 intake, hash-bound provenance attestation with custodian/attestor role separation, routed plan compiler, shared response/blinding pipeline, lexical/semantic evidence validation, execution preflight, batch audit, declarative private scoring, five-axis evidence-conflict outcome rubric, scenario-level and provenance-stratified OOD statistics, numeric phrase normalization, hash-bound two-rater reliability, placebo analysis, and a final evidence gate that rejects mixed dataset/manifest/provenance evidence
- Diagnostic result: Opus 4.8 and Sonnet 5 were both evidence-faithful on five non-promotional cases; one label-only disagreement was observed
- Promotion status: not ready; offline semantic evidence, independently verified holdout provenance, and two scored batches remain
- Single-operator path: diagnostic comparison may complete without independent provenance; it cannot produce formal GO
- Local diagnostic plan: `DIAGNOSTIC-A` generated under `.local/fable/` with 20 non-promotional runs
- Local prompt handoff: 20 hash-verified copy/paste Markdown files generated; evaluator/canary leakage hits 0
- Constraint: API credentials, paid API use, and local LLM/Ollama are excluded; no semantic gate bypass is permitted
- Ignored user file: `scratch_notion_ai_simple.md` was not modified or committed

## Next Session

0. DIAGNOSTIC-E is prepared but unexecuted (see above) — 0/30 responses collected. Next step is manual execution (Claude.ai, Opus 5, served-model confirmation, `tool_calls: 0`) and import/scoring, following the same procedure used for DIAGNOSTIC-D.
1. Replace or independently verify the current diagnostic holdout provenance.
2. Resolve the semantic-similarity requirement without violating the no-API/no-local-LLM constraint, or keep the benchmark diagnostic-only.
3. Only after private preflight PASS, execute and audit two independent batches, score blinded outputs, calculate reliability/statistics, and run the final evidence gate.

## Notion Log URL

https://app.notion.com/p/398b44a2dd2e81729cb9dab78c31a5e7
