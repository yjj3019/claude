# Mod Performance Evaluation Metrics

Use this scorecard when evaluating whether adding a Claude Code **Mod** to this repository improves outcomes versus the current settings-hook + Skills + Agents baseline.

Mods run inside Claude Code (JS/TS event handlers). They are not sandboxed and increase the trust surface. Measure before adopting.

This is a repository-defined evaluation protocol, not an official benchmark or a
measured improvement claim. See [official capabilities versus custom design](mods-and-tiered-agents.md).

## Baseline (current)

| Layer | Implementation |
|-------|----------------|
| Instructions | `CLAUDE.md` + selective packs |
| Skills | `skills/coding`, `skills/rca` |
| Agents | `.claude/agents/*` reviewers |
| Hooks | `hooks/hooks.json` (shell, verification reminders) |
| Routing | `config/routes.json` + `scripts/detect_task.py` |

## Evaluation dimensions

Score each dimension 1–5 (1 = worse than baseline, 3 = same, 5 = clearly better). Record evidence and a task-specific scoring rubric, not opinion. Unmeasured dimensions remain N/A; do not assign a verdict until all required evidence is available.

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
| **Adopt** | Weighted total ≥ 80, every dimension ≥ 3, no critical M7 issue |
| **Trial** | Weighted total ≥ 65, Adopt conditions not met, M4/M7/M8 ≥ 3, no critical M7 issue |
| **Reject** | Weighted total < 65, a critical M7 issue, or M4/M7/M8 < 3 |

Use the weights and formula in the [scorecard](mod-evaluation-scorecard.md), the
single scoring reference. These local thresholds are not statistical confidence
levels; security and verification/stability failures override the total.

Critical M7 examples: mod can approve tool calls that settings hooks would block; reads secrets without necessity; network calls not required for the feature.

## Minimum test protocol

1. Record exact host and candidate versions; verify the required APIs and UI on that host. A version threshold alone does not prove that a candidate works.
2. Hold model, effort, task prompt, initial workspace, active instructions/plugins, tool permissions, verification-wrapper availability, sandbox and grading conditions constant. Change only the candidate being evaluated.
3. Predeclare matched repetitions and alternate or randomize arm order using fresh isolated sessions. Cover code change + verification, RCA, documentation, multi-file edits and simple Q&A. A single pair is exploratory evidence, not a general improvement claim.
4. Capture per-run context tokens, usage, measured cost source, wall time, cache reads/writes and cold/warm status, verification reminder accuracy and review results against a fixed rubric. Mark unavailable metrics as missing; separate cold and warm comparisons.
5. Grade correctness, safety and verification before efficiency. Report denominators explicitly; do not silently discard timeouts, crashes or incomplete runs. Distinguish tests being present, tests executing successfully, and tests detecting regressions or injected faults.
6. Run `claude plugin validate` on the mod and archive the hooks/calls output. This is static inspection, not a security certification; review code and actual data access separately.
7. Retain raw per-run results, cwd, relevant non-secret settings and grading rules for recomputation. Label excluded samples and reasons; do not generalize savings from a single session or transfer another project's benchmark percentages.

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
  "tasks": null,
  "scores_1_5": { "M1": null, "M2": null, "M3": null, "M4": null, "M5": null, "M6": null, "M7": null, "M8": null },
  "weighted_total": null,
  "verdict": "unmeasured",
  "evidence": "paths or notes",
  "notes": ""
}
```

Store completed records under `docs/evaluations/` (create when first used). Do not claim improvement without the protocol above.
