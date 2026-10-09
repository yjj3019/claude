# Integration verification — 2026-10-09

## v1.2.1 semantic corrections

Current prompt fixes cover standalone interview frontmatter, proof-before-rerun order, approval for each rerun's external effects including payments/permission changes, permanent validation/stop/approval instructions in generated SKILL files, and multiple/external cause classification. Eight deterministic acceptance tests exercise those document contracts and isolated generated-playbook fixtures. They do not establish model adherence.

`tests/evidence-status.json` separates unchanged original v1.2 model artifacts (HISTORICAL/STALE_FOR_CURRENT_PACKAGE) from the new current hash records and deterministic `acceptance-results.json`. The original report is preserved as `simulation-report.v1.2.ko.md`. `integration-manifest.json` explicitly identifies nine modified original package files and nine unchanged originals; the full original package remains recoverable from the unchanged Git bundle. `refresh_evidence.py --check` reproduces current records without writing and without model CLI calls. Current hash drift, historical artifact tampering and fresh model claims are regression-tested failures.

Current local validation passed all 35 delegation tests (two Windows symlink privilege skips), the evidence regeneration check, offline history restoration and FEF repository/routes/golden validation. Current model behavior and Codex auxiliary reads remain UNVERIFIED. Full final-head CI results are reported on the draft PR. The older pre-publication counts below describe the initial integration; current additional acceptance/guard checks are separate.

## Initial integration baseline

Pre-publication local checks ran on Windows with Python 3.14. Actual user HOME installation, authenticated/paid model CLIs, credentials, source remote changes, merge and deletion were not performed.

| Check | Result |
| --- | --- |
| FEF validate_repository.py, validate_routes.py, run_golden_tests.py --validate-only | PASS; 31 Golden Tests, 10 routes; 4558-byte root cold start |
| FEF unittest discover | PASS: 152 tests; 2 Windows symlink privilege skips |
| FEF installation regression after document link repair | PASS: 51 tests; 2 Windows symlink privilege skips |
| Existing FEF CI run commands | PASS: routing, isolated install/check, all 9 coding answer fixtures, expected failing GT012 negative control |
| Delegation validator | PASS: frontmatter/size/links/JSON/evidence hashes/version/leak patterns/openai.yaml/root entry existence |
| Delegation unittest discover | PASS: 25 tests; 2 Windows symlink privilege skips; real Windows junction refusal and mocked ancestry guard pass |
| Installer | PASS: isolated HOME, exact/idempotent copy, conflict refusal, force backup, no-write dry-run, project argument guards, explicit sibling pack preservation |
| Reproducible ZIP | PASS: equal bytes, fixed timestamps/creator-platform metadata, stored payloads avoiding zlib-version drift, correct top-level directory, cache exclusion, overwrite refusal |
| Simulation grader self-check | PASS; no model execution, historical results untouched |
| History | PASS: SHA-256, mirror restore, fsck, refs, 5 commits/26 trees/42 blobs, all source main/optimized file bytes; no pattern hits in reachable blobs |
| Protected root files | AGENTS.md, CLAUDE.md, LICENSE and original FEF workflow unchanged |

FEF retains its pre-existing advisory warning for `workflows/CodingWorkflow.md`. Existing historical simulation/native evidence is preserved; Codex auxiliary prompt reads remain UNVERIFIED. No new all-platform real-system verification is claimed.

The delegation workflow restores the archive and runs validation, script tests and the grader on Ubuntu/Windows with Python 3.11/3.14. Existing FEF CI remains unchanged (Ubuntu, Python 3.11/3.12/3.14). Exact remote commit checks and a standalone fresh target clone are checked after publication and reported on the draft PR; they are distinct from this pre-publication record.
