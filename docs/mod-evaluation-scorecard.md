<a id="mod-성능-평가-지표-수치"></a>
# Mod Performance Evaluation Metrics (Numeric)

Rate results with a Mod against the repository's current baseline run on a **1–5 scale**, then summarize them as a weighted score. These criteria and weights are a custom decision tool for this repository, not an official benchmark or verified evidence of improvement. For the distinction between features and designs, see [Mods and Three-Tier Delegation](mods-and-tiered-agents.md).

<a id="1-차원별-점수-규모"></a>
## 1. Scoring Dimensions

| ID | Dimension | Weight | Maximum | Measurement |
|----|------|--------|------|-----------|
| M1 | Context efficiency | 15% | 15 | Percentage change in main context tokens |
| M2 | Cost | 15% | 15 | Percentage change in billed tokens per task |
| M3 | Latency | 10% | 10 | Percentage reduction in total elapsed time |
| M4 | Verification confidence | 15% | 15 | Reduction in omissions and false positives |
| M5 | Review quality | 15% | 15 | Detection rate for important issues |
| M6 | Development friction | 10% | 10 | Reduction in additional actions and retries |
| M7 | Security surface | 10% | 10 | Risk score for new permissions and unsandboxed execution |
| M8 | Stability | 10% | 10 | Rate of session failures and partial loads |
| | **Total** | **100%** | **100** | |

<a id="2-점수-환산"></a>
## 2. Score Conversion

Rate each dimension from 1–5, then apply its weight.

```
Dimension score = (1–5 rating / 5) × (weight × 100)
Total = Σ dimension scores   (maximum 100)
```

Enter weights as fractions, such as 15% = 0.15. If all dimensions are rated from 1–5, the total ranges from 20–100; if all dimensions match the baseline with a rating of 3, the total is 60. This score is not a percentage improvement in performance. Leave unmeasured items as N/A and do not assign a total or verdict.

| 1–5 rating | Meaning | Example (M1, weight 15%) |
|---------|------|----------------------|
| 5 | Excellent | 15.0 |
| 4 | Good | 12.0 |
| 3 | Unchanged | 9.0 |
| 2 | Below baseline | 6.0 |
| 1 | Poor | 3.0 |

<a id="3-판정-기준-수치"></a>
## 3. Decision Criteria (Numeric)

| Total | Verdict | Conditions |
|------|------|------|
| **80–100** | Adopt | All dimensions ≥ 3, with no critical M7 issue |
| **65–100**, when adoption conditions are not met | Trial | M4·M7·M8 ≥ 3, with no critical M7 issue |
| **20–64**, or a required condition fails | Reject | Insufficient total, M4·M7·M8 < 3, or a critical M7 issue |

Critical security issues and failed required conditions take precedence over the total. These thresholds support local adoption decisions; they are not statistical criteria that demonstrate improvement.

<a id="4-측정-기록"></a>
## 4. Measurement Records

Enter scores only after obtaining original evidence from actual baseline and Mod-enabled runs. Do not reuse hypothetical performance scores or savings targets as measurement results.

<a id="5-baseline-비교-항목"></a>
<a id="5-기준-실행-비교-항목"></a>
## 5. Baseline Comparison Items

Repeat measurements with the same tasks, versions, permissions, and evaluation criteria. Include cache conditions, failures, and retries.

| Metric | Evidence to record |
|------|-------------|
| Context | Main and subagent inputs and outputs, and aggregation scope |
| Cost | All calls, cache writes/reads, retries, and review costs |
| Completion time | Start and end times, and whether cold starts are included |
| Verification and quality | Counts of successes, failures, omissions, and tasks; regression results |
| Retries and stability | Failures, cancellations, partial loads, and sample size |

<a id="6-기록-형식"></a>
## 6. Record Format

```json
{
  "date": "YYYY-MM-DD",
  "mod_name": "",
  "scores_1_5": { "M1": null, "M2": null, "M3": null, "M4": null, "M5": null, "M6": null, "M7": null, "M8": null },
  "weighted_total": null,
  "verdict": "unmeasured",
  "metrics": {},
  "evidence": [],
  "limitations": []
}
```

Do not use example values before taking actual measurements. Follow the protocol in [mod-evaluation-metrics.md](mod-evaluation-metrics.md).
