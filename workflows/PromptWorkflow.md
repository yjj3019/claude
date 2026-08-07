# Prompt Improvement Workflow

Use the Prompt Contract in `modules/PromptEngineering.md` as the field checklist while working through these steps: Role/Task/Context map to steps 1-3, Tools to step 2, Constraints to steps 5 and 7, Output/Verification/Stop-Escalation to step 8.

1. Identify the operational objective, target users, and non-goals.
2. Identify the target model, runtime, available tools, context limits, and platform policies.
3. Inventory existing instructions and classify them as permanent, task-specific, runtime-specific, or redundant.
4. Identify observed failure modes; do not add broad rules without a concrete failure or risk.
5. Define instruction precedence, evidence priority, and untrusted-content handling.
6. Replace vague personas and slogans with trigger-action rules.
7. Define file, tool, freshness, uncertainty, approval, and failure behavior only where the runtime supports them.
8. Define the output contract, completion criteria, and degraded-mode response.
9. Minimize duplication and move optional capabilities into modules or policies.
10. Build representative tests, including normal, ambiguous, conflicting, tool-failure, and adversarial cases.
11. Compare baseline and revised prompt results using the same tasks and scoring rubric.
12. Promote only rules that measurably improve quality or reduce variance; document removal criteria. See `modules/PromptEngineering.md`'s "Recording a Promoted Rule's Evaluation" for where that evidence lives.
