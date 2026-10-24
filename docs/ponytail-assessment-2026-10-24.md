# Ponytail assessment — 2026-10-24

## Scope and decision

Reference: [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail/tree/09c434ab73ca43761c5d8b0c5d341926c2fba710),
revision `09c434ab73ca43761c5d8b0c5d341926c2fba710`, package/plugin `5.3.2`.
Inspected 161 tracked regular text files (971,898 bytes) extracted from a no-checkout
clone. This is static source analysis: upstream installers, hooks, tests, UI and
model benchmarks were not executed. Symlinks and binary contents were not extracted.

Adopt three small, independently worded improvements in existing TaskForge surfaces:

- Compare project abstractions, standard-library/platform features and installed
  dependencies before custom implementation or a new dependency; preserve required
  behavior, compatibility, security and accessibility.
- Follow connected execution/failure paths during review. Connect confirmed findings
  to a triggering case, observable impact and a compatible fix; label missing evidence.
- Compare candidates with matched tools/permissions/wrappers and cache conditions,
  explicit failure denominators and retained raw results.

The existing minimum-change and change-owned cleanup rules already cover much of
Ponytail's instruction value. No separate skill, mode, dependency, debt parser,
dashboard, webhook or persistent ledger is added. The assessment itself is not
included in generated runtime payloads. Coding becomes `1.0.2`, plugin `2.0.2`;
IDs, routing, authorization, reviewer output headings and state v1 are preserved.

## Upstream findings

These findings concern upstream code, not defects imported into TaskForge. Concrete
source paths establish the conditions below; no upstream runtime incident is claimed.

### P2 — CSV updates split quoted multi-line records

[csvField and upsertCsv](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/hooks/band/metrics.ts#L282)
quote task names containing newlines, but updates split the existing CSV on physical
newlines. Updating the same key for a name such as `first\nsecond` removes the first
physical line while retaining the continuation, leaving malformed/orphan data.
The board's logical CSV parser cannot restore the removed prefix. Parse logical
records before replacement and serialize them again; add same-key multiline tests.
Existing ordinary/comma-name tests do not cover this case. Runtime reproduction remains open.

### P2 — Shared ledger read/modify/write can lose history

[record](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/hooks/band/register.tsx#L138)
reads the project CSV and writes a whole updated file without coordination in this
path. Two same-project sessions reading the same old contents can overwrite each
other's new row. The read catch also maps every read failure to an empty ledger;
a later successful write can replace history after a non-ENOENT read failure.
Distinguish absence from read failure and coordinate updates or store session rows
separately. Atomic replacement alone does not resolve stale read/modify/write.
Host scheduling and filesystem behavior were not exercised, so live incidence is unverified.

### P2 — Benchmark summaries use inconsistent error denominators

[compare.py](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/benchmarks/agentic/compare.py#L19)
returns no pass value for cells missing `correct`, and aggregation filters missing
values. [run.py](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/benchmarks/agentic/run.py#L394)
counts errored cells as failures in its aggregate denominator. One successful cell
and one crashed cell without `correct` therefore yield a pass rate of 100% versus
a correctness rate of 50% (if the successful cell is also safe). Answer-judge rows
are intentionally distinct and should not be reclassified as crashed result cells.
Unify failure policy and show eligible/failed/missing denominators. There is no
evidence here that this discrepancy changed the published headline results.

## Benchmark interpretation

The [published agentic result](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/benchmarks/results/2026-10-07-agentic.md)
describes 39 author-selected tasks, five repetitions and three arms (585 sessions),
Opus 5.5 and Claude Code 2.1.288. Bash was disabled in all arms: the model wrote
artifacts and an external harness graded them. This does not measure a full tool
execution, verification and repair loop like TaskForge's normal coding workflow.

The report uses per-task medians and geometric aggregation; some cost comparisons
cover 38 tasks. Completion, test presence, runnable tests and injected-bug detection
have different denominators and meanings. The inspected revision does not include
the raw run/session results or all bootstrap/mutation tooling needed to independently
recompute the report. This is a reproducibility limit, not evidence of fabricated
results. No reported savings percentage is transferred to TaskForge, and no local
model efficacy or cost improvement is claimed.

## Runtime and license boundaries

The optional band writes local CSV/HTML; the board is a local HTML file opened in a
browser, not an identified local HTTP server. Configured webhooks can send usage and
task names; the URL is empty by default, authentication is optional, and loopback
HTTP is permitted. Those features add persistent state, network and host-API surface
without a demonstrated TaskForge need, so none is adopted. Static checks did not
establish an authentication bypass or a live host compatibility result.

Upstream [LICENSE](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/LICENSE)
is MIT, copyright (c) 2026 DietrichGebert, with notice retention for copied or
substantial portions. This change adds original wording and source attribution;
it imports no upstream runtime or full prompt file. It does not clear rights for
the repository's separately archived third-party materials or enable their distribution.

## Validation boundary

Use repository validation, generated-payload checks, skill validation and existing
build/runtime/install/context regressions for this change. Exact command results
and skipped checks are recorded in the existing project progress record. Instruction
compliance, upstream runtime reproduction, full Windows stability and operational
deployment require separate evidence.
