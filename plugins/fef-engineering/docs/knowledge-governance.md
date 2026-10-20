# Knowledge Governance

Use this guide when maintaining a knowledge base, operational runbook, configuration reference, agent inventory, or reusable setup instructions.

## One Subject, One Owner

- Assign each reusable fact or executable setting to one owning document before recording it.
- Keep the authoritative value, schema, or procedure only in that document. Other documents may summarize it in one line and link to the owner.
- Treat duplicated executable configuration as drift, not as a precedence problem. Remove the duplicate instead of choosing whichever copy appears first.
- When ownership changes, name the successor and update inbound references.

## Knowledge Status

Label operational knowledge so search and retrieval cannot silently promote stale instructions:

- `Canonical`: current verified default
- `Operational`: verified only in the named environment
- `Project-specific`: do not copy into general configuration
- `Historical`: preserve evidence; do not execute
- `Replaced`: follow the named successor
- `Draft`: require deployment and smoke testing
- `Snapshot`: re-check current state before use

Historical and Replaced pages may retain failed commands or obsolete settings as evidence, but must place the non-executable status before those examples.

## Design Versus Observed State

- Keep design intent separate from observed deployment state.
- Record observations with environment, scope, date, and the command or artifact used to verify them.
- When design and deployment differ, report both; direct observation controls claims about what is installed or active.
- Do not promote a Draft to Operational merely because its specification is complete. Verify deployment and run the smallest representative smoke test.

## Runtime Modifier Inventory

Before concluding that a setting, prompt, or hook is active or inactive, inspect every applicable behavior layer:

- repository and global instruction files
- environment variables and settings
- agent or skill frontmatter
- plugins and their bundled hooks
- external workflow or automation triggers

An empty settings section does not prove the behavior is absent when a plugin or another scope can inject it.

## Portability and Executable Examples

- Name the supported host, runtime, scope, and required tool surface for environment-specific instructions.
- Use placeholders for user names and paths unless the literal value is intentionally project-specific.
- Validate configuration keys, tool identifiers, frontmatter, and file layout against the target runtime before publishing a copyable example.
- Verify that referenced agents, skills, scripts, and directories exist in the named scope.
- Before adopting an external skill or plugin, review source ownership, maintenance activity, license, requested permissions, external communication, secret handling, and prompt-injection exposure; smoke-test it in isolation and record its version and removal path.
- On Windows PowerShell 5.1, ship scripts as ASCII when practical or UTF-8 with BOM when non-ASCII text is required; test the exact `-File` invocation.

## Update Procedure

1. Identify the subject owner and current status.
2. Fetch or read the owner plus every document that repeats the same executable value.
3. Compare design intent with directly observed state.
4. Inventory hidden runtime modifiers relevant to the claim.
5. Update the owner, replace duplicates with references, and preserve superseded evidence under Historical or Replaced status.
6. Re-read the changed records and run a representative smoke test before claiming Operational status.
