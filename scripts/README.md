# Harness Scripts

All scripts use the Python standard library.

```powershell
python scripts/detect_task.py --task "RHEL 장애 RCA를 작성해줘"
python scripts/validate_routes.py
python scripts/validate_repository.py
python scripts/run_golden_tests.py --validate-only
python -m unittest tests/test_harness.py
```

- `detect_task.py` returns a deterministic candidate route as JSON. It is advisory and does not replace model judgment.
- `validate_routes.py` checks route IDs, Pack paths, and load limits.
- `validate_repository.py` runs structural, routing, Golden Test, orphan-Pack, and version/tag checks. Ambiguous maintenance findings are warnings.
- `run_golden_tests.py --validate-only` checks test metadata, fixtures, and scorecard schema without calling Claude or another API. Use `--output <path>` to save its JSON summary.


## Install and measure

```powershell
python scripts/install_pack.py --auto
python scripts/install_pack.py --print-claude
python scripts/measure_load.py
python scripts/sync_kernel.py --check
```

- `install_pack.py` copies the FEF pack to detected AI host skills directories as `fef-claude/`; sibling git repo skill roots require explicit opt-in (stdlib only). See `--print-bootstrap`.
- `measure_load.py` estimates Kernel-only vs per-route UTF-8 load and the full-tree anti-pattern size. Prints a prominent **SIMPLE Q&A COLD-START** line; optional `--fail-over-cold-start` (default 7000 bytes) fails if CLAUDE.md exceeds the structural budget.
- `markdown_sections.py` provides fence-aware `##` parsing for validators and load tools.

## Delegation tooling

- `install_pack.py --pack ai-delegation-loop --dest /path/to/skills`: separate opt-in install at the same skills root as FEF; `--check`, `--force`, `--dry-run` supported.
- `delegation/install.py install --target claude codex --scope user`: explicit tool paths; project scope requires `--project-dir`.
- `delegation/install.py package --output /path/to/package.zip`: reproducible ZIP, refuses existing output unless `--force`.
- Delegation installation and ZIP default to operational files plus acceptance guidance. Optional `--with-evidence` includes the preserved test runners/reports/JSON. The canonical Git package and history archive stay complete; local runtime links remain valid in both projections.
- `delegation/validate_skill.py`: scoped format, links, JSON, evidence hashes, version, leak and entry-file validation. Root FEF validation remains separate.
- `python -m unittest discover -s scripts/delegation -p "test_*.py"`: minimal package fixtures and isolated temporary HOME.
- `delegation/refresh_evidence.py --check`: reruns static prompt contracts, isolated playbook fixtures and the oracle grader without model execution; verifies current records and preserves historical v1.2 model artifacts. Omit `--check` to regenerate only deterministic current evidence after changes.
- `python skills/ai-delegation-loop/tests/run_simulation.py --output ./sim --self-check`: grader only, no CLI/model usage. Full simulations and native probes need separate authority and model access.

## Validation coverage and safe FEF replacement

`validate_repository.py` already invokes route and Golden metadata validation;
CI runs those checks once through that entry. Their individual CLIs remain useful
for targeted diagnostics.

FEF `--force` uses a verified stage, retained original, replacement verification
and rollback. See [recovery procedure](../docs/Installation.md). Installer tests
cover temporary HOME, source/destination links and overlap, manifests, mutation,
copy/rename/verification failures, rollback recovery and no-write identical/dry
runs. Windows CI separately exercises real junctions; OS/Python coverage remains.
