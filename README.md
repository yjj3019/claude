# FEF Claude Framework

Framework for Engineering Excellence (FEF) is a Claude-oriented engineering prompt framework.

Its goal is to help Claude produce more consistent, evidence-aware, reviewable, and enterprise-grade technical outputs.

**한국어:** [README.ko.md](README.ko.md)

## For AI agents (repo URL only)

```bash
git clone https://github.com/yjj3019/claude.git
cd claude
python3 scripts/install_pack.py --auto
# then: Claude Code → open this repo as workspace (loads CLAUDE.md)
# Claude Projects → paste CLAUDE.md into Project Instructions; attach packs as needed
```

- `python3 scripts/install_pack.py --auto` — detect Claude / Codex / Grok / Cursor / AGENTS hosts and copy the pack to each skills root as `fef-claude/`; also installs into **sibling git repos**
- `python3 scripts/install_pack.py --print-bootstrap` — one-liner AIs should run in multi-root workspaces
- `python3 scripts/install_pack.py --print-claude` — exact paste steps for Claude Project Instructions
- `python3 scripts/install_pack.py --check` — verify files and run `validate_framework.py` when tests are present
- `python3 scripts/install_pack.py --help` — `--dest`, `--siblings`, `--siblings-only`, `--with-tests`, `--dry-run`

Preferred Claude Code path: **open this clone as the workspace** so `CLAUDE.md` loads at the root. Skill copies are for hosts that discover packs under `~/.claude/skills` (and similar).

### Multi-repo / sibling auto-install

Attach **this repo + your project repo(s)** in one workspace (multi-root). The agent runs `--auto` once; the pack lands in host skills **and** each sibling project's skill roots:

```bash
# From this clone:
python3 scripts/install_pack.py --auto

# From another repo's cwd (script path is absolute to this clone):
python3 /path/to/claude/scripts/install_pack.py --auto

# Preview only / siblings only / extra roots:
python3 scripts/install_pack.py --auto --dry-run
python3 scripts/install_pack.py --siblings-only
python3 scripts/install_pack.py --siblings /other/project --auto
# Env: FEF_SIBLING_ROOTS=/a:/b  (os.pathsep-separated)
```

Sibling targets (non-destructive): `<sibling>/.claude/skills/fef-claude` and/or `<sibling>/.agents/skills/fef-claude` when `.claude/`, `.cursor/`, `AGENTS.md`, or `.git` markers warrant creating those skills dirs.

## What's new (pack updates)

- **Adaptive Effort** — Sonnet default for everyday work; Haiku only for light Notion/docs (L0); escalate model before packs (`docs/adaptive-effort.md`).
- **Round 2 routing** — KO language tiers, unmapped high-risk handling, fallback guard.
- **Round 3** — high-risk AND action gate, hooks, cold-start `CLAUDE.md`+`AGENTS.md` budget, lean install docs, reviewer Output contracts.
- **Multi-repo auto-install** — `--auto` installs into sibling git repos / `FEF_SIBLING_ROOTS` / `--siblings` (this change).

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

Operational Integrity keeps file, tool, artifact, and completion claims evidence-backed. Coding tasks use the Coding Module, Workflow, and optional Reviewer; policies are selected by task trigger rather than loaded globally.

## Memory Bootstrap

Start every new Claude session by reading `CLAUDE.md` first. Treat `CLAUDE.md` as the persistent working-memory bootstrap, then load only the supporting files it names for the task.

## Context Budget + Model-Invariant Floor

**Context Budget (normal use):** inlined Kernel via `CLAUDE.md` + packs named by `docs/loading-map.md` within Load Limits (Module 1 / Domain ≤2 / Workflow 1 / Reviewer 1 / Policies ≤3). Do **not** preload every module, domain, workflow, or doc.

**Model-Invariant Floor** (see `docs/model-usage.md`): regardless of Opus 5 / Fable 5.1 / Sonnet 5 / Haiku 4.5:

1. Same Kernel + Operational Integrity (evidence, completion, authorization).
2. Same Context Budget — do not dump extra docs onto weaker or stronger models to “compensate.”
3. Same loading map / task routing.
4. Same output contract (`[unverified]`, smallest complete change, no fake completion).
5. When blocked: **escalate the model** (`Haiku` → `Sonnet` → `Opus` → `Fable`); do **not** expand unrelated packs.

Advisory defaults (verify availability): everyday / when unsure → Sonnet 5; everyday complex → Opus 5; hardest/longest → Fable 5.1; light Notion/doc recording → Haiku 4.5.


## Latency & lightness

**Always-on (simple/low-risk cold-start):** `CLAUDE.md` inlined Kernel only. Do not autoload `docs/model-usage.md`, README, CHANGELOG, PROGRESS, SESSION_LOG, optimization reports, or full modules/domains.

**Deferred:** `docs/loading-map.md` and the packs it names, only for substantial tasks within Load Limits. Prefer latency over completeness of pack load.

**Model choice ≠ more docs:** Haiku / Sonnet / Opus / Fable share the same tiny Kernel; escalate the model when blocked — do not dump packs to compensate. Load `docs/model-usage.md` only when choosing or switching models (or tuning effort/thinking).

**Projects warning:** Attaching the entire repository as Project Knowledge slows models and defeats the cold-start contract. Paste `CLAUDE.md` into Project Instructions and attach only the packs the task needs.

Estimate structural load with `python scripts/measure_load.py` (prints a **simple Q&A cold-start** line). This measures pack bytes/tokens, not host wall-clock latency.


## Adaptive Effort

FEF auto-tiers work by request complexity (L0 Light docs → L3 Hardest): **Sonnet is the default** for everyday coding/Q&A/edits (and when unsure); Haiku only for light Notion/doc recording; Opus for multi-step everyday work; Fable for deep/long-running tasks. Escalate the **model before packs**, and keep L0–L1 free of model-usage/README/PROGRESS preloads so cold-start stays fast. Details: `docs/adaptive-effort.md`.

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

Naming note: FEF `workflows/` contains Markdown task procedures loaded as prompts. Claude Code `.claude/workflows/` contains executable dynamic-workflow scripts. They are unrelated, and FEF does not ship dynamic workflows.

## Design Philosophy

- Keep the kernel small.
- Add capability through modules.
- Prefer evidence over memory.
- Reduce hallucination by requiring uncertainty markers.
- Improve consistency through review and golden tests.

## Validate

GitHub Actions runs the same validator on every push and pull request. Run it locally with:

```powershell
python scripts/validate_framework.py
python scripts/sync_kernel.py --check
python scripts/measure_load.py
python -m unittest discover -s tests -p "test_*.py"
```

## Task Routing Examples

### RHEL incident RCA

- Request: “RHEL 커널 장애 원인을 분석하고 고객 RCA를 작성해줘.”
- Packs: RCA Module, RHEL Domain, RCA Workflow, Technical Reviewer, Evidence/Thinking/Review policies.
- Why: incident/RCA and RHEL keywords; customer-facing work raises risk.
- Abbreviated output: observed facts, hypotheses, root cause, corrective actions, verification gaps.
- Verification: one Technical Reviewer pass after the draft.

### OpenShift feature proposal

- Request: “OpenShift 신규 기능을 조사해 고객 제안서로 정리해줘.”
- Packs: Proposal Module, OpenShift Domain, Proposal Workflow, Proposal Reviewer, Writing/Evidence/Review policies.
- Why: proposal intent wins over the secondary research keyword; OpenShift selects the Domain.
- Abbreviated output: requirement mapping, scoped feature claims, value, risks, evidence gaps.
- Verification: current claims still require Freshness verification when applicable.

### Minimal code fix

- Request: “이 Python 버그를 최소 변경으로 수정하고 테스트해줘.”
- Packs: Coding Module and Workflow, optional Code Change Reviewer, FileHandling/ToolExecution policies.
- Why: bug/minimal-change keywords map to the shared-root-cause coding route.
- Abbreviated output: root cause, patch, caller scan, test result, remaining risk.
- Verification: inspect the actual repository diff and run the narrowest relevant test.

Preview routing without an API:

```powershell
python scripts/detect_task.py --task "RHEL 장애 RCA를 작성해줘"
```

## Install and Operate

- [Claude Projects setup](docs/ClaudeProjects.md)
- [Claude Code setup](docs/ClaudeCode.md)
- [Installation](docs/Installation.md)
- [Model usage + invariant floor](docs/model-usage.md)
- [Harness scripts](scripts/README.md)
- [Golden Test coverage](docs/golden-test-coverage.md)
- [Release and versioning](docs/release-process.md)
- [Simulation-10 report (2026-09-06)](docs/simulation-10-report-2026-09-06.md)
