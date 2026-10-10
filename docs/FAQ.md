# FAQ

## Does FEF make Claude smarter?

No. It improves consistency, calibration, and output discipline.

## Does FEF replace web research?

No. It encourages evidence-based work but does not create evidence.

## Should every module always be loaded?

No. Load only relevant modules.

## Should the kernel grow?

Rarely. Most improvements belong in policies or modules.

## What happens when I replace an installed FEF pack?

Default conflicts refuse and identical verified payloads skip without writes.
`--force` validates a stage before renaming the original into a hidden recovery
folder, then publishes and verifies the new pack. Ordinary publish failures
restore the original; a failed rollback reports the retained original's exact
path. Successful force replacements also retain that backup. See
[installation and recovery](Installation.md); avoid concurrent installers.
