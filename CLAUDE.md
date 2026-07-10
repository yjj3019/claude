# CLAUDE.md — FEF Runtime Entry

If the Kernel files cannot be loaded, stop and report the missing file.
Do not continue in an ungoverned state.

## Purpose

This file is the runtime entry point for FEF. It points to the active instruction files; it does not duplicate their rules.

## Required Kernel Load Order

1. `kernel/CoreKernel.md`
2. `kernel/MetaRules.md`
3. `kernel/Checklist.md`

Kernel rules are the single source of truth for permanent reasoning behavior.
Edit Kernel behavior in `kernel/`, not in this file.

## Optional Runtime Packs

Use `docs/context-protocol.md` to frame substantial tasks.
Use `docs/model-usage.md` when splitting work across builder/reviewer/architect roles.
Use `docs/fable-transfer-protocol.md` only when converting Fable5 feedback into reusable FEF improvements.
Use `docs/loading-map.md` to select task-specific:

- policies
- modules
- domains
- workflows
- reviewers

Load only what the task requires.

## Instruction Precedence

1. System / platform instructions
2. Workspace `CLAUDE.md`
3. Workspace `AGENTS.md`
4. Repository `CLAUDE.md`
5. User task
6. Loaded FEF packs

If a conflict appears, follow the higher-priority instruction and report the conflict when it affects the task.

## Runtime Rules

- Simple low-risk tasks may use Kernel only.
- Substantial technical artifacts should use `docs/loading-map.md`.
- Reviewer runs at most once per artifact.
- Do not review reviewer output.
- Do not add new permanent layers; add new capability inside existing directories.
