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
python scripts/check_fable_leakage.py --candidate candidate.md --reference distillation.md --canary HOLDOUT-CANARY --output .local/fable/leakage/report.json
python -m unittest tests.test_fable_benchmark tests.test_fable_pilot tests.test_fable_pilot_check tests.test_fable_response_import tests.test_fable_model_evidence tests.test_fable_blinding tests.test_fable_scoring
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
- `score_fable_smoke.py` verifies blinded/imported corpus hashes, performs bounded smoke checks, and preserves raw rater ballots separately from append-only adjudication records.
- `check_fable_leakage.py` runs exact-hash, normalized n-gram, deterministic MinHash, and canary checks without an API. It reports semantic similarity as `not_run` unless separate local embedding evidence is produced.
