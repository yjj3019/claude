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

Naming note: FEF `workflows/` contains Markdown task procedures loaded as prompts. Claude Code `.claude/workflows/` contains executable dynamic-workflow scripts. They are unrelated, and FEF does not ship dynamic workflows.

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
- [Harness scripts](scripts/README.md)
- [Golden Test coverage](docs/golden-test-coverage.md)
- [Release and versioning](docs/release-process.md)

