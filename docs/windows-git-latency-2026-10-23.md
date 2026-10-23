# Windows Git 지연 추가 진단 — 2026-10-23

이번 로컬 진단은 지연 범위를 Git 내부 연산보다 프로세스 실행 전후 구간으로 좁혔다. 제품 코드의 결함이나 보안 검사·콘솔·실행기 중 특정 구성요소의 근본 원인을 확정한 것은 아니다. 제품의 Git 선택·snapshot·timeout·상태 계약은 변경하지 않았다.

기준 HEAD는 `45de11e2dbe8548f2542fb677b023286592bda85`이며 기존 미커밋 변경을 포함한다. Windows/Python 3.14.4, Git 2.54.0.windows.1이다. [이전 래퍼·모델 실험](verification-wrapper-2026-10-23.md)과 달리 이번에는 실제 모델을 실행하지 않았다.

## 방법과 경계

- 사용자 저장소 대신 새 임시 Git 저장소를 만들고 sample.txt 한 파일만 두었다. 커밋·네트워크·사용자 설정 변경은 하지 않았다. 기본 샌드박스의 fixture 생성/정리 권한 오류 실행은 측정에서 제외하고 전체 Windows 회귀와 같은 허용된 실행 모드에서 재실행했다.
- PATH에서 선택된 Git for Windows의 `cmd/git.exe`를 기본 실행기(A), 같은 설치의 `mingw64/bin/git.exe`를 내부 실행 파일(B)로 비교했다. 다른 Git 배포판을 제품에서 자동 선택하지 않았다.
- 각 명령은 같은 저장소에서 AB/BA/BA/AB 네 쌍으로 실행했다. `subprocess.run`의 stdout/stderr를 캡처하고 timeout 25초, 외부 시간은 perf_counter로 측정했다. 매 실행의 종료 코드와 stdout/stderr SHA256을 비교했다.
- 명령은 `git --version`, `git status --porcelain=v1 -z --untracked-files=all`, `git submodule status`다. 마지막 항목은 **등록된 서브모듈이 없는 저장소**이므로 실제 서브모듈의 초기화·변경 감지·이관 호환성 증거가 아니다.
- Trace2는 `GIT_TRACE2_EVENT`를 해당 프로세스에만 지정했다. 후속 추적 파일은 저장소 밖에 두어 status 출력 해시가 일반 실행과 같은지 확인했다. 1차 탐색은 trace 파일을 저장소 안에 둬 출력이 달랐으므로 해당 trace를 동일 조건 비교에서 제외했다.

## 실행 순서를 바꾼 비교

단위는 초이며 아래 각 열은 쌍 번호 0~3에 대응한다. 모든 실행은 exit 0, stderr 0바이트였고 같은 명령의 출력 해시도 일치했다.

| 명령 | 실행 파일 | 표본 0 | 표본 1 | 표본 2 | 표본 3 | 중앙값 |
|---|---|---:|---:|---:|---:|---:|
| version | 기본 실행기 | 1.577406 | 1.189676 | 1.271773 | 1.255839 | 1.263806 |
| version | 내부 실행 파일 | 0.686335 | 0.729079 | 0.668472 | 0.756974 | 0.707707 |
| status | 기본 실행기 | 1.790971 | 1.626260 | 1.949138 | 2.026830 | 1.870055 |
| status | 내부 실행 파일 | 0.749540 | 0.690230 | 0.975539 | 0.855130 | 0.802335 |
| submodule status | 기본 실행기 | 5.431579 | 5.885284 | 6.918449 | 4.717963 | 5.658432 |
| submodule status | 내부 실행 파일 | 3.717104 | 4.185395 | 6.152617 | 4.646168 | 4.415781 |

출력 SHA256: version `a0bef3335cdbc9a4a7733503ecdb281e91319f5a15e22026bfbef750ce76aaba`, status `26660e7ab1f9cb40676066574fd690bea1073f9ccba19f8934ff11027343fe52`, 빈 submodule 출력 및 stderr `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

별도 status 추적은 외부 시간 2.190938초, Trace2 exit의 t_abs 0.154657초였다. 그 실행도 일반 status와 출력 해시가 일치했다. 두 시계의 범위는 다르다. 차이를 모두 실행기나 보안 검사 시간으로 단정하지 않으며, 이 한 번의 추적은 이전 전체 회귀나 실제 모델 지연의 시간 분해가 아니다.

1차 탐색에서 빈 Python 실행(`python -c pass`)도 0.832990/0.630930/0.788304초, 중앙값 0.788304초였다. 저장소 연산이 없는 실행에서도 지연이 관측됐다. 별도 번들 Git 실행기도 status 중앙값 1.679752초(n=3)였으나 배포판·설치 위치가 달라 원인 확정용 비교로 쓰지 않는다.

## 콘솔 생성 옵션 비교

기본 실행기에 대해 기본 옵션과 `CREATE_NO_WINDOW`만 AB/BA/AB/BA 네 쌍으로 바꿨다. 동일한 새 fixture와 status 명령, 캡처·timeout 20초를 사용했다. 모든 실행의 종료 코드와 출력 해시는 같았다.

| 옵션 | 표본 0 | 표본 1 | 표본 2 | 표본 3 | 중앙값(초) |
|---|---:|---:|---:|---:|---:|
| 기본 | 1.508477 | 1.487817 | 1.641791 | 1.828439 | 1.575134 |
| CREATE_NO_WINDOW | 1.656513 | 1.584469 | 1.654508 | 1.725682 | 1.655511 |

이 표본에서 개선을 관측하지 못했다. 통계적 동등성이나 모든 환경에서의 무효성을 증명한 결과는 아니다. 제품에 해당 옵션을 추가하지 않았다.

## 판단과 남은 검증

실행 파일 선택에 따른 시간 차이는 반복됐지만 설치 위치·시작/종료 처리·부하·보안 검사 등 변수를 완전히 분리하지 못했다. 내부 경로 직접 지정은 다른 설치 구조, portable Git, 외부 helper/필터, 사용자 PATH·설정과 실제 서브모듈을 포함한 호환성 검증이 필요하다. 이번 표본만으로 제품의 Git 실행기를 바꾸거나 일반적인 속도·비용 절감을 주장하지 않는다.

OS/보안 제품의 프로세스 추적과 다른 호스트 재현은 하지 않았다. snapshot 호출을 생략·캐시하거나 timeout을 늘리지 않았고 보안 설정도 바꾸지 않았다. 런타임 변경이 없어 전체 회귀는 다시 반복하지 않는다. 앞서 완료한 Windows 263실행/259통과/4symlink skip 결과와 이번 진단은 구분한다. 외부 diff 리뷰·원격CI·배포·커밋·푸시 없음.

## 후속 호환성 확인과 적용 방향

[Git for Windows 공식 wrapper 설명](https://gitforwindows.org/git-wrapper.html)은 wrapper의 환경 준비와 실제 프로그램 실행을 설명하며, 내부 Git의 절대 경로 직접 호출을 지원한다고 명시한다. 이 문서는 내부 bin을 전역 PATH에 추가하는 방식과 구분한다. 직접 호출 지원 자체를 미지원 기능으로 해석하지 않는다. 단, 공식 문서가 프로젝트의 모든 사용자 환경에서 동등성을 보증하는 것은 아니다.

새 임시 저장소에서 제품의 snapshot 함수를 그대로 실행하고 subprocess의 Git 실행 파일만 각 비교 구간에서 교체했다. 각 상태는 기본 실행기→내부 실행 파일 순서로 한 번씩 비교했으므로 아래 시간은 순서·부하 통제가 충분한 성능 추정치가 아니다.

| 비교 상태 | 기본 실행기(초) | 내부 실행 파일(초) | 결과 |
|---|---:|---:|---|
| unborn HEAD | 3.920924 | 1.696207 | snapshot 동일, head=None |
| 초기화된 실제 로컬 서브모듈 | 9.988933 | 5.083874 | snapshot 동일, child files 비어 있음 |
| 공백·유니코드 staged rename + ignore=all인 dirty 서브모듈 | 9.258072 | 4.929369 | snapshot 동일, child 수정/미추적2파일 및 부모 rename 감지 |

고정 셸 alias의 `printf helper-ok` 실행도 양쪽 exit0/stdout 동일/stderr0바이트였다. fixture 안에서만 합성 작성자로 커밋하고 로컬 file transport를 명령 한 번에 허용해 서브모듈을 생성했다. 사용자 저장소·전역 설정·네트워크는 바꾸지 않았다. 제품 subprocess 코드는 수정하지 않았다.

독립 방향 검토에서 자동 경로 치환의 남은 위험을 확인했다. 경로 형태와 sibling 버전 확인만으로 기업용/custom wrapper를 식별할 수 없다. 또한 현재 timeout 진단은 명령 이름이 git인 경우 operation을 기록하므로 절대 경로 지원 시 진단 계약도 함께 보완해야 한다. 공용 Git 호출과 HEAD 호출의 선택 정책, unborn nonzero 처리, 재귀 서브모듈 동작도 일치해야 한다.

기본 PATH 동작을 유지하고 명시적으로 지정한 경우에만 실행 파일을 선택하는 `FEF_GIT_EXECUTABLE` 방안을 제안하고 공개 설정 계약 추가 승인을 요청했다. 이 시점에는 미구현 상태였다. 이후 사용자의 후속 진행 지시에 따라 아래와 같이 구현·검증했다. 외부 helper/필터 전체·portable Git·다른 버전·다른 호스트 호환성은 여전히 미검증이다.

## 명시적 Git 선택 구현과 observer 검증

`FEF_GIT_EXECUTABLE`을 추가했다. 미설정/빈 값은 기존 git 검색을 유지한다. 명시 값은 기존 파일의 절대 경로여야 하고 Windows에서는 .exe여야 한다. 잘못된 값이나 실제 Git 명령 실패를 다른 실행기로 재시도하지 않는다. 공용 호출·HEAD·서브모듈 재귀가 같은 선택 함수를 사용한다. 내부 함수가 실행한 Git의 timeout만 기존 operation 식별용 명령 형태로 정규화해 경로/출력을 노출하지 않는 진단을 보존했다. snapshot v1·footer·15초 timeout·테스트 child argv는 유지했다. 설정은 부모가 명시적으로 전달할 때만 사용하며 자동 탐지·probe·전역 PATH 변경은 없다. [설치 안내](Installation.md#optional-git-executable-for-verification)에 사용·해제 방법을 기록했다.

현재 Windows 호스트에서 SessionStart → app 수정 → 검증 래퍼(합성 unittest 1개 포함) → recorder → Stop을 새 fixture마다 실제 별도 Python 프로세스로 실행했다. recorder에는 host exit metadata 없이 래퍼 stdout/stderr만 제공했다. 기본(A)/명시(B) 순서는 AB/BA/BA/AB 네 쌍이다. 전반2쌍은 HOME 상속, 후반2쌍은 child 환경에서만 HOME을 제거했다. 작업 경로와 지정 Git 설치 경로 모두 공백을 포함한다. 초기화·fixture 커밋 시간은 제외하며 아래 전체 시간은 네 단계 소요의 합이다.

| 쌍 | HOME | 기본 전체(초) | 명시 전체(초) |
|---|---|---:|---:|
| 0 | 상속 | 53.082368 | 28.607781 |
| 1 | 상속 | 54.743755 | 30.729446 |
| 2 | 제거 | 48.833536 | 25.948679 |
| 3 | 제거 | 40.654443 | 22.510799 |
| 중앙값 | 혼합 표본 | 50.957952 | 27.278230 |

8회 모두 실제 테스트 exit0, 저장된 verification.returncode0, 최종 Stop stdout/stderr 없음·exit0을 확인했다. 각 행의 합과 전체 중앙값도 재계산했다. 명시 값의 경로 검증 시간도 이 관측에 포함된다. 단일 호스트의 소표본이며 다른 회귀가 동시에 실행돼 부하가 섞여 있다. 이는 현재 합성 observer의 관찰 결과이며 실제 모델 세션 지연·구독 비용·다른 시스템의 속도 개선을 증명하지 않는다.

회귀는 설정/기존 진단13개, 기본 경로 실제 훅3개, 명시 경로 핵심 훅5개, runtime7개, build8개, installer71개를 실행했다. 합계107실행/105통과/2symlink skip/실패0이다. 기본 경로3개174.435초, 명시5개289.198초, runtime29.881초, build25.646초, installer77.055초였다. 설정 관련 신규 테스트는8개이며 기존 진단·훅 계약5개와 함께 확인했다. 임시 샌드박스 권한 오류와 runner의 최초 잘못된 cwd로 인한 import 실패는 수정된 실행 결과와 구분했다. 이 묶음의 별도 원시 로그 파일은 생성되지 않았고 도구/세션 출력에 결과가 남아 있다.

로컬 독립 리뷰에서 구체적 결함은 발견하지 못했고 원본/생성본 일치도 확인했다. repository validator·payload101·10라우트·Kernel·diff 공백 검사도 통과했다. runtime은 코드+설치 안내2파일을 생성기에 의해 동기화했다. 기존 전체263개 회귀는 이 구현 전 결과이며 이번 코드의 전체 회귀 결과로 재사용하지 않는다. 이번 전체 main/delegation 재실행·Linux 실기·실제 Claude/UI·외부 diff 전송·원격CI·전역 배포·커밋·푸시는 하지 않았다. 기존 캐시 설치본이나 실행 중 호스트가 자동 갱신되는 것은 아니다.

## 두 설정의 Windows 전체 회귀와 누적 최종 리뷰

후속 요청으로 같은 제품460파일을 고정하고 Windows/Python3.14.4에서 기본 설정과 명시 설정의 main/delegation 전체를 순차 실행했다. HEAD는 계속 `45de11e2dbe8548f2542fb677b023286592bda85`다. 두 설정의 소스 기준 해시 맵은 같고 제품 파일 변경은 없었다. 아래 결과는 위의 집중107개 검증 이후 수행한 별도 전체 실행이다.

| 설정 | 메인 | 위임 | 합계 |
|---|---|---|---|
| 기본(PATH Git) | 222실행 / 218통과 / 2skip / 2실패, 2825.735초 | 49실행 / 47통과 / 2skip, 76.991초 | 271실행 / 265통과 / 4skip / 2실패 |
| FEF_GIT_EXECUTABLE 명시 | 222실행 / 220통과 / 2skip, 1901.936초 | 49실행 / 47통과 / 2skip, 162.866초 | 271실행 / 267통과 / 4skip / 실패0 |

전체542실행/532통과/8skip/2실패/오류0이다. 각 설정의 skip4개는 symlink 생성 권한 제한이며 메인2개에서 WinError1314가 기록됐다. 시간은 순차 단일 실행의 관측으로 부하·캐시·사용자 활동을 통제하지 않았으므로 설정의 일반적 성능 개선률로 해석하지 않는다.

기본 설정 실패는 `test_malformed_wrapper_attempt_invalidates_previous_pass`의 Stop 차단 기대와 `test_native_script_json_entrypoints`의 setup에서 발생했다. 두 경우 모두 `TimeoutExpired; git_operation=status` 진단, 즉 Git status가 기존15초 제한을 넘긴 실행이었다. 해당 두 테스트를 기본 설정으로 별도1회 실행하자 2/2통과(136.054초)했고, 명시 설정 전체 실행에서도 각각 통과했다. 처음 실패를 재현 성공으로 덮어쓰지 않는다. 지속적으로 재현되는 새 코드 결함은 확인하지 못했으며 timeout·관측·검증 판정·기본 PATH 동작을 완화하지 않았다. **기본 설정에서 안정적인 전체 통과는 이번에 확인하지 못했다.** OS/프로세스 지연의 근본 원인도 미확정이다.

두 설정 모두 저장소·payload101·10라우트·Kernel·위임 패키지 validator·deterministic evidence·보관 이력 복구/무결성·diff 검사는 exit0이었다. Golden31개는 메타데이터 검증이며 실제 모델 실행이 아니다. Git의 기존 LF→CRLF 안내는 남아 있다.

첫 하네스는 기본 설정 완료 뒤 사용자 settings.json 해시 변경을 감지해 명시 설정 시작 전에 중단했다. 제품 변경 경로는 없고 사용자 CLAUDE.md도 동일했다. 설정 사용처와 테스트의 HOME/USERPROFILE 격리를 확인했으나 변경 주체를 특정하지 못했다. 사용자 파일은 복원하거나 덮어쓰지 않았다. 원본 결과를 보존하고, 동일 제품 해시를 다시 강제한 별도 명시 설정 하네스에서 현재 사용자 설정을 기준으로 전체 실행을 마쳤다. 그 실행 동안 제품·확인대상 사용자 파일은 모두 동일했다. 따라서 두 실행 전체에 걸친 사용자 설정 불변성은 주장하지 않는다.

원시 로그·원본 report는 Temp의 fef-dual-windows-full-9xe_gozo와 fef-explicit-windows-full-04ocn41k에 있다. 첫 하네스의 FAILED 요약 skip 집계 누락은 원본을 유지한 `normalized-default-report.json`에서 실제 unittest 요약으로 바로잡았다. 단독2개 재현 로그는 default-env-failures-5658f4990cf549bfb60401391a5b75a7.log다. 결과·원시 요약·HEAD를 메인에서도 대조했다.

누적29개 변경 파일과 미추적 보고서7개의 독립 로컬 리뷰에서 구체적 수정 결함은 발견하지 못했다. 원본/생성본8쌍 바이트, 문자열 외 installer/builder AST, JSON 통계·문서 집계·권리 경계·기술 ID/저장 계약을 확인했다. 제한적 시크릿/개인 경로 검사에서 후보는 없었다. 제품 코드를 추가 수정하지 않았고 검증 후 이 기록과 PROGRESS만 갱신했다. 다른 Python/OS·실제 Claude/UI·외부 Claude diff 전송·새 원격CI·전역 배포·제3자 권리/상표 허가는 확인하지 않았다. 커밋·푸시 없음.

## 2026-10-23~24 기본 설정 연속 전체 검증

이전 간헐 실패 두 항목을 각각3회 순차 실행한 뒤 같은 작업트리에서 기본 설정 전체 검증을 두 차례 연속 실행했다. 자식 환경에서 FEF_GIT_EXECUTABLE만 제거했고 PATH·사용자 설정·15초 Git 제한·검증 판정은 유지했다. 다른 검증이나 별도 로그 감시 프로세스를 병렬 실행하지 않았다. 호스트의 다른 활동까지 통제한 실험은 아니다.

사전 검증은6/6통과(unittest411.575초, 하네스419.741초)했다. 이후 전체 결과는 아래와 같다. 표의 시간은 unittest 보고값이다.

| 실행 | 메인 | 위임 | 전체 |
|---|---|---|---|
| 1차 | 222실행 / 220통과 / 2skip / 실패·오류0, 3073.708초 | 49실행 / 47통과 / 2skip / 실패·오류0, 68.252초 | 271실행 / 267통과 / 4skip / 실패·오류0 |
| 2차 | 222실행 / 216통과 / 2skip / 3실패 / 1오류, 3102.181초 | 49실행 / 47통과 / 2skip / 실패·오류0, 168.286초 | 271실행 / 263통과 / 4skip / 3실패 / 1오류 |

전체542실행/530통과/8skip/3실패/1오류이며 사전6개는 별도다. Skip은 기존 Windows symlink 권한 제한이다. 두 라운드 모두 저장소·payload101·위임 validator·evidence·보관 이력·diff 검사는 exit0이었다. 기본 설정의 단일 전체 통과는 확인했지만 **안정적인 연속 전체 통과는 확인하지 못했다**.

2차의 원시 traceback에서 다음 네 Git timeout을 확인했다. 세 실패는 SessionStart setup의 stderr 기대에서, 한 오류는 snapshot 직접 호출에서 발생했다.

| 테스트 | 위치·연산 | 원인 |
|---|---|---|
| test_preexisting_dirty_read_only_session_does_not_block | setup / head | Git15초 초과 |
| test_real_wrapper_failure_preserves_exit_and_stderr | setup / repository | Git15초 초과 |
| test_real_wrapper_success_credits_native_payload_without_exit_code | setup / status | Git15초 초과 |
| test_submodule_edits_invalidate_verification_even_when_status_ignored | snapshot / child rev-parse --show-toplevel | Git15초 초과 |

이전 실패 두 항목은 사전 반복과 두 전체 실행에서 모두 통과했지만 다른 항목에서 같은 timeout이 재발했다. 현재 가설은 특정 테스트 입력보다 Windows의 간헐적 Git 실행 지연이다. 특정 OS 구성요소나 보안 제품의 책임은 확인하지 못했다. 순차 실행과 관측 부하 축소만으로 해소되지 않았으므로 세 번째 전체 반복으로 통과를 고르지 않았다. 새 제품 코드 결함이나 안전한 기본 경로 수정 방안은 확정하지 못했고 timeout 증가·자동 재시도·wrapper 자동 우회·검증 완화는 적용하지 않았다. 다음 진단은 OS 프로세스 추적 또는 별도 Windows 호스트의 같은 기본 설정 비교다. 실행기 선택 정책 변경은 custom wrapper 호환성과 적용 범위를 먼저 검토해야 한다.

근거는 Temp의 fef-default-stability-1ta8gikm/report.json, preflight-six.log, round-1-main.log, round-2-main.log 및 각 라운드별 검사 로그다. 최종 보고의 source_unchanged/user_unchanged는 모두 true, two_rounds_passed는 false다. 제품460파일·확인대상 사용자 파일·HEAD가 검증 전후 동일했고, 종료 후 이 문서와 PROGRESS에만 기록을 추가했다. 임시 로그는 영구 보존을 보장하지 않는다. 실제 모델·다른 OS·새CI·외부 diff 전송·배포·커밋·푸시는 수행하지 않았다.
