# Prompt Engineering Module

## Purpose

Improve prompts as testable, portable engineering artifacts rather than collections of persona slogans.

## Review Dimensions

- objective and non-goals
- target model, runtime, tool availability, and context limits
- instruction hierarchy and conflict handling
- user intent and clarification threshold
- output contract and completion criteria
- evidence, freshness, citation, and uncertainty rules
- file and tool behavior
- approval boundaries for external or destructive actions
- prompt-injection resistance and treatment of untrusted content
- hallucination resistance
- modularity and duplication
- context and token efficiency
- failure behavior and degraded mode
- portability across model classes
- evaluation method, golden tests, and removal criteria

## Prompt Contract

A prompt missing role, task, success, or verification is not ready for review. These ten fields make the drafting-time and output-contract dimensions above concrete; injection resistance, hallucination resistance, token efficiency, and portability still need the checks in their own sections below, not just a filled-in field.

| Field | Answers |
|---|---|
| Role | What responsibility and perspective does the judgment come from |
| Task | What is performed |
| Success | What must be true to count as complete |
| Context | Inputs, sources, current state, terminology |
| Constraints | Scope, prohibitions, authority, cost, time |
| Tools | Available tools and when to call them |
| Examples | Desired input/output and edge cases |
| Output | Return format, required fields, uncertainty expression |
| Verification | Evidence to check before declaring done, and failure handling |
| Stop / Escalation | When to halt, require approval, or retry |

Minimal example:

```xml
<role>A scoped security code reviewer.</role>
<task>Find authentication, authorization, and input-validation defects in the target diff.</task>
<success>Each finding includes file, line, rationale, severity, and a reproduction or fix.</success>
<context>Project rules and the change diff are provided here.</context>
<constraints>Do not modify files outside the diff. Do not present speculation as fact.</constraints>
<tools>Use read-only search tools; no tool may write or execute.</tools>
<examples>
Input: a diff adding an endpoint that reads `request.user_id` without an ownership check.
Output finding: {file, line, "missing authorization check on user_id", severity: critical, fix: "compare user_id against the authenticated session before the query"}.
</examples>
<output>Return a structured finding list and mark unverified items explicitly.</output>
<verification>Re-confirm each finding's evidence against the diff and the actual code.</verification>
<stop_escalation>Stop and report if scope is exceeded or a secret is exposed.</stop_escalation>
```

This overlaps `docs/context-protocol.md`'s Context Frame (audience, artifact type, risk, missing information) for Role/Task/Context; use the Context Frame to interpret a request, this contract to specify the resulting prompt.

## Recording a Promoted Rule's Evaluation

The Prompt Improvement Rules require an evaluation scenario for each promoted rule. Do not invent a new record schema for it — reuse what Golden Tests and benchmark runs already use, at whichever grain fits:

- If the rule is exercised by a Golden Test, its result is a `verdict` (`pass`/`fail`/`not_run`) plus per-dimension scores under `config/scorecard.schema.json`.
- If the rule is evaluated by a standalone prompt run (no Golden Test scenario), follow the shape in `tests/benchmarks/PILOT-RUN.example.json`: `run_id`, `requested_model`, `served_model`, `fallback_detected`, `task_success`. Use `served_model` (not a new field) to record what the runtime actually used.
- Record the resolved `effort` from `docs/model-usage.md`'s scale (`low`/`medium`/`high`/`xhigh`/`max`), and log it under the Effort Calibration Guardrail in `docs/model-usage.md`, not as a separate ledger.

Do not promote a rule to this contract without a passing or explicitly reviewed record in one of the two schemas above.

## Prompt Improvement Rules

- Remove vague persona-only instructions.
- Replace slogans with observable behaviors and trigger conditions.
- Separate permanent rules from task-specific modules.
- Define which instruction wins when rules conflict.
- Define what evidence is required and when current verification is necessary.
- Define what the model must do when tools, files, or verification are unavailable.
- Define output structure, completion criteria, and approval boundaries.
- Avoid claiming capabilities the target runtime does not provide.
- Keep safety and platform policy in the platform layer unless a domain-specific operational rule is required.
- Prefer the smallest rule that prevents a demonstrated failure.
- Add a test or evaluation scenario for each promoted reusable rule.
- Define when a rule should be removed if it no longer improves measured results.

## Examples Are Specification

An example is followed more reliably than the instruction beside it. Treat every example as a
rule the model will generalize from.

- Verify that identifiers, field names, paths, and values shown in examples exist in the target
  system. An invented example name teaches the model to invent names of that shape.
- When the permitted set is knowable, enumerate it instead of illustrating the format, and
  generate that list from the system so it cannot drift from reality.
- State what to do when a needed value is absent from the permitted set. Without that, the model
  closes the gap by extrapolating from the examples.

## Payload Budget

- Blocks that scale with input count (per-finding evidence, retrieved passages, raw data dumps)
  need a shared budget and an explicit drop order. Size the prompt on a realistic worst case,
  not on a single item.
- Drop or shorten blocks before assembly. Truncating the assembled prompt removes whatever sits
  at the end, which is usually the output contract.
- When adding content to a prompt, measure the resulting size. A change that improves grounding
  can still push the request past a latency or timeout boundary.
