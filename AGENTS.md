# AGENTS.md

This repository is a reusable guidance root for Claude-oriented engineering workflows.

## Runtime Entry Point

- Start with `CLAUDE.md`.
- Treat `CLAUDE.md` as the persistent bootstrap.
- Load only the supporting files it names for the current task.

## Guidance Layout

- `kernel/` contains always-on reasoning behavior.
- `policies/` contains evidence, decision, review, writing, calibration, and thinking rules.
- `modules/` contains task-specific behavior.
- `domains/` contains domain-specific knowledge packs.
- `reviewers/` contains focused review prompts.
- `workflows/` contains reusable task workflows.
- `tests/` contains golden tests and fixtures.

## Use Rule

When this repository is the working root, apply `CLAUDE.md` first and follow its routing. Do not load every file by default.
