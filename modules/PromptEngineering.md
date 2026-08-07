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

## Canonical Prompt Contract

Every operational prompt should be traceable to these ten fields. This is the minimum unit each `Review Dimensions` item above maps to — use it as a checklist when drafting or auditing a prompt, not as boilerplate to paste verbatim.

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
| Stop/Escalation | When to halt, require approval, or retry |

Minimal example:

```xml
<role>A scoped security code reviewer.</role>
<task>Find authentication, authorization, and input-validation defects in the target diff.</task>
<success>Each finding includes file, line, rationale, severity, and a reproduction or fix.</success>
<context>Project rules and the change diff are provided here.</context>
<constraints>Do not modify files outside the diff. Do not present speculation as fact.</constraints>
<tools>Use Read, Grep, Glob only. No write tools.</tools>
<examples>Include related, diverse examples and at least one false-positive example.</examples>
<output>Return a structured finding list and mark unverified items explicitly.</output>
<verification>Re-confirm each finding's evidence against the diff and the actual code.</verification>
<stop>Stop and report if scope is exceeded or a secret is exposed.</stop>
```

A prompt that only states role and skips task, success, and verification does not qualify for promotion to a Canonical prompt.

## Evaluation Record

Every promoted rule needs the evaluation scenario the Prompt Improvement Rules already require. Record it in a schema instead of prose so revisions stay comparable:

```yaml
prompt_id: stable-name
revision: 2026-01-01.r1
requested_model: model-alias
resolved_model: recorded-at-runtime
effort: low | medium | high
eval_set: path-or-version
success_criteria: measurable
quality_metrics: [correctness, coverage, format_validity]
usage: input_tokens, output_tokens, cost, latency
decision: keep | revise | rollback
reviewed_at: 2026-01-01
```

`requested_model` and `resolved_model` are kept separate because a runtime may substitute a different model than the one asked for; recording only one hides that drift. Do not promote a rule to Canonical status without a `decision: keep` entry backed by an actual eval run.

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
