# File Handling Policy

## Trigger

Load this policy when the task requires reading, comparing, modifying, generating, or validating files.

## Purpose

Ensure file-based work is grounded in the actual assigned files and produces real artifacts.

## Read Before Use

- Confirm that every user-referenced or task-referenced file exists and is accessible.
- Read a target file before describing, editing, or reviewing it.
- For large files, inspect structure first, then read the relevant sections. Read the entire file when the task requires whole-document coverage.
- If only part of a file was inspected, state the scope when it affects confidence.
- Never claim a file was read when access or parsing failed.

## Change Discipline

- Confirm the assigned repository or worktree before editing.
- Modify the requested files only. Avoid unrelated refactoring, mass formatting, or comment churn.
- Preserve existing conventions unless the task explicitly changes them.
- Verify that edits landed in the assigned working directory, not only in a scratch copy or temporary worktree.

## Artifact Completion

- A file-creation request is complete only when the file exists at the reported path and contains the requested content.
- A file-modification request is complete only when the diff reflects the intended change.
- Report missing, unreadable, unsupported, or partially processed files explicitly.
- Do not expose secrets or sensitive file contents beyond what the task requires.
