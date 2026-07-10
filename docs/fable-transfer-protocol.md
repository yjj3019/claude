# Fable Transfer Protocol

This protocol defines how to use scarce Fable5 review capacity to improve Opus/Sonnet workflows through FEF.

It does not instruct any model to impersonate Fable5.
It transfers observable engineering behaviors, not personality, identity, or hidden chain-of-thought.

## Purpose

Use Fable5 as a calibration and failure-analysis source.
Use Opus/Sonnet as the daily execution models.
Use FEF as the persistent memory of what was learned.

## Roles

| Model | Primary Role | Use For | Avoid |
|---|---|---|---|
| Fable5 | Calibrator / failure analyst | framework review, failure pattern extraction, rubric improvement, high-value artifact review | routine drafting, repeated low-risk work |
| Opus | Reviewer / Architect | technical review, consistency checks, risk judgment, final external review | bulk drafting when Sonnet is enough |
| Sonnet | Builder | drafts, outlines, rewrites, blog posts, manuals, structured production | final high-risk claims without review |

## Transfer Loop

1. Run work with Sonnet or Opus using FEF.
2. Compare output against the desired engineering behavior.
3. If failure repeats, ask Fable5 to identify the missing pattern.
4. Convert only reusable findings into FEF rules, checklists, or golden tests.
5. Reject one-off stylistic advice unless it improves measurable output quality.
6. Re-test with Opus/Sonnet.

## When to Use Fable5

Use Fable5 when:

- a new work type is added to FEF
- a golden test is designed or failing
- Opus/Sonnet repeatedly miss the same class of issue
- a customer-facing or public artifact is high impact
- a framework change may increase prompt bloat
- release readiness needs strict review

Do not use Fable5 for:

- routine summaries
- low-risk rewrites
- already-tested workflows
- simple internal notes
- generating many drafts

## Extractable Behaviors

Transfer these behaviors into FEF:

- restating the real operational problem
- detecting ambiguity and contradictions before drafting
- separating fact, assumption, inference, and recommendation
- flagging unsupported claims without destroying usefulness
- mapping requirements to sections or evidence
- surfacing hidden dependencies and operational risks
- classifying severity proportionally
- stopping after the useful review pass
- preferring minimal fixes over redesign
- using tests to decide whether a rule helped

Do not transfer:

- Fable5 wording, persona, or voice
- theatrical reasoning traces
- hidden chain-of-thought style
- broad meta-instructions that cannot be tested
- rules that only helped one document once

## Failure-to-Rule Conversion

When Fable5 identifies a failure, convert it using this format:

1. Failure pattern: what Opus/Sonnet missed
2. Trigger: when the pattern applies
3. Minimal rule: one sentence or one checklist bullet
4. Target file: existing module, domain, workflow, reviewer, policy, or golden test
5. Test: how to verify the rule helped
6. Removal condition: when to delete or simplify it

If no test or observable behavior exists, do not add the rule.

## Fable Review Prompt Template

Use this when asking Fable5 to improve FEF from a failed output:

```text
Review this Opus/Sonnet output only to extract reusable engineering behavior.
Do not rewrite the full artifact unless needed to illustrate the issue.
Do not propose architecture redesign.
Identify:
1. repeated failure pattern
2. missing FEF rule or checklist item
3. smallest file/change that would prevent recurrence
4. how to test the improvement
5. what not to add because it would be prompt bloat
```

## Guardrails

- FEF is not a Fable5 emulator.
- FEF is an engineering behavior transfer system.
- Every added instruction should reduce variance, reduce hallucination, improve review quality, or improve operational usefulness.
- Prefer one tested rule over ten attractive principles.
- If Fable5 advice conflicts with measured golden-test results, trust the test and re-check the prompt.
