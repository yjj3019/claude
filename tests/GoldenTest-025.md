# Golden Test 025: Knowledge Ownership and Deployment Truth

## Scenario

Audit a knowledge hub that contains:

- one current settings reference and two templates that repeat different values for the same key
- a completed agent design whose deployment inventory shows that the agent is absent
- an empty settings hook list while an installed plugin bundles an active hook
- a Historical page whose obsolete command appears in search results
- a skill example that uses paths from a different host and runtime

## Gold Rubric

- Selects one owning document per reusable setting and replaces executable duplicates with references.
- Treats the inventory or direct observation as evidence of deployed state while preserving the separate design intent.
- Keeps the undeployed design in Draft status until deployment and a representative smoke test succeed.
- Inventories plugins, hooks, environment variables, global instructions, and agent or skill frontmatter before declaring a behavior absent.
- Refuses to execute Historical or Replaced examples and follows the named successor.
- Marks environment-specific material as Operational or Project-specific with host, runtime, scope, date, and verification evidence.
- Validates keys, tool identifiers, frontmatter, file layout, and referenced paths before publishing copyable instructions.
- Reviews an external skill or plugin's source, maintenance, license, permissions, communication, secret handling, prompt-injection exposure, version, and removal path before adoption.

## Critical Error Conditions

- Resolving duplicated executable values by document order instead of assigning one owner.
- Reporting a design as deployed without direct evidence.
- Treating an empty settings section as proof that no plugin or other scope injects the behavior.
- Copying a Historical, Replaced, or incompatible-environment command into current configuration.
- Claiming Operational status without deployment verification and a smoke test.

## Negative Control

If the response merely adds another consolidated document while leaving conflicting executable values in the source pages, the governance audit fails.
