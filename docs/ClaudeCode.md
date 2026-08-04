# Claude Code Guide

Recommended structure:

```text
project-root/
├── CLAUDE.md
├── kernel/
├── policies/
├── modules/
├── domains/
├── workflows/
├── reviewers/
└── docs/
```

Start Claude Code from `project-root/` so it can discover `CLAUDE.md` and its relative Pack paths. Keep the copied directory layout intact.

Naming note: FEF `workflows/` contains Markdown task procedures loaded as prompts. Claude Code `.claude/workflows/` contains executable dynamic-workflow scripts. They are unrelated, and FEF does not ship dynamic workflows.

Mention modules explicitly in the prompt:

- "Use Proposal Module."
- "Use RCA Workflow."
- "Use RHEL Domain Pack."

Before use, run `python scripts/validate_repository.py` in the framework repository. For task previews, run `python scripts/detect_task.py --task "..."`; the result is advisory, not an automatic replacement for task judgment.

## Native Reviewer Subagents

Reviewer prompts are available as read-only Claude Code subagents such as `@agent-technical-reviewer`. Files in `reviewers/` remain the source of truth and continue to work unchanged in Claude Projects. Run `python scripts/generate_agents.py` after editing a reviewer to synchronize `.claude/agents/`.

## Mechanical Enforcement Hooks

Kernel rules 13-14 (no completion claim without observable verification) are enforced mechanically, not just by prompt, via two Claude Code hooks configured in `.claude/settings.json`:

- `scripts/hooks/record_test_run.py` (PostToolUse, Bash): records a session-local marker whenever a recognized test command runs (`pytest`, `unittest`, `npm test`, `go test`, `cargo test`).
- `scripts/hooks/verify_before_stop.py` (Stop): if `*.py` files were modified after the last recorded test run, blocks the stop once and asks for verification (or an explicit stated limitation). It never loops (`stop_hook_active` guard) and fails open on any error, so a broken hook cannot trap a session.

`.claude/settings.json` invokes both hooks as `python` (matches this workspace's primary Windows/PowerShell environment per `AGENTS.md`). On Linux/Mac where `python` is not aliased to Python 3, change it to `python3`. Both hooks are covered by `tests/test_hooks.py`.
