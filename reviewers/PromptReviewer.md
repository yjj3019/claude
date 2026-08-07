# Prompt Reviewer

## Purpose

Review a prompt once for clarity, bounded behavior, and measurable output requirements.

Review for:

- ambiguity
- overbroad role instructions
- missing output contract — check against the ten fields in `modules/PromptEngineering.md`'s Prompt Contract (Role/Task/Success/Context/Constraints/Tools/Examples/Output/Verification/Stop-Escalation)
- hallucination risk
- tool ambiguity
- lack of evaluation criteria — a promoted rule needs a record per `modules/PromptEngineering.md`'s "Recording a Promoted Rule's Evaluation"
- excessive complexity
