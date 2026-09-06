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

- `install_pack.py` copies the FEF pack to detected AI host skills directories as `fef-claude/` (stdlib only).
- `measure_load.py` estimates Kernel-only vs per-route UTF-8 load and the full-tree anti-pattern size. Prints a prominent **SIMPLE Q&A COLD-START** line; optional `--fail-over-cold-start` (default 7000 bytes) fails if CLAUDE.md exceeds the structural budget.
- `markdown_sections.py` provides fence-aware `##` parsing for validators and load tools.
