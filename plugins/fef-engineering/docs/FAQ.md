# TaskForge for Claude — FAQ

<a id="does-fef-make-claude-smarter"></a>

## Does TaskForge for Claude make Claude smarter?

No. It supplies task guidance and verification reminders. Effects on consistency,
calibration, quality and cost depend on the workload and must be measured.

<a id="does-fef-replace-web-research"></a>

## Does TaskForge for Claude replace web research?

No. It encourages evidence-based work but does not create evidence.

## Should every module always be loaded?

No. Load only relevant modules.

## Should the kernel grow?

Rarely. Most improvements belong in policies or modules.

<a id="what-happens-when-i-replace-an-installed-fef-pack"></a>

## What happens when I replace an installed pack?

Default conflicts refuse and identical verified payloads skip without writes.
`--force` validates a stage before renaming the original into a hidden recovery
folder, then publishes and verifies the new pack. Ordinary publish failures
restore the original; a failed rollback reports the retained original's exact
path. Successful force replacements also retain that backup. See
[installation and recovery](Installation.md); avoid concurrent installers.
