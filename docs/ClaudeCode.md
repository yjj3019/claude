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
