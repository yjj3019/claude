# AGENTS.md

This repository is a reusable guidance root for Claude-oriented engineering workflows.

## Runtime Entry Point

- Start with `CLAUDE.md`.
- Treat `CLAUDE.md` as the persistent bootstrap.
- Load only the supporting files it names for the current task.

## Context Budget

**Latency > completeness of pack load.** Normally use the inlined Kernel in `CLAUDE.md` plus at most the packs named by `docs/loading-map.md` within Load Limits (Module 1 / Domain ≤2 / Workflow 1 / Reviewer 1 / Policies ≤3). Do not preload every module, domain, workflow, or doc. Simple low-risk questions stay Kernel-only.

**Model-Invariant Floor:** Opus 5 / Fable 5.1 / Sonnet 5 / Haiku 4.5 keep the same Kernel, Operational Integrity, Context Budget, and routing. When blocked, escalate the model — do not expand unrelated packs (`docs/model-usage.md` only when choosing/switching).

**Adaptive Effort:** classify ask (L0–L3); unsure→Sonnet(L1); Haiku only light Notion/docs(L0); escalate model before packs. See `docs/adaptive-effort.md`.

## Guidance Layout

- `kernel/` contains always-on reasoning behavior.
- `policies/` includes trigger-loaded Evidence, FileHandling, ToolExecution, and Freshness rules.
- `modules/` contains task-specific behavior, including the Coding pack.
- `domains/` contains domain-specific knowledge packs.
- `reviewers/` contains focused review prompts.
- `workflows/` contains reusable task workflows.
- `tests/` contains golden tests and fixtures.
- `scripts/validate_framework.py` checks framework structure and routing.
- `scripts/install_pack.py --auto` installs this pack for detected AI hosts (URL-only setup).
- `scripts/measure_load.py` estimates Kernel vs route load sizes.

## Use Rule

When this repository is the working root, apply `CLAUDE.md` first and follow its routing. Do not load every file by default.
