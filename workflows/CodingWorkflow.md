# Coding Workflow

1. Confirm repository, branch or worktree, requested scope, and protected files.
2. Inspect project instructions, target files, relevant callers, tests, and available commands.
3. Reproduce the defect or establish a concrete failing condition when feasible.
4. Form a root-cause hypothesis and compare at least one plausible alternative.
5. Select the narrowest change point that fixes all relevant callers without unrelated refactoring.
6. Apply the change and add or update focused tests when needed.
7. Run the narrowest relevant validation first, then broader project checks when practical.
8. Inspect exit codes, test output, final diff, and the actual assigned worktree.
9. Report changed files, validation commands and results, assumptions, and remaining risks.

Do not declare completion after planning, editing, or running a command alone. Completion requires verified state.
