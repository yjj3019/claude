# Simulation Round 4 — 메타리뷰 · 개선 계획

| 항목 | 내용 |
|---|---|
| 대상 저장소 | `yjj3019/claude` |
| 검증 기준 | `origin/main` @ **`b88eecb`** (PR #19/#20/#21/#22 머지 후) |
| 원 피드백 | Round 4 정밀 분석 리포트 (분석만 · 저장소 변경 없음) |
| 성격 | **메타리뷰(동의/부분동의/미수용) + 개선 처방 + PR 순서**. 코드 수정은 본 문서 범위 밖 |
| 작성일 | 2026-09-07 (KST) |

Round 1=구조, Round 2=라우팅·effort, Round 3=고위험 게이트·훅·측정, Round 4=재구현 원리 어긋남 + multi-repo 안전.  
본 문서는 **결정적 라우터·설치 스크립트·훅·파일** 재현 결과에 대한 검토이며 호스트 모델 품질 점수가 아닙니다.

---

## 1. 한줄 결론

Round 4 P0/P1 **대부분 동의·수용**합니다.  
특히 **S4-04**(trivia가 행위동사보다 먼저 실행)와 **S4-09**(`--auto` 부모 스캔 + `rmtree` 덮어쓰기)는 `b88eecb`에서 **재현·확인**되었고, Round 2의 고위험 미매칭 보호와 Kernel 범위 규율이 다른 문으로 다시 열린 상태입니다.

**보정(부분동의):** “Kernel-only”는 **L0(Haiku)로 떨어진다**는 뜻이 아닙니다. 실측은 `effort_tier=L1` / Sonnet 유지 + `kernel_only_safe=true`(Evidence 미부착)입니다. 위험의 본질은 **팩/정책 경량화**이지 모델 티어 붕괴가 아닙니다.

**명시적 미수용·약화:** 비율 과장(“4/5”), `--auto` 자체 폐기 함의, S4-08을 확정 FAIL로 취급, 다중 팩 동시 로드/도메인 silent trim 재도입.

---

## 2. 재현 요약 (`main` @ `b88eecb`)

### 2.1 P0 S4-04 — `detect_task` 실측

| 질문 | risk | kernel_only_safe | unmapped | effort_tier | trivia∧action |
|---|---|---|---|---|---|
| 고객사 운영 환경에 패치 배포 절차 알려줘 | **low** | **true** | true | L1 | trivia=True, action=True, hr_raw=`운영 환경`,`고객`, gated=[] |
| production DB 마이그레이션 순서 알려줘 | **low** | **true** | true | L1 | trivia=True, action=True, hr_raw=`production`, gated=[] |
| 보안 정책 적용 방법이 뭐야? 지금 바로 운영에 반영해야 해 | **low** | **true** | true | L1 | trivia=True, action=True, hr_raw=`보안`, gated=[] |
| what does the production rollout plan look like? apply it today | **low** | **true** | true | L1 | trivia=True, action=True, hr_raw=`production`, gated=[] |

코드 경로 (`scripts/lib/routing.py` · `high_risk_hits`):

1. `_is_definition_or_trivia` **먼저** → `알려줘` / `뭐야` / `what does` 매칭 시 **즉시 []**
2. 그 다음에야 `_has_action_verb`

→ 행위동사(`배포`·`마이그레이션`·`적용`·`rollout`·`apply`)가 있어도 고위험이 꺼집니다.  
대조: `운영 환경에서 고객 데이터 마이그레이션 계획 검토`는 여전히 **high** + Evidence (S3-06 의도 보호는 유지).

### 2.2 P0 S4-09 — 설치 폭발 반경 (코드 확인)

- `discover_sibling_repos`: 기본값이 **`repo_root.parent`의 모든 git 자식** 스캔 (`FEF_SIBLING_PARENT` 미설정 시).
- `--auto` → 호스트 skills **+** sibling 전부 `install_pack`.
- `install_pack`: 대상 `fef-claude/` 존재 시 **`shutil.rmtree` 후 재복사** (확인/`--force` 없음, 백업 없음).
- `AGENTS.md` Multi-repo: *“다른 작업보다 먼저 `--auto`를 한 번 실행하라”* — **실행 지시**.
- README “Sibling targets **(non-destructive)**”는 skills **디렉터리 생성** 문맥이나, 기존 팩 **내용 덮어쓰기**와 모순되어 오해 소지.

### 2.3 P1 스팟체크

| ID | 재현 | 결과 |
|---|---|---|
| **S4-03** | 산문 4문장 → 전부 `coding`; `what is … main.py?` → `unknown` | **확인** (blocklist 양방향 실패) |
| **S4-05** | `노션에 장애 이력 메모 추가`→L2; `원인 분석`→L3; `incidental…`→L2(`incident` 부분문자열); `제안서…메모`→L2 | **확인** |
| **S4-06** | `config/routes.json` 최종 커밋 `e5471ae`(2026-08-05); R2/R3 게이트는 `routing.py` 하드코딩 튜플 | **확인** |
| **S4-08** | `extract_exit_code`는 `tool_response`/`tool_output`/… 만; **`tool_result` → None** | 코드 상 키 공백 **확인**, 실호스트 페이로드는 **UNVERIFIED 유지** |

---

## 3. Round 2/3 메타리뷰 원칙 (이번 처방의 고정축)

1. **고위험 → L0 금지 + L1 바닥**. **무조건 L2/Opus floor 금지**.
2. **고위험 미매칭 → Evidence + `kernel_only_safe=false`** (R2-P0). trivia 가드가 이 문을 다시 열면 안 됨.
3. **도메인 silent trim 금지** (top-N + 드롭 경고).
4. **복합의도 = 고지만** (다중 팩 동시 로드로 확대하지 않음).
5. **원리 > 예문 암기**: allowlist/결합형 신호, blocklist·단독 명사 과적합 지양.
6. **설정 단일 권위 + validator** — 행동 게이트가 Python 전용 하드코딩으로만 늘면 설계 원칙 위반.
7. **설치/쓰기 = 최소 범위·opt-in** — Assessment ≠ mutation; AGENTS는 실행 강제가 아니라 안내.

---

## 4. 항목별 판정 · 처방

범례: ✅ 수용 · ⚠️ 부분수용(서술 보정) · ❌ 미수용 · 🧾 백로그 · 🔍 검증 대기

| ID | 등급 | 검증 | 판정 | 처방 요지 |
|---|---|---|---|---|
| **S4-09** | P0 | ✅ | ✅ | sibling **opt-in만**; 기존 팩 덮어쓰기 방지; AGENTS/README 문구 수정 |
| **S4-04** | P0 | ✅ | ⚠️ | 순서 뒤집기 + trivia 축소 **수용**. “Kernel-only=L0” 서술은 **보정** |
| **S4-03** | P1 | ✅ | ✅ | coding fallback을 **코드 문맥 allowlist**로 전환 |
| **S4-05** | P1 | ✅ | ✅ | L2/L3 단독 명사 제거·결합형; ASCII **단어 경계** |
| **S4-06** | P1 | ✅ | ✅ | 게이트 목록을 `routes.json`(또는 동등 config)로 이전 + validate |
| **S4-08** | P1 | 코드만 | 🔍 | 실호스트 1회 확인 전 확정 FAIL **미수용**; 방어적 키 추가는 허용 |
| **S4-01** | P2 | 미심층 | 🧾 | `여러 파일`·ASCII 하이픈 compact — 백로그 |
| **S4-07** | P2 | 미심층 | 🧾 | 도메인 어순 민감 — 문서화 또는 `rank` (silent trim 없이) |
| **S4-02/10** | — | PASS 인용 | — | Round 3 회귀·설치 검증 — 본 계획에서 재작업 없음 |

### 4.1 S4-09 — multi-repo auto-install (P0, 최우선)

**동의:** 폭발 반경·자기모순·AGENTS 주입 경로 지적은 타당.

**구체 처방 (한 PR):**

1. **Sibling 설치는 opt-in만**
   - 기본 `--auto` = **호스트 skills만** (현재 `detect_targets` 경로 유지).
   - 부모 디렉터리 자동 스캔(`repo_root.parent` iterdir) **제거** 또는 `--scan-sibling-parent` 같은 **명시 플래그**로만.
   - `--siblings PATH` / `FEF_SIBLING_ROOTS` / `--siblings-only`는 유지.
2. **덮어쓰기 안전장치**
   - 대상 `…/fef-claude/` 존재 시 기본 **중단** + 안내; 재설치는 `--force`(또는 내용 hash 동일 시 skip).
   - `rmtree` 전 백업은 필수는 아니나, 최소 “존재하면 거부”는 필수.
3. **문서**
   - `AGENTS.md` Multi-repo: *“실행하라”* → *“사용자가 형제 설치를 원할 때만 … `--siblings` / env로 설치할 수 있다”*.
   - README/Installation: “non-destructive”를 **디렉터리 생성**과 **기존 팩 보존**으로 분리 서술; dry-run 권장.
4. **회귀 테스트**
   - tmp parent 아래 `claude/` + 무관 git repo 3개: `--auto`가 sibling에 **쓰지 않음**.
   - 기존 dest 있으면 `--force` 없이 exit≠0 / 내용 불변.
   - `--siblings <path>`만 해당 경로에 설치.

**미수용:** `--auto` 자체를 없애라는 함의. 호스트 감지 설치는 유지.

### 4.2 S4-04 — trivia가 고위험을 강등 (P0)

**부분동의:** 결함·원인·수정 방향 **수용**. 영향 서술만 보정.

- 실측 4문장 모두 `risk=low`, `kernel_only_safe=true`, `effort_tier=L1`.
- Round 2 P0(고위험 미매칭 → Evidence)가 **다른 문(trivia short-circuit)**으로 재개방된 것은 동의.
- **보정:** 모델이 Haiku로 붕괴한 것이 아님. 문제는 Evidence 없는 light config.

**구체 처방:**

```text
high_risk_hits:
  1) keyword hits 없으면 []
  2) action_verb 있으면 → hits 유지 (trivia 무시)
  3) else if definition/trivia(결합형) → []
  4) else if non-question → hits
  5) else []
```

- `_DEFINITION_OR_TRIVIA_PATTERNS`에서 **단독** `알려줘` / `뭐야` / 과도한 `what does` 제거.
- 유지 예: `뜻이 뭐야`, `차이가 뭐야`, `규칙이 뭐야`, `what is the meaning`, `meaning of`.
- S3-06 회귀 세트 **유지**: 전화번호·단어 뜻·이름 규칙은 low; 마이그레이션 계획 검토는 high.

**회귀 고정 (필수):**

| 기대 | 예시 |
|---|---|
| high + kos=false | 본 리포트 4문장 + `운영 환경에서 고객 데이터 마이그레이션 계획 검토` |
| low | `고객센터 전화번호 좀 알려줘`, `production 이라는 단어 뜻이 뭐야?`, `보안 그룹 이름 규칙이 뭐야?` |

### 4.3 S4-03 — coding fallback blocklist (P1)

**동의.** 원리(약한 신호는 **코드 문맥이 있을 때만**)로 재정렬.

**처방:**

- `_CODING_FALLBACK_BLOCKERS` 폐기 또는 최소화.
- coding 라우트에 `fallback_requires_any` / `fallback_requires_pattern` (경로 `*.py`/`*.ts`/…, `def `/`class `/`function `, `stack trace`, `traceback` 등).
- 산문(`회의록…에러`, `이메일…오류 고쳐줘`) → **non-coding**; `what is causing this error in main.py?` → coding 또는 최소 unknown이 아닌 디버그 경로.

### 4.4 S4-05 — 티어 신호 과대 (P1)

**동의.**

**처방:**

- L2에서 단독 `장애` / `제안서` / 느슨한 `incident` 제거 → `장애 원인`·`장애 대응`·`제안서 작성`·`incident response` 등 결합형.
- L3 `원인 분석` → L2로 하향; L3는 `근본 원인`·`deep rca`·`root cause` 중심.
- `_signal_in`의 ASCII는 **단어 경계** (`incident` ≠ `incidental`). KO는 기존 compact 유지.
- 고정 테스트: `노션에 장애 이력 메모 추가` → **L0**(또는 L1 이하, Haiku 게이트 의도 충족); `incidental cleanup of the README` → L1; `프로덕션 장애 근본 원인 분석` → L3 유지.

### 4.5 S4-06 — 설정 vs 코드 권위 (P1)

**동의.** R2/R3 게이트가 `routes.json` 밖에만 있음.

**처방 (S4-03/05와 한 묶음 권장):**

- `routes.json`에 예:
  - `high_risk_gate.action_verbs`
  - `high_risk_gate.trivia_patterns` (결합형만)
  - coding 라우트 `fallback_requires_any` / `fallback_requires_pattern`
  - (선택) `effort_signals` L0–L3 — 또는 `config/effort_signals.json` 분리
- `validate_routes.py`(또는 신설 validate): 각 목록이 **의도 샘플**에서 발화/비발화하는지 검사.
- `routing.py` / `adaptive_effort.py`는 config 로드만.

**주의:** 한 PR에 “이사 + 행동 수정”을 넣되, 커밋을 (1) config 이전·동작 동등 (2) 원리 수정으로 나누면 리뷰가 쉽습니다.

### 4.6 S4-08 — 훅 페이로드 키 (P1, 검증 대기)

**부분동의:** fail-closed + fixture 자기참조 위험은 인정.  
**미수용:** 실호스트 미확인 상태에서 “프로덕션에서 마커가 영원히 안 쓰인다”를 **확정 FAIL**로 고정하는 것.

**처방:**

1. Claude Code에서 `.md` 수정 → `validate_repository.py` → `.claude/.test-run-marker` 여부 **1회 실측**.
2. 키가 다르면 `extract_exit_code`에 실제 키 추가 + 테스트 fixture를 실측 스키마에 맞춤.
3. 확정 전 **방어적**으로 `tool_result` 등 후보를 넣는 것은 허용(과잉 크레딧만 피하도록 exit=0 조건 유지).

### 4.7 P2 (S4-01 / S4-07)

- **S4-01:** `여러 파일` L2 동의어; ASCII 하이픈 compact — 한 줄 패치 백로그.
- **S4-07:** 어순=팩 민감성을 docs에 명시 **또는** domain `rank` 도입. **silent trim 금지** 유지.

---

## 5. 명시적 미수용 · 보정

1. **“알려줘 한 단어 → Kernel-only(경량) = 모델도 붕괴”**  
   → **팩/Evidence 경로 붕괴는 수용**. effort는 L1 유지 → 비용 과장 보정.
2. **“4/5” 비율**  
   → 첨부 본문은 실패 예시 4건. 우리는 **4/4 재현**. 비율 수사 약화.
3. **`--auto` 전면 폐기**  
   → **미수용**. sibling 자동 스캔·강제 덮어쓰기·AGENTS 실행 지시만 제거/완화.
4. **S4-08 확정 FAIL**  
   → **미수용**(UNVERIFIED). 코드 키 공백은 인정, 호스트 확정 후 패치.
5. **다중 라우트 동시 로드 / 도메인 silent trim**  
   → Round 2/3과 동일하게 **미수용**.
6. **고위험 blanket L2**  
   → **계속 미수용**.

---

## 6. 권장 PR 순서

| 순번 | PR | 포함 | 이유 |
|---|---|---|---|
| **1** | `fix/sim-round4-install-safety` | **S4-09** | 이미 main에 머지된 쓰기 폭발 반경 — 안전 최우선 |
| **2** | `fix/sim-round4-highrisk-trivia` | **S4-04** (+ S3-06 회귀 테스트 확장) | R2-P0 문 재개방; 소규모·검증 명확 |
| **3** | `fix/sim-round4-routing-authority` | **S4-03 + S4-05 + S4-06** | 하드코딩·예문 과적합·권위 분리 동일 뿌리 |
| **4** | `fix/sim-round4-hooks-payload` | **S4-08** | 실호스트 확인 후에만 코드 확정 |
| — | 백로그 | S4-01, S4-07 | P2 |

각 PR: `unittest` + `validate_repository` / `validate_routes` 그린 필수. 푸시·머지는 상위 에이전트/관리자 결정(본 문서는 로컬 계획만).

---

## 7. 성공 기준 · 회귀 락

### 7.1 S4-09
- [ ] `--auto`가 parent 아래 **미지정** git repo에 파일을 만들지 않음
- [ ] 기존 `fef-claude/`는 `--force` 없이 불변
- [ ] `AGENTS.md`에 선행 강제 실행 문구 없음
- [ ] README가 overwrite 정책을 명시

### 7.2 S4-04
- [ ] 위 4문장: `risk=high`, `kernel_only_safe=false`, Evidence 부착
- [ ] S3-06 benign 3문장: `risk≠high`
- [ ] `운영 환경에서 고객 데이터 마이그레이션 계획 검토`: high 유지
- [ ] 고위험이라도 **effort floor는 L1** (blanket L2 없음)

### 7.3 S4-03 / 05 / 06
- [ ] 산문 4문장 ≠ coding; `main.py` 디버그 질문 ≥ coding 또는 동등 디버그 경로
- [ ] Notion 장애 메모 ≤ L1(의도 L0); incidental ≠ L2; 근본 원인 분석 = L3
- [ ] 게이트 목록이 config에 있고 validator가 샘플을 검사
- [ ] `routes.json` mtime/내용이 게이트 변경과 함께 갱신됨

### 7.4 S4-08
- [ ] 실측 페이로드 키 문서화
- [ ] 해당 키로 marker 기록 E2E 테스트

### 7.5 전역
- [ ] Round 2/3 공유 리포트 회귀 표(KO 티어, also_matched, cold-start 예산, 훅 세그먼트 앵커) 통과
- [ ] unittest 전량 + `validate_repository` pass

---

## 8. 한계

- 본 계획도 **결정적 스크립트 관찰**이며 모델 응답 품질이 아님.
- S4-09 폭발 반경은 코드 경로로 확인; 실제 사용자 디렉터리는 미접근.
- S4-08 공식 호스트 스키마는 미확정.
- Round 4 원문 “4/5” 등 일부 수사는 재현 세트와 표기 불일치 가능 → 위 보정 따름.

---

## 9. 다음 액션 (상위 에이전트)

1. 본 파일을 이해관계자와 공유(푸시 여부는 선택; **현재 로컬 미커밋 가정**).
2. PR1(S4-09)부터 구현·리뷰.
3. PR2(S4-04) 직후 benign/고위험 표를 CI에 고정.
4. PR3 묶음에서 config 이전과 원리 수정을 커밋 분리.
5. S4-08은 호스트 실측 로그를 이슈에 붙인 뒤 패치.

