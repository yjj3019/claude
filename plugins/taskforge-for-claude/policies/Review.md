# Review Policy

## Purpose

Review reduces unsupported claims, logical gaps, and operational risk.

## Review Checklist

- Are factual claims supported?
- Are assumptions explicit?
- Are conclusions proportional to evidence?
- Are risks and failure modes included?
- Are version and scope clear?
- Is the recommendation actionable?
- Is anything overconfident?
- Is anything missing for real-world execution?

## Evidence and Independence

- For substantial deliverables, compare the requested criteria with the actual diff, artifacts and command results; the implementer's summary is a starting point, not proof.
- Distinguish verified behavior, observed failure, blocked verification and checks not run. Static review and dynamic testing provide different evidence; neither substitutes for a missing applicable check.
- Bind conclusions to the inspected artifact or worktree state. Preserve earlier failures and skipped checks when a later run passes; a rerun does not establish that an intermittent defect is resolved.
- Inspect the intended verification command and its final summary against the criteria, including no-tests and skipped results. Retain raw logs behind summaries; a footer or exit code proves only the recorded process outcome.
- A hash or read receipt does not establish relevance, reviewer understanding, authorship or execution authority. State excluded inputs and environment limits; when CI is relied on as independent evidence, check its actual required jobs and command rather than trusting a local attestation.
- Use a separate reviewer context when task risk and available tools justify it. If independent review was unavailable, disclose that gap; do not imply a second reviewer participated.
- Blocking findings require correction or an explicit unresolved limitation. Optional style suggestions alone should not start another implementation or review loop.

## Review Severity

Critical:
- dangerous, false, misleading, or unsupported high-impact claim

Major:
- important omission or weak reasoning

Minor:
- wording, structure, clarity issue

Suggestion:
- optional improvement
