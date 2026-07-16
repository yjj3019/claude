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
