# FAQ

## Does FEF make Claude smarter?

FEF aims to support consistency, calibration and output discipline. Static tests do not establish improved model ability; inspect the dated evidence and its limits.

## Does FEF replace web research?

No. It encourages evidence-based work but does not create evidence.

## Should every module always be loaded?

No. Load only relevant modules.

## Should the kernel grow?

Rarely. Most improvements belong in policies or modules.

## How do I try a complete task without real operations data?

Use the [synthetic examples](https://github.com/yjj3019/claude/blob/main/docs/Examples.md):
input → selected packs → output → evaluator criteria. GT003 supplies a RHEL RCA;
GT004 supplies an OpenShift upgrade-impact decision. Neither requires cluster
access or changes. Metadata checks verify availability, not report/model quality.

## What happens when I replace an installed FEF pack?

Default conflicts refuse and identical verified payloads skip without writes.
`--force` validates a stage before renaming the original into a hidden recovery
folder, then publishes and verifies the new pack. Ordinary publish failures
restore the original; a failed rollback reports the retained original's exact
path. Successful force replacements also retain that backup. See
[installation and recovery](Installation.md); avoid concurrent installers.

## Where should reviewer guidance be edited?

Edit `reviewers/TechnicalReviewer.md` (or another source in the reviewers directory), then run `python scripts/generate_agents.py` and
`python scripts/validate_repository.py` from the clone root. Inspect generated
`.claude/agents/` changes; keep the single read-only review contract and the
existing tools/model/turn limits. Editing only generated copies creates drift.

## Which evidence is current?

The [evidence index](https://github.com/yjj3019/claude/blob/main/docs/evidence-index.md)
separates mechanical checks, NOT_RUN manual exercises, historical diagnostics,
INVALID comparisons and design-only documents. O-N/S-N are identical historical
neutral controls, not different active model instructions. No label authorizes
paid execution or upgrades an old result to current PASS.
