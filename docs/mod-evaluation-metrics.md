# Mod Performance Evaluation Metrics

Use this scorecard when evaluating whether adding a Claude Code **Mod** to this repository improves outcomes versus the current settings-hook + Skills + Agents baseline.

Mods run inside Claude Code (JS/TS event handlers). They are not sandboxed and increase the trust surface. Measure before adopting.

## Baseline (current)

| Layer | Implementation |
|-------|----------------|
| Instructions | `CLAUDE.md` + selective packs |
| Skills | `skills/fef-coding`, `skills/fef-rca` |
| Agents | `.claude/agents/*` reviewers |
| Hooks | `hooks/hooks.json` (shell, verification reminders) |
| Routing | `config/routes.json` + `scripts/detect_task.py` |

## Evaluation dimensions

Score each dimension 1–5 (1 = worse than baseline, 3 = same, 5 = clearly better). Record evidence, not opinion.

| ID | Dimension | What to measure | How to measure |
|----|-----------|-----------------|----------------|
| M1 | Context efficiency | Tokens in main context per typical task | `/context` or usage export; compare same task with/without mod |
| M2 | Cost | Billed tokens / estimated cost per task | `/usage` or provider billing over N identical tasks |
| M3 | Latency | Time to first useful result and total task time | Wall clock; exclude cold start if comparing warm sessions |
| M4 | Verification reliability | False pass / missed verification rate | Count Stop-hook reminders vs actual changed trees; golden tests |
| M5 | Review quality | Critical issues found / missed | Same change set reviewed with and without mod-assisted path |
| M6 | Developer friction | Extra steps, reload, failures | Count of `/reload-plugins`, validate failures, unexplained no-ops |
| M7 | Security surface | New privileges and data access | List hooks/calls from `claude plugin validate`; note unsandboxed reach |
| M8 | Stability | Crashes, partial loads, version skew | Session error rate over 20+ sessions on target Claude Code version |

## Verdict rules

| Verdict | Condition |
|---------|-----------|
| **Adopt** | M1–M5 average ≥ 3.5, no M7 regression, M8 ≥ 3 |
| **Trial** | Average ≥ 3.0 and M7 acceptable with documented mitigations |
| **Reject** | Any critical M7 issue, or average < 3.0, or M4 worse than baseline |

Critical M7 examples: mod can approve tool calls that settings hooks would block; reads secrets without necessity; network calls not required for the feature.

## Minimum test protocol

1. Fix Claude Code version (≥ 2.1.287 CLI) and record it.
2. Run the same 5 tasks twice: baseline (mod disabled) and with mod.
3. Tasks should cover: code change + verification, RCA-style investigation, documentation edit, multi-file edit, simple Q&A.
4. Capture for each run: context tokens, usage, wall time, verification reminder accuracy, subjective review completeness.
5. Run `claude plugin validate` on the mod and archive the hooks/calls output.
6. Do not treat a single session as sufficient.

## Suggested first mod candidates (optional)

Only evaluate if a concrete gap exists:

| Candidate | Goal | Primary metrics |
|-----------|------|-----------------|
| Verification status band | Show last verification result above prompt | M4, M6 |
| Reviewer invocation guard | Prompt before skipping code-change-reviewer on non-trivial diffs | M5, M6 |
| Load-limit reminder | Warn when more than one module/reviewer is about to be loaded | M1, M4 |

## Record template

```json
{
  "date": "YYYY-MM-DD",
  "claude_code_version": "",
  "mod_name": "",
  "tasks": 5,
  "scores": { "M1": 0, "M2": 0, "M3": 0, "M4": 0, "M5": 0, "M6": 0, "M7": 0, "M8": 0 },
  "average": 0,
  "verdict": "adopt|trial|reject",
  "evidence": "paths or notes",
  "notes": ""
}
```

Store completed records under `docs/evaluations/` (create when first used). Do not claim improvement without the protocol above.
