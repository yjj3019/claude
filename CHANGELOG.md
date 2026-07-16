# Changelog

## Unreleased

- Added deterministic Korean/English task routing with JSON output, safe unmapped fallback, Pack-path checks, and load-limit validation.
- Added repository and Golden Test validate-only harnesses, coverage metadata, Scorecard anchors, a critical-error gate, and JSON result schema.
- Clarified Reviewer selection/execution, Integrity versus Preference Policy precedence, and external-facing wording for unverified claims.
- Expanded Claude Projects, Claude Code, scripts, CI, Semantic Versioning, and release onboarding.

## v1.2.0 - 2026-07-16

- Fixed the loading-map reviewer-count conflict by introducing a single combined Proposal Consistency Reviewer.
- Clarified instruction precedence and separated instruction authority from evidence priority.
- Added graded missing-pack behavior for critical, required, and optional runtime files.
- Added Freshness, File Handling, and Tool Execution policies.
- Added Coding Module, Coding Workflow, and Code Change Reviewer.
- Expanded Prompt Engineering Module and Prompt Workflow with runtime contracts, action boundaries, injection resistance, portability, and evaluation criteria.
- Added a project-specific `CLAUDE.md` template without replacing the FEF runtime entry.
- Added automated framework structure and loading-map validation with GitHub Actions.
- Added operational-integrity Kernel rules for evidence-backed completion.
- Added trigger-based policy selection, context checkpoints, and a model-independent distillation gate.
- Added Golden Tests 015-022 for file truthfulness, artifact completion, tool failures, freshness, instruction conflicts, proportionality, output contracts, and long-context retention.
- Expanded validation for required runtime packs, Golden Test IDs, and prohibited model-specific Runtime modes.
- Updated README, AGENTS, Roadmap, task routing, reviewer contracts, and CI coverage for the integrated v1.2 runtime.

## v1.1.1 - 2026-07-10

- Added S-Core OSSLab style guidance to the Blog module.
- Added technical blog post routing to the loading map.
- Added Fable transfer protocol for using Fable5 feedback to improve Opus/Sonnet workflows without impersonation.
- Added Fable pattern bank and distillation prompts for extracting reusable Fable5 judgment patterns.
- Promoted core Fable patterns into Evidence policy and Proposal reviewer guidance.
- Added coding-focused golden tests GT012, GT013, and GT014.
- Recorded GT012, GT013, and GT014 coding evaluation results comparing Fable5, Opus+FEF, and Sonnet+FEF.
- Added coding transfer findings summary for observed Opus/Sonnet behavior against Fable5 reference runs.
- Tightened GT014 runner protocol to verify patches land in the assigned work directory.
- Added `.gitignore` entries for temporary work directories and Python cache files.
## v1.1.0 - 2026-07-09

- Converted `CLAUDE.md` into a runtime entry point that points to Kernel and task-specific packs instead of duplicating rules.
- Added `docs/loading-map.md` with load limits, task routing, simple-task bypass, and reviewer execution bounds.
- Expanded `domains/RHEL.md` with version-sensitive, public-sector, disconnected operations, security, operations, competitive, and proposal fact discipline guidance.
- Reworked `tests/GoldenTest-001.md` into an operational RHEL proposal A/B evaluation asset.
- Added context and model usage guides for builder/reviewer/architect workflows.
- Added proposal consistency review mode to Proposal module, workflow, reviewer, and loading map.
- Added Golden Test 011 for proposal consistency check evaluation.
- Added GT011 fixture, answer key, and runner protocol for GT001/GT011.
- Added fixed prompt files for GT001 and GT011 baseline/FEF runs.
- Added GT001 result worksheet for 5x baseline/FEF evaluation runs.
- Added GT011 result worksheet for proposal consistency evaluation runs.
- Added GT001/GT011 follow-up guidance for evidence-sensitive claims and hidden dependency review.
- Removed orphan EngineeringPrinciples and Communication policy files.
- Simplified model usage guide to avoid pack-routing duplication with loading-map.

## v1.0.0

- Initial complete framework package.
- Added kernel, policies, modules, domains, reviewers, workflows, tests, docs, and examples.
