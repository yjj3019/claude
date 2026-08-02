# Golden Test Coverage

Generated conceptually from `config/golden-tests.json`; IDs show existing coverage, not model-run pass status.

| Workflow | General | RHEL | OpenShift | Proposal | RCA | Research | Coding |
|---|---|---|---|---|---|---|---|
| Analysis | GT009, GT018, GT022 | — | GT004 | — | — | GT006, GT009, GT018 | — |
| Writing | GT002, GT006, GT010, GT016, GT020, GT021 | GT001 | — | GT001 | — | GT006, GT010 | — |
| Review | GT005, GT007, GT008, GT015, GT019 | — | — | GT011 | — | — | — |
| Troubleshooting | GT017 | — | — | — | GT003 | — | — |
| Coding change | — | — | — | — | — | — | GT012, GT013, GT014 |

Largest gaps: domain-specific RHEL fact verification beyond proposals, OpenShift writing/review, and existing-failure repository handling. Add tests only after a repeated failure is documented and a measurable rubric exists.

## Mechanical Runner for Fixture-Mode Coding Tests

`scripts/run_golden_test_coding.py` mechanically scores the three fixture-mode coding tests (012-014): unit-test pass/fail, expected-fix-file coverage vs sibling-only workarounds, test-file tampering, and new-dependency candidates. Executable answer files live in each fixture's `answers/` directory; CI runs the answer overlays as a positive gate (must exit 0) and the pristine buggy file as a negative control (must exit 1). Rubric dimensions beyond these mechanical checks still require a human or LLM reviewer, and a single mechanical pass is not the GoldenTest PASS rule.
