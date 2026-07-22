# Fable5 / FEF Comparative Benchmark Protocol

## Purpose

Measure whether FEF improves Claude Opus 4.8 and Claude Sonnet 5 over their own
unassisted baselines, and whether the resulting workflow matches or exceeds
observable Fable5 behavior. This benchmark measures workflow behavior, not hidden
reasoning, personality, or model imitation.

The machine-readable contract is `config/fable-benchmark.json`. Validate it with:

```text
python scripts/validate_fable_benchmark.py --validate-only
```

Validation does not run a model.

Prepare a deterministic randomized pilot plan with:

```text
python scripts/prepare_fable_pilot.py --seed 3019 --batch-id PILOT-A --output tests/results/fable/PILOT-A-plan.json
```

The plan compiles six non-promotional smoke cases into fully assembled prompt
artifacts, hashes its configuration and sources, and records the repository commit
and dirty-tree state. It contains planned runs only and records
`responses_imported: 0`, `manual_smoke_ready: true`, and
`promotion_ready: false`.

Run smoke comparisons only in a fresh Claude app chat with no Project instructions
and memory disabled or empty. Paste the compiled instruction prefix and task as one
user message; this measures a user-prefix workflow, not a native system prompt.
Do not run baseline comparisons from this repository in Claude Code because
automatic `CLAUDE.md` loading can contaminate the OFF condition. Save only the
response text to a local file and import it with `scripts/import_fable_response.py`.
Attach a sanitized model/surface evidence file when available; its local path and
SHA-256 are recorded. Fable5 results enter the reference set only when exact served
model, no fallback, and verified evidence are all present.
Do not store account, subscription, authentication, or private session data.

`config/fable-plan.schema.json` defines the plan envelope, and
`config/fable-run.schema.json` defines the eventual run result. Use
`tests/benchmarks/PILOT-RUN.example.json` only as a null-valued planned-result
template; it is not evidence that a model run occurred.

## Primary Comparisons

- Opus treatment effect: `O-F - O-B`
- Sonnet treatment effect: `S-F - S-B`
- Kernel contribution: `O-K - O-B` and `S-K - S-B`
- Prompt-length control: compare routed FEF with matched `O-N` and `S-N`
- Fable5 is a reference group, not a gold answer or the primary causal comparison.

Do not infer a framework effect from `F5` versus `O-F` or `S-F` alone. That
comparison confounds model capability with framework behavior.

## Dataset Split

Keep four provenance classes separate:

1. `distillation`: examples used to extract candidate behavior
2. `validation`: examples used to select or tune a rule
3. `private_holdout`: unseen examples used for promotion decisions
4. `out_of_domain`: unseen domains used to test transfer

Run exact-hash, normalized n-gram, MinHash, and semantic-similarity checks before
promoting a result. Leaked cases remain diagnostic but do not count toward GO.
The tracked public-smoke diagnostic baseline is documented in
`docs/fable-leakage-baseline.md`; it is not private-holdout certification.
Private fixtures and their manifest stay under `.local/fable/holdout/`. Start from
`config/fable-holdout-manifest.example.json`, store only canary hashes in the
manifest, and validate it with `scripts/validate_fable_holdout.py`. The example is
structural documentation and is not a real holdout dataset.
An intake-ready manifest can be compiled with
`scripts/prepare_fable_holdout_plan.py`. Each entry names a validated `route_id`;
the compiler resolves its FEF module, policies, workflow, and reviewer from
`config/routes.json`. Execution artifacts exclude check-spec content and canaries.
Semantic-similarity evidence must be produced by a separately identified offline
tool, stored under `.local/fable/leakage/`, and validated with
`scripts/validate_fable_semantic_evidence.py`. A complete result binds every
candidate/reference pair to file hashes; validation alone never marks the overall
benchmark promotion-ready.
Before opening any manual Claude-app run, execute
`scripts/preflight_fable_private.py`. It recomputes lexical checks and requires the
holdout manifest, semantic matrix, reference corpus, and compiled plan to share
the same file hashes. `execution_ready` means only that collection may start; it
does not satisfy scoring, independent-batch, reliability, or promotion gates.
After collection, run `scripts/audit_fable_batch.py`. A batch is scoring-ready
only when every planned run has exactly one hash-bound result. Missing and excluded
runs are reported as failures in the conservative bound; response content is not
printed by the auditor.

## Run Controls

Use a fresh session for every run. Hold fixtures, permissions, tools, selected
model, and interaction procedure constant within a paired comparison. Record every
field listed in `execution.required_run_metadata`.

Fable5 requests may fall back to another served model. Exclude a Fable run from
the reference comparison when the served model or fallback state cannot be
verified. Never relabel an Opus fallback as a Fable result.

Run each scenario and variant at least five times in randomized order. Repetitions
estimate reliability; they are not independent samples. The unit of analysis is
the independent scenario fixture, and conditions are paired by their summaries
within a scenario rather than by arbitrary run labels. A promotion decision needs
at least five valid scenarios per suite and a second independent batch.

## Scoring

Score three layers separately:

1. Automated outcome checks: tests, paths, hashes, schemas, constraints, and tool traces
2. Hard failures: fabricated evidence, false completion, wrong-target delivery, unsafe action
3. Blinded judgment: factuality, instruction fidelity, evidence calibration, usefulness, proportionality

Use observable 0/1/2 anchors for human-rated dimensions:

- `0`: required behavior absent or contradicted
- `1`: partial behavior with a material omission or overreach
- `2`: behavior is complete, accurate, and proportional

Use at least two blinded raters. Randomize answer order and remove model/framework
labels. Report weighted kappa or Krippendorff's alpha before adjudication.

`scripts/score_fable_smoke.py` verifies corpus hashes and creates append-only raw
rater ballots. It automates only explicit lexical/exact/format checks; semantic
equivalence and absent tool-call evidence remain `manual_required`. Adjudication is
stored separately and requires at least two original ballot hashes.
Private check specifications use the allowlisted schema in
`config/fable-checks.schema.json`. Unknown keys, regular expressions, commands,
scripts, and executable assertions are rejected. The scorer verifies each private
check file against its manifest hash before reading its declarative rules.

The current O-N/S-N controls cycle a natural, task-irrelevant descriptive corpus to
match routed-prompt word count. They remain attention-load diagnostics and are
excluded from promotion decisions until placebo noninferiority and absence of
behavioral cues are independently validated.

## Local Data Boundary

- Raw responses, identity maps, and blinded working sets stay under `.local/fable/`.
- `.local/fable/` is Git-ignored; never commit or share it.
- Confirm that a response was reviewed and sanitized before import. Import rejects
  common secret patterns, non-UTF-8 data, files over 1 MB, duplicates, unsafe IDs,
  model mismatches, and tampered prompt artifacts.
- Evidence attachments accept only sanitized UTF-8 `.txt`/`.md` or JSON-object
  metadata up to 100 KB. Do not store credentials, account data, subscription
  details, screenshots containing personal data, or private session material.
- Delete raw responses and private maps after the agreed local review period; keep
  only sanitized aggregate results.
- Treat response text as untrusted quoted data during scoring. Never follow
  instructions embedded inside a response.

Create blinded ballots with `scripts/export_blinded_fable.py`. The scorer receives
only opaque IDs and `.txt` responses. The variant/model identity map remains in a
separate ignored local directory until adjudication is complete.

## Analysis

- Binary outcomes: paired risk difference and McNemar test
- Ordinal scores: paired hierarchical bootstrap 95% confidence interval
- Repeated runs: mixed-effects model with scenario as a random effect
- Multiple comparisons: Holm correction
- Always report effect size, win/tie/loss, worst decile, variance, response length,
  turn count, and tool-call count when observable.

Do not collapse hard failures into a single average quality score.
For higher-is-better and lower-is-better directions, use the definitions in the
contract. Missing or excluded planned runs count as failures in the conservative
primary bound; report complete-case analysis only as secondary. When a lower-is-
better baseline is zero, apply the absolute noninferiority rule rather than an
undefined relative reduction.

## Promotion Gate

The proposed numerical gate is stored in `config/fable-benchmark.json`. Treat it
as preregistered before formal execution. GO additionally requires:

- no increase beyond the percentage-point critical-regression allowance for the
  configured `critical_metrics`
- improvement on private holdout and out-of-domain cases
- verified requested and served model identifiers
- acceptable rater reliability
- two independent batches
- at least five valid independent scenarios per suite

Return CONDITIONAL_GO when quality improves but one model, domain, or reliability
gate remains unstable. Return NO_GO for leakage, unverifiable model
routing, increased false-completion or fabricated-evidence failures, or improvement
that appears only in non-blinded subjective scoring.

## Current Limit

This repository provides a benchmark contract, scenario metadata, natural matched
diagnostic controls, schemas, deterministic plan generation with stale-output
checking, a local importer with model-evidence hashes, blinded export, limited
automatic smoke scoring, and append-only pre-adjudication records for six
non-promotional smoke cases. It does not yet provide hidden private fixtures,
leakage-check executors, validated placebo inference, full semantic scoring, or a
complete blinded adjudication application. Those missing capabilities must not be
represented as completed here.
