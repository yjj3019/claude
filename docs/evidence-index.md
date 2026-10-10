# Evidence index

Status describes what an artifact can support, not a model's general ability.
Read this optional index when evaluating evidence; it is not an autoload entry.

| Status | Evidence | Scope and limit |
|---|---|---|
| CURRENT mechanical | [Repository validator](../scripts/validate_repository.py), [Golden metadata](../config/golden-tests.json), [coding runner](../scripts/run_golden_test_coding.py) | Structure, route limits, generated-agent sync, fixture checks and answer-overlay gates; no model execution or quality score |
| NOT_RUN manual | [GT003](../tests/GoldenTest-003.md), [GT004](../tests/GoldenTest-004.md) | Synthetic RHEL RCA / OpenShift upgrade evidence, paired inputs and evaluator keys now available; human rubric/model comparisons not executed |
| HISTORICAL diagnostic | [DIAGNOSTIC-D](opus5-diagnostic-findings.md), [earlier result records](../tests/results/) | Dated, narrow observations; no formal promotion or current-model generalization |
| INVALID comparison | [2026-08-04 batch](../tests/results/pack-ablation/batch-2026-08-04.json), [2026-08-05 GT031 batch](../tests/results/pack-ablation/batch-2026-08-05-gt031.json), [protocol warning](pack-ablation-protocol.md) | Repository auto-loading contaminated both arms; raw mechanical numbers do not validate pack-layer conclusions. INVALID remains INVALID |
| DESIGN_ONLY | [Kernel-versus-FEF design](kernel-vs-fef-experiment.md) | Proposed instrument; not an executed experiment or approval to call models |
| HISTORICAL controls | [O-N / S-N notes](../tests/benchmarks/controls/README.md) | Identical neutral text for model-specific controls; associated diagnostic runner removed |
| CURRENT / HISTORICAL/STALE delegation | [Verification](delegation-loop/VERIFICATION.md), [integration](delegation-loop/INTEGRATION.md), [archive manifest](delegation-loop/source-history/manifest.json) | Current static contracts separate from unchanged historical model artifacts. Current live model behavior remains UNVERIFIED; Git bundle preserves source history |

For any new run, record exact commit/input hashes, host/model configuration,
loaded files, command/cwd/exit evidence and the predeclared rubric. Preserve prior
raw evidence and labels. A file's presence or a CI green badge cannot convert a
manual NOT_RUN, historical result, design or INVALID comparison to model PASS.
Licensing/redistribution permission remains unresolved; this index grants no rights.
