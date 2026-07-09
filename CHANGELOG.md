# Changelog

## v1.1.0 - Unreleased

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
- Removed orphan EngineeringPrinciples and Communication policy files.
- Simplified model usage guide to avoid pack-routing duplication with loading-map.

## v1.0.0

- Initial complete framework package.
- Added kernel, policies, modules, domains, reviewers, workflows, tests, docs, and examples.
