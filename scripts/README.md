# Harness Scripts

All scripts use the Python standard library.

```powershell
python scripts/detect_task.py --task "RHEL 장애 RCA를 작성해줘"
python scripts/validate_routes.py
python scripts/validate_repository.py
python scripts/run_golden_tests.py --validate-only
python -m unittest tests/test_harness.py
python scripts/validate_fable_benchmark.py --validate-only
python scripts/prepare_fable_pilot.py --seed 3019 --batch-id PILOT-A --output tests/results/fable/PILOT-A-plan.json
python scripts/prepare_fable_pilot.py --output tests/results/fable/PILOT-A-plan.json --check
python scripts/import_fable_response.py --plan tests/results/fable/PILOT-A-plan.json --package-dir tests/results/fable/PILOT-A-package --run-id PILOT-A-PB001-O-F-R01 --response-file response.md --served-model claude-opus-4-8 --fallback no --source-surface claude_app --confirm-sanitized
python scripts/export_blinded_fable.py --import-dir .local/fable/imported --blinded-dir .local/fable/blinded/PILOT-A --mapping-path .local/fable/private/PILOT-A-map.json --seed 3019
python scripts/score_fable_smoke.py --help
python scripts/score_fable_smoke.py score --corpus-dir .local/fable/blinded/PRIVATE-A --check-manifest .local/fable/holdout/manifest.json --output .local/fable/scores/PRIVATE-A.json
python scripts/check_fable_leakage.py --candidate candidate.md --reference distillation.md --canary HOLDOUT-CANARY --output .local/fable/leakage/report.json
python scripts/validate_fable_holdout.py --manifest .local/fable/holdout/manifest.json
python scripts/prepare_fable_holdout_plan.py --manifest .local/fable/holdout/manifest.json --output .local/fable/holdout/plans/PRIVATE-A.json --batch-id PRIVATE-A --seed 3019
python scripts/validate_fable_semantic_evidence.py --evidence .local/fable/leakage/semantic.json
python scripts/preflight_fable_private.py --manifest .local/fable/holdout/manifest.json --lexical-evidence .local/fable/leakage/lexical.json --semantic-evidence .local/fable/leakage/semantic.json --plan .local/fable/holdout/plans/PRIVATE-A.json --canary-file .local/fable/holdout/canaries.txt
python scripts/audit_fable_batch.py --plan .local/fable/holdout/plans/PRIVATE-A.json --import-dir .local/fable/imported/PRIVATE-A
python scripts/analyze_fable_results.py --input .local/fable/analysis/scenario-results.json --output .local/fable/analysis/statistics.json --seed 3019
python scripts/calculate_fable_reliability.py --ballot .local/fable/ballots/RATER-1.json --ballot .local/fable/ballots/RATER-2.json --output .local/fable/analysis/reliability.json
python scripts/evaluate_fable_gate.py --analysis .local/fable/analysis/statistics.json --reliability .local/fable/analysis/reliability.json --preflight .local/fable/analysis/preflight.json --batch-audit .local/fable/analysis/PRIVATE-A-audit.json --batch-audit .local/fable/analysis/PRIVATE-B-audit.json --output .local/fable/analysis/final-gate.json
python scripts/audit_fable_batch.py --plan .local/fable/holdout/plans/PRIVATE-A.json --import-dir .local/fable/imported/PRIVATE-A
python -m unittest tests.test_fable_benchmark tests.test_fable_pilot tests.test_fable_pilot_check tests.test_fable_response_import tests.test_fable_model_evidence tests.test_fable_blinding tests.test_fable_scoring tests.test_fable_reliability
```

- `detect_task.py` returns a deterministic candidate route as JSON. It is advisory and does not replace model judgment.
- `validate_routes.py` checks route IDs, Pack paths, and load limits.
- `validate_repository.py` runs structural, routing, Golden Test, orphan-Pack, and version/tag checks. Ambiguous maintenance findings are warnings.
- `run_golden_tests.py --validate-only` checks test metadata, fixtures, and scorecard schema without calling Claude or another API. Use `--output <path>` to save its JSON summary.
- `validate_fable_benchmark.py --validate-only` validates the Fable/FEF comparison contract and prompt-source paths without running a model.
- `prepare_fable_pilot.py` creates a seeded, randomized manual execution plan and hashes the benchmark config, repository commit, prompt sources, and compiled artifacts.
- `prepare_fable_pilot.py --check` regenerates the plan/package and fails when checked-in artifacts are stale; commit/dirty checkout metadata alone is normalized.
- `import_fable_response.py` imports a sanitized response captured manually from the fixed Claude app smoke-test surface. It stores the response, minimal run metadata, integrity hashes, and optional sanitized surface/model evidence hash under the Git-ignored local benchmark tree.
- `export_blinded_fable.py` creates a model/variant-free local ballot and stores the identity map separately under the ignored `.local/fable/` tree.
- `score_fable_smoke.py` verifies blinded/imported corpus hashes and private check hashes, evaluates only allowlisted declarative rules, and preserves raw rater ballots separately from append-only adjudication records. It never executes check or response content.
- `check_fable_leakage.py` runs exact-hash, normalized n-gram, deterministic MinHash, and canary checks without an API. It reports semantic similarity as `not_run` unless separate local embedding evidence is produced.
- `validate_fable_holdout.py` validates local-only holdout provenance, hashes, containment, canary hashes, and minimum independent scenario counts without printing fixture content.
- `prepare_fable_holdout_plan.py` compiles only intake-ready local holdouts into manual Claude-app execution artifacts. It resolves routed FEF sources from `config/routes.json` and excludes evaluator checks and canaries from the execution package.
- `validate_fable_semantic_evidence.py` verifies that offline semantic-similarity results are hash-bound to every candidate/reference pair and remain below the preregistered threshold. It validates evidence; it does not generate similarity scores.
- `preflight_fable_private.py` permits manual execution only when holdout intake, recomputed lexical leakage checks, semantic evidence, and every compiled artifact bind to the same private corpus. Execution readiness never implies promotion readiness.
- `audit_fable_batch.py` audits planned-versus-imported run coverage, metadata and response hashes, exclusions, and conservative missing-as-failure bounds without printing response content.
- `analyze_fable_results.py` calculates scenario-level paired effects, hierarchical scenario bootstrap intervals, exact McNemar results when summaries remain binary, and Holm-adjusted p-values. Repetitions and batches are not counted as independent scenarios.
- `calculate_fable_reliability.py` validates two blinded ordinal ballots and reports hash-bound quadratic weighted Cohen's kappa against the configured reliability gate.
- `evaluate_fable_gate.py` combines hash-recorded quality, reliability, private-preflight, and distinct-batch evidence. Failed required evidence returns `NO_GO`; missing placebo evidence limits the verdict to `CONDITIONAL_GO`.
