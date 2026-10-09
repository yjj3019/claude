# Delegation optimization — 2026-10-09

## Prompt contracts

The [official Claude prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) supports explicit outputs/context, distinct instructions and reference material, bounded autonomy and general solutions rather than fixture-specific shortcuts. The [evaluation guide](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) supports measurable criteria. We adapted these general principles into persisted output contracts, standalone untrusted-data boundaries, criterion integrity and original/other-input regression rules. This is an application to this workflow, not measured cross-model prompting performance. Claude-specific model/effort settings and reasoning-output requests were not introduced.

The acceptance tests check written contracts, missing-field mutations, isolated generated-playbook files and synthetic policy oracles. A 450-character fixture still fails its original 400-character limit; a documented human-confirmed criterion correction is recorded separately. These checks do not demonstrate model adherence or actual prompt injection defense. Current model behavior remains UNVERIFIED.

## Reduced work without deleting recovery evidence

- Default delegation install/ZIP contains operational documents, prompts, templates, platform metadata and the acceptance checklist. Historical/model JSON, reports and developer runners remain byte-preserved in canonical Git; optional `--with-evidence` ships them. Runtime links are independently checked. Updating a previous full install requires explicit force with a backup.
- Installer source lists/hashes are reused within one call for comparison and diff reporting. Fresh source checks still run after copying and after promotion. Stage/destination hashes remain independent. Source drift, conflicts, no-write behavior and Windows reparse boundaries are regression-tested.
- The validator inventories package/tooling/doc/workflow paths once per command. Direct helper calls still discover current files. All format, JSON, link, leak and evidence guards remain.
- CI removed its second standalone grader invocation. `refresh_evidence.py --check` still executes and checks the grader; a failing grader blocks evidence verification. The workflow gate is covered by tests. Stored ZIP encoding remains fixed for cross-platform byte identity.

## Measurement scope

Measurements use the same Windows host and Python 3.14, isolated HOME, warm local filesystem, and three validator subprocess samples. Install/force measurements are exploratory single samples with operation counts. Token values are rough UTF-8-byte/4 estimates, not tokenizer output. Root FEF entry files stay unchanged. Timing is sensitive to host load; suite duration changes also include added test coverage. Model quality and response latency were not measured.

Local data and source fingerprints are preserved in [optimization-metrics.json](optimization-metrics.json). The before sample is commit `0163af554b3576924b8db247b5259ee03355d377`; the after sample is the v1.3 working tree with recorded source fingerprints. Exact-head CI/fresh checkout outcomes are recorded on the PR.

| Measurement | Before | After | Interpretation |
| --- | ---: | ---: | --- |
| Delegation installed files | 23 | 14 | Experimental files excluded from default; preserved in Git |
| Delegation installed bytes | 239,215 | 62,892 | 73.7% smaller than prior full default |
| Complete canonical package bytes | 239,215 | 246,262 | Added contracts/evidence remain in repository |
| Force source hash passes | 4 | 3 | Source-change and independent stage/destination checks retained |
| Force source inventory passes | 7 | 3 | Per-call reuse, no persistent stale cache |
| Validator command inventories | 3 | 1 | Direct helpers remain fresh |
| CI grader invocations per matrix job | 2 | 1 | Same grader gate retained through evidence check |
| FEF installed files, including 3 generated | 94 | 94 | History was already excluded |
| FEF installed worktree bytes | 307,873 | 308,940 | Small CLI/docs increase, not a reduction |
| FEF normalized LF entry bytes / estimated tokens | 4,558 / ~1,140 | 4,558 / ~1,140 | AGENTS + CLAUDE unchanged |
| Delegation entry bytes / estimated tokens | 5,347 / ~1,337 | 5,847 / ~1,462 | Required contract added; supporting files selected on demand |
| Delegation install, one sample | 1.203s | 0.978s | Exploratory, not a general latency guarantee |
| Force install, one sample | 1.137s | 0.153s | Different payload sizes, not a model benchmark |
| Validator median, three samples | 0.910s | 0.776s | Same host/command/Python; host-load variability remains |
| Delegation suite | 35 / 79.265s | 49 / 51.935s | Different coverage/contention; do not infer speed gain |

The full pre-change FEF 152-test rerun took 846.302s on Windows. Final-head CI reruns the complete configured suite; CI timings cannot be directly compared with local Windows timings.

## Decisions retained

FEF already excludes the source-history directory from installation and already has a compact/selective Kernel. Delegation fixtures were already minimal. These are retained protections, not new performance gains. Routing/config-import changes were not adopted without isolated evidence of useful impact. No large feature, approval rule, verification guard or provenance archive was deleted to pursue a speed claim.
