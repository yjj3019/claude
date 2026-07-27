# Project Progress

## Current Status

- Updated: 2026-07-24 KST
- Branch: `main`
- Remote state: pushed through `356aa14`; copy/paste diagnostic prompt export pending verification and push
- **STILL PAUSED**: the DIAGNOSTIC-B safety-guardrail task below (`maximum_tool_calls: 0` in v2 `checks.json`, offline-evidence prompt preamble, PRIVATE-004 tool-session ban, manifest/plan/prompt regen, new tool-call tests) was never resumed — a separate repo-wide improvement pass (below) was done first. The read-only Explore agent's DIAGNOSTIC-B findings are still unconsumed.
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

0. **Resume DIAGNOSTIC-B safety hardening first** (interrupted 2026-07-24): re-run/re-check the Explore agent's findings on v2 `checks.json` locations, the DIAGNOSTIC-B generator, manifest-hash script, and Fable test suite, then apply the 8-point change list from the user's request (constraints block, offline-evidence prompt preamble, PRIVATE-004 tool-session ban, manifest regen + plan/prompt regen, new tool-call tests, full Fable test + hash verification) — no model/MCP execution, no commit/push per user instruction.
1. Replace or independently verify the current diagnostic holdout provenance.
2. Resolve the semantic-similarity requirement without violating the no-API/no-local-LLM constraint, or keep the benchmark diagnostic-only.
3. Only after private preflight PASS, execute and audit two independent batches, score blinded outputs, calculate reliability/statistics, and run the final evidence gate.

## Notion Log URL

https://app.notion.com/p/398b44a2dd2e81729cb9dab78c31a5e7
