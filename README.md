# FEF Claude Framework

Framework for Engineering Excellence (FEF) is a Claude-oriented engineering prompt framework.

Its goal is to help Claude produce more consistent, evidence-aware, reviewable, and enterprise-grade technical outputs.

## Core Idea

FEF does not try to change the underlying model.

It provides:

- a small permanent reasoning kernel
- task-specific modules
- domain packs
- reviewer prompts
- workflow packs
- golden tests
- Claude Code / Claude Projects usage guides

Operational Integrity keeps file, tool, artifact, and completion claims evidence-backed. The Fable Transfer Protocol distills observable behavior from external evaluations without model imitation. Coding tasks use the Coding Module, Workflow, and optional Reviewer; policies are selected by task trigger rather than loaded globally.

## Memory Bootstrap

Start every new Claude session by reading `CLAUDE.md` first. Treat `CLAUDE.md` as the persistent working-memory bootstrap, then load only the supporting files it names for the task.

## Recommended Usage

For Claude Code, copy this repository into your Claude working directory and use `CLAUDE.md` as the always-loaded instruction file.

For Claude Projects, paste `CLAUDE.md` into Project Instructions and upload selected modules/domains as Project Knowledge.

## Git-Based Setup

```powershell
git clone https://github.com/yjj3019/claude.git
cd claude
```

Start Claude Code from this directory, or set this directory as the workspace root. Claude should use `CLAUDE.md` as the runtime bootstrap. `AGENTS.md` is included as a lightweight repository entry point for tools that look for an `AGENTS.md` file.

## Directory Layout

```text
FEF_Claude_Framework/
├── CLAUDE.md
├── kernel/
├── policies/
├── modules/
├── domains/
├── reviewers/
├── workflows/
├── tests/
├── docs/
└── examples/
```

## Design Philosophy

- Keep the kernel small.
- Add capability through modules.
- Prefer evidence over confident recall.
- Reduce hallucination by requiring uncertainty markers.
- Improve consistency through review and golden tests.

## Validate

GitHub Actions runs the same validator on every push and pull request. Run it locally with:

```powershell
python scripts/validate_framework.py
```

