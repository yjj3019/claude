# Simulation Round 4 — 조치 응답 (accepted items)

| 항목 | 내용 |
|---|---|
| 대상 | `yjj3019/claude` |
| 기준 | `origin/main` @ `b88eecb` |
| 브랜치 | `fix/sim-10-round4` |
| 작성일 | 2026-09-07 (KST) |

메타리뷰 계획: `docs/simulation-round4-improvement-plan-2026-09-07.md`.

## 수용 · 구현

| ID | 판정 | 조치 |
|---|---|---|
| **S4-09** | ✅ | `--auto` = 호스트 skills만. 형제 설치 opt-in (`--siblings` / `FEF_SIBLING_ROOTS` / `--siblings-only` / `--scan-sibling-parent`). 기존 `fef-claude/`는 `--force` 없으면 거부(동일 해시 skip). AGENTS/README/Installation 문구 수정. |
| **S4-04** | ⚠️→✅ | `high_risk_hits`에서 **행위동사 우선**; trivia는 무행위 ∧ 의문/정의형일 때만. 단독 `알려줘`/`뭐야` trivia 제거(질문 마커로만). 4문장 회귀: `risk=high`, `kernel_only_safe=false`. |
| **S4-03** | ✅ | coding fallback = keyword ∧ (code-context tokens ∨ path regex). `fallback_requires_any` / `fallback_requires_pattern` in `routes.json`. |
| **S4-05** | ✅ | L2/L3 단독 명사 제거·결합형; `원인 분석`→L2; ASCII 단어 경계(`incident`≠`incidental`). |
| **S4-06** | ✅ | `high_risk_gate` / coding fallback requires / `effort_signals` → `config/routes.json`; `validate_routes`가 config 구동 샘플 검사. |
| **S4-08** | 🔍 | 방어적으로 `tool_result` / top-level `exit_code` 수용. **호스트 실측 스키마는 UNVERIFIED** — 확정 FAIL 아님. |

## 미수용 · 보정 (계획과 동일)

- `--auto` 전면 폐기 미수용 (형제 자동 스캔·강제 덮어쓰기만 제거).
- “Kernel-only = L0/Haiku 붕괴” 서술 보정 (실측은 Evidence 경로·팩 경량화).
- S4-08 확정 FAIL 미수용 (UNVERIFIED).
- 다중 팩 동시 로드 / 도메인 silent trim / 고위험 blanket L2 계속 미수용.

## P2 백로그

- S4-01 / bug self-satisfy / KO·EN tier parity / ASCII hyphen compact — **잔여 PR** `fix/sim-round4-p2-residuals`에서 처리.
- S4-07 (도메인 어순) — **문서화만** (`docs/loading-map.md`): mention-order 유지; optional `rank`는 미래. silent trim 미구현.
