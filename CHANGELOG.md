# Changelog

## Unreleased — 2026-10-16 (fix)

- generate_agents.py now preserves per-reviewer model (opus/sonnet) and emits omitClaudeMd: true.
- Regenerated .claude/agents/*.md so validation passes on clean checkout.
- Latency oversize test uses CHANGELOG.md as stand-in (PROGRESS.md was too small).
- Bump plugin.json version to 1.3.0.
- Move completed v1.3 items out of ROADMAP In Progress.

## Unreleased — 2026-10-16

- Sync generated reviewer agents under `.claude/agents/` with current reviewer sources.
- Compact AGENTS.md guidance lines so CLAUDE.md + AGENTS.md cold-start stays under 5500-byte budget.
- Stabilize latency oversize test to use CHANGELOG.md as stand-in.
- Expand domains/Tesla.md and domains/AI.md with version-sensitive and evaluation rules.

## Unreleased — 2026-10-09

- Compact generated core and pointer entry; merge Coding/Research default procedures with compatible old paths; make coding review conditional.
- Session baseline/content-hash verification and real-exit argv wrapper replace the shared marker; retain visible fail-open diagnostics and Stop loop protection.
- Fingerprint all shipped files, verify installed manifests and omit local session state; preserve overwrite protection.
- Update Code/Projects, effort/Advisor and context/harness guidance without adding model calls or dependencies.
