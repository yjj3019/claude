# Fable Distillation Prompts

Use these prompts while Fable5 is still available.

Goal: extract reusable engineering behavior from Fable5 and transfer it into FEF for Opus/Sonnet.

Do not ask Fable5 to merely write artifacts.
Ask Fable5 to identify reusable judgment patterns, failure modes, minimal rules, and tests.

## Universal Distillation Prompt

```text
I am not trying to copy your wording, persona, or hidden reasoning.
I am trying to transfer your observable engineering judgment patterns into a framework used by Opus/Sonnet.

Work type:
<insert work type>

Context:
<insert short business/technical context>

Please extract reusable patterns only.
Do not redesign the framework.
Do not propose a mega-prompt.
Do not include chain-of-thought.

Output:
1. The first context signals you would inspect
2. Common Opus/Sonnet failure modes for this work type
3. The judgment sequence that leads to high-quality output
4. Submission-blocking or production-risk failures
5. Five minimal FEF rules that would improve Opus/Sonnet
6. Ten reviewer checklist items
7. Golden Test dimensions to measure the improvement
8. What NOT to add because it would be prompt bloat
9. Which existing FEF file each rule belongs in
10. How to know the rule worked
```

## 1. Proposal Consistency Review Prompt

```text
Work type:
Enterprise proposal consistency review

Context:
The task is to check an existing proposal for internal contradictions, requirement gaps, unsupported claims, terminology/version/date/number inconsistencies, hidden dependencies, and submission risk.

Use the Universal Distillation Prompt.
Focus especially on what Opus/Sonnet miss when a proposal looks polished but is not defensible.
```

## 2. RHEL / OpenShift Proposal Prompt

```text
Work type:
RHEL/OpenShift enterprise proposal writing and review

Context:
The task is to create or review customer-facing infrastructure proposals involving lifecycle, subscription, supportability, public-sector constraints, disconnected operations, security, compliance, migration, and operating model.

Use the Universal Distillation Prompt.
Focus especially on version-sensitive claims, evidence requirements, operational feasibility, and buyer-facing defensibility.
```

## 3. Technical Blog Prompt

```text
Work type:
Korean enterprise technical blog post in S-Core OSSLab-style practical tone

Context:
The task is to write technical blog posts that are readable, practical, grounded, and useful for engineers or architects. Posts should avoid marketing tone, unsupported claims, and stiff translated prose.

Use the Universal Distillation Prompt.
Focus especially on title framing, hook, reader problem, technical explanation, operational example, and how to avoid shallow trend commentary.
```

## 4. Operations Manual / SOP Prompt

```text
Work type:
Linux/RHEL operations manual and SOP writing

Context:
The task is to create reproducible procedures with prerequisites, commands, validation, rollback, troubleshooting, operational notes, and risk warnings.

Use the Universal Distillation Prompt.
Focus especially on what makes a manual safe for real operators rather than merely descriptive.
```

## 5. RCA / Troubleshooting Prompt

```text
Work type:
Linux/RHEL incident RCA and technical troubleshooting review

Context:
The task is to analyze incident data, separate facts from hypotheses, build a timeline, identify likely root cause, calibrate confidence, and recommend immediate and preventive actions.

Use the Universal Distillation Prompt.
Focus especially on avoiding premature root cause claims and missing alternative hypotheses.
```

## 6. Code Review / Coding Workflow Prompt

```text
Work type:
Code implementation, debugging, refactoring, and review

Context:
The task is to make Opus/Sonnet better at producing maintainable code, identifying root causes, avoiding overengineering, writing useful tests, and reviewing operational/security risks.

Use the Universal Distillation Prompt.
Focus especially on how to convert senior engineering judgment into minimal coding rules, review checklists, and golden tests.
```

## Final Consolidation Prompt

Use after collecting Fable5 responses for several work types.

```text
Below are Fable5 pattern extractions across multiple work types.

Task:
Consolidate them into reusable FEF improvements.

Constraints:
- Do not redesign architecture.
- Do not add a new permanent layer.
- Do not imitate personality or wording.
- Prefer deletion/simplification over expansion.
- Only keep patterns that are reusable, testable, and likely to reduce variance or hallucination.

Output:
1. Cross-cutting patterns to promote
2. Work-type-specific patterns to keep local
3. Patterns to reject as prompt bloat
4. Existing FEF file targets
5. Minimal patch list
6. Golden Test updates needed
7. Final keep/change/drop recommendation
```
