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

## Source Intake

Source: Fable5 distillation answers pasted by user on 2026-07-10.

Important limitation: Fable5 explicitly warned that self-report is not a reliable source of hidden reasoning. Patterns below are therefore treated as observable-behavior candidates, not personality or internal reasoning transfer.

## Cross-Cutting Candidate Patterns

### Pattern: Claimed vs Actual Contrast

Source:
- Fable5 distillation, common pattern across proposal, manual, RCA, code, and blog work.

Observed failure:
- Opus/Sonnet may accept the user's stated state, proposal claims, or code symptom without checking the actual artifact.

Fable5 behavior to transfer:
- Compare what is claimed against what exists: RFP vs proposal, expected output vs actual output, testimony vs logs, request vs diff, title promise vs body.

Trigger:
- Any review, consistency check, RCA, code fix, or artifact validation task.

Minimal rule:
- Before judging quality, contrast the stated claim with the primary artifact and report mismatches explicitly.

Target FEF file:
- `policies/Evidence.md`
- Existing module/reviewer files as local applications.

Test method:
- Add mismatched claim fixtures to GT011 and future RCA/code tests.

Do not add:
- Do not add persona language such as "think like Fable5".

Status:
- Candidate

### Pattern: Location-Bound Findings

Source:
- Fable5 distillation, repeated across proposal, RCA, manual, and code review.

Observed failure:
- Reviews describe issues vaguely: "some sections", "the document", "the code".

Fable5 behavior to transfer:
- Findings include a location: section, page, table, log line, file, or line number.

Trigger:
- Any review output with actionable findings.

Minimal rule:
- A finding without a location is not actionable; include the narrowest available location.

Target FEF file:
- `policies/Evidence.md`

Test method:
- Score location coverage in GT011 and future review tests.

Do not add:
- Do not require exact line numbers when the input has no stable line numbers; use section/table identifiers instead.

Status:
- Candidate for promotion

### Pattern: Placeholder Discipline

Source:
- Fable5 distillation, repeated across proposal facts, manuals, blogs, and code API use.

Observed failure:
- Models turn unverified facts into confident claims or silently invent missing details.

Fable5 behavior to transfer:
- Mark unverifiable items with scoped placeholders such as `[검증 필요: 옵션]`, `[API 검증 필요]`, or `[저자 검증 필요]`.

Trigger:
- Version-sensitive facts, lifecycle/support claims, API details, compliance claims, author-specific blog claims.

Minimal rule:
- If the fact cannot be verified from the provided/source material, tag it with a scoped verification placeholder instead of asserting it.

Target FEF file:
- `policies/Evidence.md`
- `domains/RHEL.md`
- `modules/Blog.md`
- `modules/Manual.md`

Test method:
- Existing GT001 factual-accuracy cap; add placeholder precision checks where needed.

Do not add:
- Do not tag every sentence; over-tagging is a precision failure.

Status:
- Candidate for promotion

### Pattern: Precision Is Part of Quality

Source:
- Fable5 distillation, especially GT011 improvement recommendation.

Observed failure:
- Tests reward issue detection but do not penalize false positives enough.

Fable5 behavior to transfer:
- Treat over-reporting, severity inflation, and `[unverified]` overuse as failures.

Trigger:
- Reviewer, RCA, compliance, and consistency-check tasks.

Minimal rule:
- Measure false positives as well as missed issues.

Target FEF file:
- `tests/GoldenTest-011.md`
- Future golden tests.

Test method:
- Add a normal/non-issue section to fixtures and score whether the model leaves it alone.

Do not add:
- Do not create a new policy; this is a test/rubric enhancement.

Status:
- Candidate

### Pattern: Ambiguous Severity Defaults Down

Source:
- Fable5 distillation, proposal and RCA severity/confidence handling.

Observed failure:
- Models classify too many issues as Major/Critical, destroying prioritization.

Fable5 behavior to transfer:
- If severity is ambiguous, classify one level lower unless there is direct evidence of blocker/business impact.

Trigger:
- Proposal consistency review, RCA confidence, technical review severity.

Minimal rule:
- Ambiguous severity defaults down; explain what evidence would raise it.

Target FEF file:
- `reviewers/ProposalReviewer.md`
- `reviewers/TechnicalReviewer.md`

Test method:
- GT011 severity-inflation count.

Do not add:
- Do not weaken true Critical issues such as false compliance claims or missing mandatory RFP requirements.

Status:
- Candidate for promotion

### Pattern: Mitigation Is Not Resolution

Source:
- Fable5 distillation across proposal, manual, RCA, and code.

Observed failure:
- Models treat restart/workaround/vendor support as if the underlying issue is solved.

Fable5 behavior to transfer:
- Separate mitigation, permanent fix, prevention, and support boundary.

Trigger:
- RCA, operations manual, support proposal, code hotfix.

Minimal rule:
- Label mitigation and resolution separately; do not call mitigation a root-cause fix.

Target FEF file:
- `modules/RCA.md`
- `modules/Manual.md`
- `reviewers/TechnicalReviewer.md`

Test method:
- Future GT014 RCA fixture with workaround vs root cause.

Do not add:
- Do not force a permanent fix when evidence supports only mitigation; label confidence instead.

Status:
- Candidate

## Task-Specific Candidate Patterns

### Pattern: RFP-First Mapping

Source:
- Fable5 proposal consistency distillation.

Observed failure:
- Proposal reviews judge prose quality before verifying RFP coverage.

Fable5 behavior to transfer:
- Read requirements first, create an RFP-to-proposal mapping, then assess quality.

Trigger:
- Proposal generation or proposal consistency review.

Minimal rule:
- Coverage is checked from RFP to proposal, not from proposal to RFP.

Target FEF file:
- `reviewers/ProposalReviewer.md`
- `workflows/ProposalWorkflow.md`

Test method:
- GT011 requirement coverage dimension.

Do not add:
- Do not require a large table for tiny ad-hoc reviews; list mapping is enough.

Status:
- Candidate for promotion

### Pattern: Repeated Value Cross-Check

Source:
- Fable5 proposal consistency distillation.

Observed failure:
- Dates, versions, quantities, and terms drift across executive summary, body, tables, and appendices.

Fable5 behavior to transfer:
- Extract values that appear in multiple places and compare all occurrences.

Trigger:
- Proposal consistency review, manual review, release notes review.

Minimal rule:
- Values appearing in two or more places must be cross-checked across all locations.

Target FEF file:
- `reviewers/ProposalReviewer.md`

Test method:
- Add table/body mismatch fixture to GT011.

Do not add:
- Do not require exhaustive entity extraction for short documents; focus on dates, versions, quantities, terms.

Status:
- Candidate

### Pattern: Resolution Path with Contradiction

Source:
- Fable5 proposal consistency distillation.

Observed failure:
- Models identify a contradiction but do not help the user decide what to change.

Fable5 behavior to transfer:
- Each contradiction report includes at least one resolution path or decision question.

Trigger:
- Contradiction detection in proposals, architectures, manuals, or plans.

Minimal rule:
- Report contradiction + impact + one practical resolution path.

Target FEF file:
- `reviewers/ProposalReviewer.md`
- `docs/context-protocol.md`

Test method:
- GT001/GT011 contradiction actionability scoring.

Do not add:
- Do not rewrite the whole document unless requested.

Status:
- Candidate for promotion

### Pattern: Connectivity Model First for RHEL/OCP

Source:
- Fable5 RHEL/OpenShift proposal distillation.

Observed failure:
- Models describe cloud-connected features in disconnected or public-sector environments.

Fable5 behavior to transfer:
- Determine connectivity model before proposing patching, subscriptions, Insights, image mirroring, or support workflows.

Trigger:
- RHEL/OpenShift proposal, architecture, or operations work.

Minimal rule:
- State the connectivity model first: connected, proxy/partially connected, or disconnected.

Target FEF file:
- `domains/RHEL.md`
- Future `domains/OpenShift.md` if added.

Test method:
- GT001 disconnected-network scenario.

Do not add:
- Do not hardcode vendor lifecycle or certification facts in prompts; keep those in sourced domain facts.

Status:
- Candidate

### Pattern: Support vs Compliance vs Capability

Source:
- Fable5 RHEL/OpenShift proposal distillation.

Observed failure:
- Models conflate "supports", "is capable of", and "complies/certified".

Fable5 behavior to transfer:
- Keep support scope, technical capability, and compliance/certification claims separate.

Trigger:
- Public-sector, security, compliance, support, and subscription claims.

Minimal rule:
- Do not convert capability or support into compliance/certification without evidence.

Target FEF file:
- `domains/RHEL.md`
- `policies/Evidence.md`

Test method:
- GT001 factual accuracy and `[unverified]` discipline.

Do not add:
- Do not list specific certifications unless sourced with URL/date/version.

Status:
- Candidate for promotion

### Pattern: Manual Three-Part Command Set

Source:
- Fable5 operations manual distillation.

Observed failure:
- Manuals provide commands without expected output or failure behavior.

Fable5 behavior to transfer:
- Operational steps include command, expected output, and what to do if output differs.

Trigger:
- Operations manual/SOP generation.

Minimal rule:
- For non-trivial commands, provide command + expected output/check + mismatch action.

Target FEF file:
- `modules/Manual.md`

Test method:
- Future GT013 manual fixture.

Do not add:
- Do not expand every trivial command; use for validation and state-changing steps.

Status:
- Candidate

### Pattern: Blog Promise-to-Body Match

Source:
- Fable5 blog distillation and S-Core OSSLab style work.

Observed failure:
- Blog titles promise practical insight, comparison, or results that the body does not deliver.

Fable5 behavior to transfer:
- Match title hook, opening promise, section structure, and conclusion takeaway.

Trigger:
- Technical blog outline, draft, or review.

Minimal rule:
- The title promise must be fulfilled by a specific body section and closing takeaway.

Target FEF file:
- `modules/Blog.md`

Test method:
- Manual review for first few blog drafts; golden test deferred as low ROI.

Do not add:
- Do not mimic individual authors or copy OSSLab text; use observable structure only.

Status:
- Candidate

### Pattern: Code Fix Requires Reproduction

Source:
- Fable5 coding workflow distillation.

Observed failure:
- Models patch plausible symptoms without proving the bug or scanning sibling callers.

Fable5 behavior to transfer:
- Reproduce first, fix the root cause, then scan for the same pattern elsewhere.

Trigger:
- Bug fixes and code review.

Minimal rule:
- Bug fix = failing reproduction/check + root-cause fix + one same-pattern scan.

Target FEF file:
- `reviewers/CodeChangeReviewer.md` when code review is the selected FEF task.
- Main coding behavior belongs in the runtime harness, not duplicated in FEF.

Test method:
- Coding Golden Tests 012-014.

Do not add:
- Do not duplicate shared file and tool rules inside the Coding pack.

Status:
- Promoted to the Coding Module, Workflow, and Code Change Reviewer.

## Minimal Promotion Queue

Promote only in this order:

1. `policies/Evidence.md`: add location-bound findings and scoped placeholder discipline.
2. `reviewers/ProposalReviewer.md`: add RFP-first mapping, repeated-value cross-check, contradiction resolution path, severity downshift.
3. `tests/GoldenTest-011.md`: add precision/false-positive scoring before creating new tests.
4. Re-run GT001 and GT011 before promoting RHEL, Manual, RCA, Blog, or Code patterns.

## Permanent Drop List

Do not promote:

- Persona instructions: "act like Fable5", "senior-like", "expert-like".
- Unmeasurable adjectives: "carefully", "thoroughly", "professionally" without a concrete behavior.
- Static factual claims in prompts: lifecycle dates, API references, certification lists.
- Arbitrary numeric quotas unless tied to a golden test.
- Full exemplar answers that would template-match future fixtures.
- Raw Fable5 self-report text as runtime instruction.
- The same rule in multiple files.
