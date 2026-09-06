# Simulation Round 2 — Behavioral Routing Fixes (2026-09-06)

Baseline: `origin/main` @ `fd0dc07`. Branch: `fix/sim-10-round2`.

Mechanical routing/effort simulations + meta-review prescriptions (not the original write-up’s blanket high-risk→L2 floor / silent domain trim).

Timezone: recorded 2026-09-06 evening KST (UTC+9); applied 2026-09-07 KST.

## Defects fixed

| ID | Severity | Fix |
|---|---|---|
| R2-P0-KO-TIER-BLIND | P0 | KO (+ spacing-tolerant) L2/L3/L1 signals in `adaptive_effort.py` so `프로덕션 장애 근본 원인 분석` tracks EN L3 |
| R2-P0-UNMAPPED-HIGHRISK | P0 | `high_risk_keywords` before unmapped return; high-risk → Evidence + `kernel_only_safe=false` |
| R2-P1-RISK-TIER-DECOUPLED | P1 | High risk bans L0 / floors L1 only; **no** blanket L2/Opus floor; `detect_task` emits `effort_tier`/`model`/`effort_reason` |
| R2-P1-FALLBACK-OVERFIRE | P1 | Gate coding fallbacks for Q&A/typo prose |
| R2-P1-DOMAIN-OVERFLOW | P1 | Top-2 domains by rank + warning naming drops (not silent trim; not hard-exit preferred) |
| R2-P1-CI-EN-ONLY-SAMPLES | P1 | KO + high-risk unmapped + fallback-negative samples in validate/tests |
| R2-P2-L0-LEAK | P2 | Substantial packs / high-risk cannot stay L0 |
| R2-P2-KO-SPACING | P2 | Spacing/separator-tolerant KO matching |
| R2-P2-HEADROOM | P2 | CLAUDE.md kept ≤7000B; detail in adaptive-effort / loading-map |

## Intentional deviations from original write-up

- **No blanket high-risk → L2/Opus floor.** Meta-review: floor at L1/Sonnet; L2 only with L2/L3 text signals.
- **Domain overflow:** prefer top-2 + explicit drop warning over fail-loud exit 1 (Integrity policies retained).

## Smoke before/after (P0)

| Ask | Pre-fix | Post-fix |
|---|---|---|
| `프로덕션 장애 근본 원인 분석` | effort L1 (EN root-cause path was L3) | effort **L3** |
| `운영 환경에서 고객 데이터 마이그레이션 계획 검토` | unmapped, risk=low, kernel_only_safe=true | unmapped, risk=**high**, Evidence attached, kernel_only_safe=**false** |
