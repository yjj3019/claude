# Fable Pattern Bank

This file stores distilled, reusable engineering patterns extracted from Fable5 feedback.

It is a holding area, not an instruction layer.
Do not load this file by default.
Promote a pattern into a module, domain, workflow, reviewer, policy, or golden test only when it is reusable and testable.

## Promotion Rule

A pattern can be promoted only if it has:

1. repeated failure evidence from Opus/Sonnet output
2. a clear trigger condition
3. a minimal behavior rule
4. a target FEF file
5. a golden-test or review method
6. a reason it is not prompt bloat

## Pattern Record Template

```markdown
### Pattern: <short name>

Source:
- Fable5 review date:
- Work type:
- Related outputs/tests:

Observed failure:
- What Opus/Sonnet missed:

Fable5 behavior to transfer:
- What Fable5 consistently did better:

Trigger:
- When this pattern should activate:

Minimal rule:
- One sentence or one checklist bullet:

Target FEF file:
- Existing file only:

Test method:
- How to verify improvement:

Do not add:
- What would be prompt bloat:

Status:
- Candidate / Promoted / Rejected / Retired
```

---

## 1. Proposal Consistency Review

Use for enterprise proposal consistency checks, requirement traceability, contradiction detection, and submission risk review.

Candidate patterns:

- TBD from Fable5 distillation

## 2. RHEL / OpenShift Proposal

Use for enterprise infrastructure proposals involving version-sensitive technical, lifecycle, subscription, support, compliance, and operations claims.

Candidate patterns:

- TBD from Fable5 distillation

## 3. Technical Blog Post

Use for practical Korean enterprise technical blog posts, including S-Core OSSLab-style posts.

Candidate patterns:

- TBD from Fable5 distillation

## 4. Operations Manual / SOP

Use for reproducible technical procedures with validation, rollback, troubleshooting, and operational notes.

Candidate patterns:

- TBD from Fable5 distillation

## 5. RCA / Troubleshooting

Use for incident analysis, log review, hypothesis testing, root cause confidence, corrective actions, and prevention.

Candidate patterns:

- TBD from Fable5 distillation

## 6. Code Review / Coding Workflow

Use for transferring Fable5-like engineering judgment into Opus/Sonnet coding workflows.

Candidate patterns:

- TBD from Fable5 distillation

## 7. Cross-Cutting Patterns

Use for patterns that appear across multiple work types.

Candidate patterns:

- surface request -> operational problem
- ambiguity and contradiction first
- evidence-sensitive claims require source/scope
- hidden dependency surfacing
- severity classification
- one-pass review unless re-requested
- test before expanding instructions
