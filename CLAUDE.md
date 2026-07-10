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

## Autoload Protocol

This file is the single runtime entry point. For each task:

1. Always load the Required Kernel files below, in order.
2. For simple low-risk tasks, answer with Kernel only.
3. For substantial tasks, load `docs/loading-map.md` and follow its selected packs.
4. Load only the files named by the loading map: policies, modules, domains, workflows, reviewers.
5. If a selected file is missing, stop and report the missing file. Do not substitute silently.

## Optional Runtime Packs

Use `docs/context-protocol.md` to frame substantial tasks.
Use `docs/model-usage.md` only when splitting work across builder/reviewer/architect roles.
Use `docs/fable-transfer-protocol.md` only when converting Fable5 feedback into reusable FEF improvements.
Use `docs/loading-map.md` as the routing table for task-specific packs.

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

