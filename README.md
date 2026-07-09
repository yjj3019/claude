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

## Recommended Usage

For Claude Code, copy this repository into your Claude working directory and use `CLAUDE.md` as the always-loaded instruction file.

For Claude Projects, paste `CLAUDE.md` into Project Instructions and upload selected modules/domains as Project Knowledge.

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
