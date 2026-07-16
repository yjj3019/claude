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
