# Examples

These exercises use fabricated evidence only. Read the input before choosing
packs; a route preview and a written report do not execute infrastructure actions.
The inlined Kernel is the entry, with no second copy or full-pack preload.

## RHEL incident RCA (GT003)

| Step | Concrete example |
|---|---|
| Input | [GT003 evidence](../tests/fixtures/GT003-evidence.md): demo-api terminates at a 512 MiB cgroup limit while host memory remains available |
| Select | `modules/RCA.md`, `domains/RHEL.md`, `workflows/RCAWorkflow.md`, `reviewers/TechnicalReviewer.md`; Evidence, Thinking and Review policies. RHEL already subsumes Linux |
| Output | Short RCA with E1–E4-linked timeline, observed 75-second probe outage, likely memcg limit exhaustion, unknown cause of growth, alternatives and non-executed next checks |
| Verify | [Evaluator key](../tests/fixtures/GT003-answer-key.md): no invented leak/deployment/data-loss claim, host-versus-unit distinction preserved, critical-failure gate and eight anchored dimensions |

From the clone root:

```sh
python scripts/detect_task.py --task "RHEL incident RCA"
python scripts/run_golden_tests.py --validate-only
```

Use the [paired prompts](../tests/prompts/GT003-baseline.md) in isolated contexts
for a separately authorized comparison. The metadata check does not grade an RCA.

## OpenShift upgrade impact (GT004)

| Step | Concrete example |
|---|---|
| Input | [GT004 evidence](../tests/fixtures/GT004-evidence.md): Upgradeable=False, network degraded, disruptionsAllowed=0, inventory/vendor evidence missing |
| Select | `modules/Research.md`, `domains/OpenShift.md`; Evidence, Freshness and Calibration policies. No separate workflow/reviewer; no Kubernetes duplicate |
| Output | Release-impact brief recommending a hold, with blockers, evidence gaps and ordered read-only readiness checks |
| Verify | [Evaluator key](../tests/fixtures/GT004-answer-key.md): no forced upgrade, PDB bypass, invented official support/upgrade edge, acknowledgment or claimed execution |

```sh
python scripts/detect_task.py --task "OpenShift release impact research"
python scripts/run_golden_tests.py --validate-only
```

Supplied release numbers are fictional lab inputs, not current product guidance.
Both exercises are manual **NOT_RUN** comparisons. See the
[evidence index](evidence-index.md) for current versus historical evidence.

## Prompt review

Input: a draft prompt and explicit outcome/constraints. Select
`modules/PromptEngineering.md`, `reviewers/PromptReviewer.md`, Thinking and Review
policies; add Evidence only for external factual claims. Output: findings plus a
revised draft. Verify each accepted change against the stated constraints, once;
missing caller evidence stays a validation gap.
