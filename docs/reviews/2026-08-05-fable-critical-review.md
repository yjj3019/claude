# Critical Repository Review — Fable Model (2026-08-05)

Independent review requested by the user ("git 저장소의 내용을 fable 모델을 통해서 비판적인 분석 진행해줘"), run as a `general-purpose` subagent with `model: fable`, scoped to the whole repository rather than a specific diff. Reproduced here verbatim (Korean original) as a committed artifact, since the prior 10-pass architecture review (`2026-08-04-architecture-review-10x.md`) existed only as a chat-session synthesis until that gap was identified — see this review's own M4 finding below, which flagged exactly that problem.

**Outcome of this review's Critical finding (C1):** independently reproduced in-session the same day. A subagent given only the bare instruction "Fix the bug." (no repository context, no bug description) autonomously ran this repo's unit test suite and validators, then refused to guess and asked for a bug report, explicitly citing "this workspace's rules (no unilateral assumptions — guessing is a defect)" — a paraphrase of `AGENTS.md` §6 obtainable only via auto-injected project context. This confirms Claude Code (and Agent-tool subagents operating in this repo's working directory) auto-load `CLAUDE.md`/`AGENTS.md` regardless of the literal prompt given, invalidating the pack-ablation experiment's "kernel_only" arm across all 54 recorded runs. See `PROGRESS.md`'s 2026-08-05 correction entry.

---

## 직접 검증한 사실 (재현 완료)

- `batch-2026-08-04.json` / `batch-2026-08-05-gt031.json`은 PROGRESS의 24/24, 3/3 수치와 정확히 일치.
- GT031 정답 패치 cap 100/exit 0, pristine exit 1 — 로컬 재실행으로 재현됨.
- `sync_kernel.py --check` 통과, `validate_routes.py`(9 routes)·`validate_repository.py` 통과, 전체 unittest 스위트 exit 0 (단, "154개" 개수 자체는 출력 캡처 한계로 [unverified]).
- `2db68f1` diff는 커밋 메시지 내용(CI 분리, `커널` 키워드 제거, `운영`→`운영 환경`, priority 필드)과 일치.

## 발견 사항

### Critical

**C1. pack-ablation의 두 arm이 실제로는 "팩 계층 유무"를 분리하지 못함 — 실험 설계 자체가 무효에 가깝다.**
- `docs/ablation-runbook.md:14-19`: 두 arm 모두 `main` 브랜치의 이 저장소 안에서 세션을 열고, arm은 **붙여넣는 프롬프트 파일로만** 구분된다. 그런데 Claude Code 세션(및 Agent-tool 서브에이전트 — 지금 이 세션에서 실증되듯)은 이 저장소의 `CLAUDE.md`(인라인 커널 + Autoload Protocol + loading-map 지시)를 자동 주입받는다. 즉 **"kernel_only" arm도 커널만 로드된 것이 아니라, full_fef와 동일한 FEF 부트스트랩 환경에서 실행**되었고, Autoload Protocol에 따라 coding 팩을 스스로 로드했을 수도 있다. 실제 로드된 컨텍스트는 어느 run에서도 기록되지 않았다.
- `docs/pack-ablation-protocol.md:9`의 "K arm: no loading-map, no pack files, Kernel behavior only"는 runbook의 실행 방식 하에서 성립하지 않는 주장이다.
- 추가 교란: arm 차이가 팩 로딩만이 아니라 **프롬프트 내용 자체**다. `tests/prompts/GT012-fef.md:6-11`(GT031도 동일)은 "smallest shared root cause / sibling 스캔 / 의존성 금지" 등 5개 명시 요구를 담고, baseline엔 없다. 설령 격차가 나왔더라도 팩 계층 효과와 프롬프트 문구 효과를 분리할 수 없는 설계다.
- PROGRESS는 full_fef arm의 fidelity 캐비앳(PROGRESS.md:10)은 적어놨지만, **kernel_only arm의 오염(역방향 문제)은 어디에도 언급이 없다**. "두 독립 축에서 완전 동률"이라는 결론은 "동률이 구조적으로 거의 보장된 설계"에서 나온 것이므로, 팩 계층에 대한 null 증거로서의 가치가 문서가 시사하는 것보다 훨씬 낮다.

### Major

**M1. 통계적 검정력 0 + 천장 효과가 설계에 내장됨.** 8개 fixture 전부 단일 함수의 자명한 버그(PROGRESS.md:10이 자인). 양 arm 24/24 = 100%인 표본에서는 어떤 차이도 검출 불가. GT031은 arm당 N=3 — 진짜 성공률이 90%여도 3연속 성공 확률 73%. "두 독립 축" 프레이밍도 과장: GT031의 판별자(`new_dependency_candidates`)는 6개 run 전부 미발화 — **판별 사건이 0건**이므로 의존성 회피 축에 대한 정보량이 사실상 없다(둘 다 유혹조차 안 받았다는 것만 확인).

**M2. GT031 설계 타당성.** `tests/fixtures/GT031-code/validators.py:3` — 9줄 파일에 문자 하나 빠진 regex + 기대 동작을 명시한 테스트 파일. "모델이 email_validator로 과잉 해결한다"는 시나리오는 그린필드 검증 과제에서의 현상이지, 최소 수정이 눈앞에 보이는 fixture에는 적용되지 않는다. 미발화(0/6)는 예측 가능한 결과였다. 게다가 fef 프롬프트 자체에 "Do not add dependencies"(GT031-fef.md:10)가 있어, 격차가 나왔어도 그 한 줄 대 팩 계층을 구분 못한다.

**M3. 사전등록 프로토콜의 실행 중 이탈.** `pack-ablation-protocol.md:18`과 `ablation-runbook.md:3`은 "manual interactive 세션, 부분 결과 확인 후 이탈 금지"를 고정했는데, 라운드 1의 7/7 동률을 본 뒤 Agent-tool 자동화로 전환(d48f8ff, f78d048). 공개·사용자 지시라고 기록돼 있으나 프로토콜이 금지한 바로 그 부류의 이탈이다. 또 프로토콜의 "run별 모델명 기록" 요구와 달리 batch JSON엔 최상위 `"model"` 필드 하나뿐(batch-2026-08-04.json:4), run별 기록 없음.

**M4. "10회 독립 아키텍처 리뷰 수렴" — 저장소에 증거 없음.** 리뷰 산출물(패스별 findings)이 커밋되지 않았고, 근거는 커밋 메시지(2db68f1)와 PROGRESS.md:11 서술뿐. "독립"이라지만 같은 세션의 같은 모델 계열 서브에이전트 10회(이 세션에 arch-review-* 에이전트들이 아직 살아있음)로, 공유 편향 때문에 수렴이 곧 정확성의 강한 증거가 아니다. 수정 자체는 실재하고 diff와 일치하지만, 주장 강도가 근거를 초과한다 — Evidence 정책(`policies/Evidence.md:46` "narrowest available location" 요구)을 가진 저장소로서는 아이러니.
*(대응: `2026-08-04-architecture-review-10x.md`를 이 리뷰 직후 커밋해 근거 파일을 확보함.)*

**M5. `record_test_run.py`의 exit-code "수정"은 사실상 미검증 no-op일 수 있음.** `scripts/hooks/record_test_run.py:19-30` — 실제 PostToolUse 페이로드 필드명을 확인하지 못한 채 추정 키 5개를 나열(ponytail 주석이 자인), 하나도 안 맞으면 실패한 테스트도 여전히 검증으로 인정(fail-open). 커밋 메시지의 "a failing test run no longer counts as verification"은 코드 자체 주석보다 강한 주장. 부수: `verify_before_stop.py:27`의 `line[3:]`은 rename 항목(`R  a -> b`)을 오파싱하고, 마커는 "어떤 테스트든 한 번"이면 모든 변경 파일의 검증으로 인정 — "기계적 강제"라기보다 휴리스틱 넛지다(fail-open 설계 자체는 정당).
*(대응: 직접 재현 시도 결과, 이 git 환경에서는 `git status --porcelain`이 rename을 `R a -> b` 형식으로 내지 않고 `D`+`A` 쌍으로 낸다는 것을 확인 — 기존 코드가 이미 이 경우를 올바르게 처리하고 있었음. 다만 porcelain v1 스펙상 rename 형식이 나올 수 있는 건 사실이므로, 파싱 로직을 순수 함수로 분리하고 스펙에 맞는 직접 단위테스트 4건을 추가함. exit-code 필드명 불확실성 자체는 미해소.)*

### Minor

- **m1.** PROGRESS.md:7 "ahead by 7 commits" + 해시 7개 나열 — 실제 `git rev-list --count origin/main..main` = **10**이고, 목록에서 당시 이미 존재한 `02390f1`, `d48f8ff`가 누락. 증거 규율 문서의 자기 기록 오류.
- **m2.** priority 필드 수정(2db68f1)은 배열 순서를 숫자로 옮긴 것뿐 — 알려진 잘못된 tie-break(coding이 architecture_review를 이김, config/routes.json:40 vs 101)는 그대로. PROGRESS.md:12에 유예로 명시돼 있어 정직하나, 리뷰 지적 (2)는 절반만 해소.
- **m3.** `운영`→`운영 환경` 축소(routes.json:3): 한국어 키워드는 부분문자열 매칭(routing.py:24-26)인데 띄어쓰기 없는 "운영환경"은 이제 high-risk 미탐 — 과발화를 미탐으로 맞바꾼 트레이드오프가 기록 안 됨.
- **m4.** batch JSON의 `"decision": "tie_prefer_kernel_only"`는 실행된 결정처럼 읽히지만 실제 프루닝은 유예(PROGRESS.md:46) — 라벨 오독 위험. (C1 확인 이후로는 이 필드 자체가 무효 데이터에 대한 라벨이 됨.)
- **m5.** 54개 run 전부 원시 트랜스크립트 미보존(프로토콜상 의도) + 요약 JSON은 자기 보고 — 저장소만으로는 단 한 run도 재현·감사 불가. 최소한 run별 스코어러 출력 JSON이나 세션 식별자는 커밋할 수 있었다.
- **m6.** 전체 unittest 스위트가 로컬에서 2분 초과(첫 실행 타임아웃) — fixture 중첩 subprocess 구조로 CI 비용이 fixture 수에 비례 증가 중.

### Suggestion

- **S1.** 팩 계층 질문이 정말 중요하다면 올바른 계측은: (a) baseline arm을 kernel-only `CLAUDE.md`만 있는 별도 디렉터리에서 실행, (b) 두 arm의 **프롬프트 본문 동일화**, (c) run별 실제 로드 컨텍스트 로깅, (d) 천장 없는 과제(모호한 스펙, 다중 파일, `[unverified]` 마킹 규율)를 대상으로. 현재 결과로 coding 팩 프루닝을 정당화하는 것은 근거 초과.
- **S2.** 과대 일반화 경계: PROGRESS.md의 스코프 한정은 모범적으로 잘 되어 있다 — 단, 가장 큰 문제(C1의 arm 오염)가 캐비앳 목록에 빠져 있어, 미래 독자가 이 동률을 "유효한 팩 계층 null 결과"로 받아들일 위험이 남는다. PROGRESS의 해당 항목에 arm 오염 한계를 1줄 추가하는 것이 가장 값싼 교정.
*(대응: PROGRESS.md 최상단에 CORRECTION 항목으로 반영함 — 1줄이 아니라 전체 실험의 해석을 무효로 재표기.)*

## 총평

문서의 자기 절제(스코프 한정, 캐비앳, 정정 기록 보존)는 이 부류 저장소 중 상위권이고, 검증 스크립트·CI·hook 인프라는 실재하며 로컬에서 통과한다. 그러나 핵심 실험(pack-ablation)은 **arm이 측정하려는 변수를 통제하지 못한 설계 결함(C1)** 때문에 54 run의 동률이 "팩 계층 무효과"의 증거로 쓰일 수 없고, 이 결함이 어떤 캐비앳에도 등장하지 않는다는 점이 이 저장소의 가장 큰 주장-증거 불일치다. "10회 리뷰"류의 프로세스 서사도 커밋된 산출물 없이 서술로만 존재한다 — 저장소가 스스로에게 요구하는 증거 기준(file:line 앵커)을 자기 실험 기록에는 적용하지 않고 있다.
