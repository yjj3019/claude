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

## 2026-10-25 기본 Git 시간초과 5건·상태 원인 미확정 1건 후속

이전 전체 실행의 실패는 Git15초 초과5건(status3/head2)과 stderr가 남지 않은 missing-plugin-kernel 상태 None1건이다. 이번 후속에서도 이 원본 실패를 삭제하거나 후속 통과로 대체하지 않았다. 기준 HEAD는 faba43a316f9bc3b117faf820dfb0f9f3495b83b이며 기존 미커밋2.0.5 변경을 포함한다. Git15초·네이티브 child30초·assertion 판정·기본 PATH·명시 Git 선택·state v1은 유지했다. 사용자 설정과 전역 PATH는 바꾸지 않았다.

### 집중 재현과 지연 구간

이전6개를 기본 설정에서 실제 Git으로 순차 실행해6/6통과(421.406초, 실제exit0)했다. 162개 Git 호출 중132개가 기존15초 제한 대상이고30개는 기존 fixture 생성 호출(timeout 미지정)이다. 시간초과는 없었다. 15초 대상의 외부 시간 중앙값2.365초/최대8.805초, 대응한 Trace2 exit.t_abs(추적 세션 시작 기준) 중앙값0.131초/최대0.274초였다. argv·시각으로 대응한 관측이며 OS 프로세스 계보 증명은 아니다. 이 통과는 원래5개 시간초과나 진단이 없는1건의 원인을 소급 확정하지 않는다.

후속 전체 진단의 call179에서 실제15초 시간초과를 재현했다. test_initial_baseline_write_error_is_visible_at_stop의 setup이 아니라 복구 뒤 마지막 Stop의 rev-parse --show-toplevel이다. 직접 실행한 wrapper PID5700의 생성은0.364초였고, 실제 Git은05:06:49.429679UTC에 exit/atexit0(t_abs0.244344초)을 기록했다. Python communicate는05:07:03.502532UTC에15초 초과를 발생시켰다. wrapper 종료 요청 뒤 추가 출력 회수는 약0.075초, 최종returncode1/stdout46바이트/stderr0바이트였다. 따라서 이 표본의 긴 구간은 Git 내부 성공 기록 이후 종료 요청 전 대기에 있고, 시간초과 뒤 출력 회수가 길었던 표본은 아니다. Trace2 atexit은 OS 프로세스 종료 완료와 같지 않으며 timeout 당시 OS 종료 신호는 수집하지 못했다. wrapper 종료·상속된 출력 핸들·OS 종료 처리 중 어느 요소가 원인인지는 확정하지 않았다.

최종 실행의 일부 구간에는 이 검증이 기록한 wrapper PID와 Trace2 PID만 읽기 전용 핸들로 조회했다. 프로세스 열거·종료·관리자 권한 변경·시스템 전역 추적은 하지 않았다. 후속 정상 표본에서 atexit 뒤에도 프로세스가 nonsignaled이고 이후 signaled가 되는 것을 관측했다. [Windows WaitForSingleObject](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject)의 즉시 조회 결과와 [GetExitCodeProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getexitcodeprocess)를 기록했다. 두 API 조회는 원자적이지 않고0.5초 표본·명령/시각 대응이며 계보 검증이나 과거 timeout의 원인 입증이 아니다. 계측 오버헤드와 호스트 부하는 통제하지 않았다. [Git for Windows wrapper 설명](https://gitforwindows.org/git-wrapper.html)도 내부 프로그램 실행 계층을 설명하지만 해당 호스트 지연을 특정 구성요소 탓으로 증명하지 않는다. 기존 로컬 WPR 요약 역시8샘플에15초 실패가 없어 CPU stack 원인 귀속이 미확정이다. 새 WPR은 시작하지 않았다.

### 확인된 진단 누락 수정

call179가 발생한 테스트는 마지막 Stop의 stdout만 빈 값인지 검사해 stderr advisory가 있어도 기존 판정상 통과했다. Stop 결과를 한 번 저장하고 정제된 stderr를 테스트 로그와 assertion 메시지에 보존하도록 tests/test_hooks.py를 보완했다. 같은 단일 호출과 stdout 조건을 유지해 경고를 새 실패나 skip으로 바꾸지 않았다. 앞서 적용한 missing-plugin-kernel assertion의 stderr 메시지도 유지했다. 제품 런타임·검증 인식·상태 형식·실행기 선택·15/30초 제한은 바뀌지 않았다. 자동 실행기 우회·부분 stdout 성공 처리·재시도·snapshot 캐시/생략도 추가하지 않았다.

수정한 실제 상태 복구 테스트1개를 기본/명시로 각각 실행해 모두exit0(53.705/34.103초)을 확인했다. 실제 소스의 마지막3문장을 추출한 격리 확인에서도 stdout 유무×stderr 경고 유무4조합의 기존 판정, Stop1회 호출, 경고 기록을 확인했다(exit0). 합성 확인은 실제 지연 재현이나 모델 효능 증거가 아니다. 독립 로컬 코드 리뷰에서 추가 결함은 확인하지 못했다. 테스트와 기록만 바뀌어 plugin2.0.5/coding1.0.4/generated90을 유지했다.

### 수정본의 최종 Windows 전체 회귀

두 메인 실행에 같은 Popen 관찰과 Trace2를 적용하고 전체를 순차 실행했다. 기본 child에서만 FEF_GIT_EXECUTABLE을 제거하고, 명시 child에서는 기존 mingw64/bin/git.exe 절대 경로를 지정했다. 아래 시간은 unittest 관측이며 일반적 속도 개선률이나 안정성 보장이 아니다.

| 설정 | 메인 | 위임 | 합계 |
|---|---|---|---|
| 기본 PATH | 224실행/222통과/2skip/실패·오류0, 2984.686초, exit0 | 53실행/51통과/2skip, 56.511초, exit0 | 277실행/273통과/4skip/실패·오류0 |
| FEF_GIT_EXECUTABLE 명시 | 224실행/222통과/2skip/실패·오류0, 1446.518초, exit0 | 53실행/51통과/2skip, 53.265초, exit0 | 277실행/273통과/4skip/실패·오류0 |

전체554실행/546통과/8skip/실패·오류0이다. 각 설정의 skip4개는 기존 symlink 권한 제한이며 메인 WinError1314를 확인했다. 각 메인에서 직접 관찰한 Git 호출1133회씩은 모두 timeout 없이 완료했다. 네이티브 자식 내부의 모든 Popen 경계를 관찰한 것은 아니므로 이 수를 모든 자손 호출 수로 표현하지 않는다. 저장소 validator·generated --check90·위임 형식·evidence --check·보관 이력·diff 검사6개도 실제exit0이다. Golden31은 메타데이터 검사이며 실제 모델 실행이 아니다.

첫 진단 도구가 Popen을 함수로 교체해 asyncio의 Windows 상속을 깨뜨린45테스트/8import오류 실행은 제품 회귀 결과에서 제외하고 보존했다. Popen 클래스를 유지하도록 수정한 뒤224개 로딩과 asyncio 상속 사전 검사exit0을 확인했다. 그다음 call179를 얻은 진단 전체는 진단 누락 수정 전 중단한 부분 실행이며 최종 전체로 계산하지 않았다.

최종 기록기도 명시 메인 종료0을 먼저 저장한 후 runs.json 교체에서 WinError5로 중단됐다(helper exit1). 이미 저장된 실제exit0과 원시224개 OK 로그를 대조했고 원본 JSON은 덮어쓰지 않았다. 조회용 읽기 핸들을 열어둔 합성 파일에서 같은 replace WinError5와 핸들 종료 후 교체 성공을 재현했다. 다만 원래 교체를 막은 정확한 행위자는 확정하지 않았다. 조회기를 중단하고 결과 JSON을 열지 않는 종료 flag 방식으로 진단 도구를 보완했다. 통과한 두 메인은 재시도하지 않고, 남은 위임1개와 정적6개만 별도 기록기로 이어가 helper exit0을 확인했다. 이 파일 공유 재현은 Git15초 초과 원인 입증이 아니다.

최종 전체 실행 중 제품457파일은 바이트 동일했고 HEAD·사용자/저장소 settings·CLAUDE/AGENTS 해시도 같았다. 완료 뒤 이 문서와 PROGRESS만 추가 기록한다. 원시 실패·targeted·Trace2·소유 PID 조회·기록기 오류/복구·실제 명령별 종료 코드·정규화 집계는 checkout 옆 validation-20261025-git-timeout-followup, validation-20261025-git-timeout-full-v2, validation-20261025-git-timeout-final에 보존한다. 진단 조회 종료는exit1(명시적 중단)이며 지속 실행하지 않는다.

이번 단일 전체 통과로 기본 설정의 간헐 지연 해소나 안정적인 연속 통과를 보증하지 않는다. 과거 stderr가 없는1건과 Windows 종료 지연의 구성요소 원인은 미확정이다. 안전하고 호환되는 런타임 수정은 확립되지 않았다. 다른 호스트/OS·실제 모델·새 시스템 전역 추적·운영 설치·외부 diff 전송·새 원격CI·커밋·푸시는 수행하지 않았다. 유지보수 참조 원격HEAD는 Ponytail09c434ab73ca43761c5d8b0c5d341926c2fba710, Karpathy-inspired2c606141936f1eeef17fa3043a72095b4765b9c2로 기존과 같았다.

## 2026-10-25 실패 시점의 프로세스·출력 핸들 추적 후속

이번에는 실패 순간을 구분할 진단기를 보완하고 기본/명시 전체 회귀까지 완료했다. 그러나 실제15초 Git 시간초과는 재현되지 않았다. 따라서 과거 시간초과의 대기 단계나 특정 Windows 구성요소 원인을 이번 자료로 확정하지 않는다. 제품 런타임 수정의 근거도 확립되지 않았다. 기존15초 Git/30초 네이티브 제한·assertion 판정·기본 PATH/FEF_GIT_EXECUTABLE 선택·state v1은 유지했다.

### 진단 경계와 안전한 관측

로컬 실험 도구 exit_observer.py를 자식 환경의 sitecustomize로 적용했다. 사용자 설정·전역 PYTHONPATH·Python 표준 라이브러리·배포 플러그인에는 설치하지 않았다. Popen 클래스 형태와 원래 인자·입출력·kill 전달을 유지하고, communicate가 TimeoutExpired를 던진 직후 run()이 종료 요청을 하기 전에 관측한다. 현재 Python3.14.4의 private 구현에 한정한 도구이며 버전이 바뀌면 자체 검사를 다시 해야 한다.

- 예외 traceback의 실제 발생 줄을 원본 _communicate/_wait 코드와 대응해 stdout reader, stderr reader, stdin writer, process wait를 구분한다. 이후 reader 생존 상태·버퍼 항목/길이·Python 스택(로컬 변수 제외)과 읽기 완료/닫힘 시각을 기록한다. buffer_entries=0은 read가 아직 반환하지 않았다는 뜻이며 파이프 안의 데이터가0이라는 뜻이 아니다.
- Popen이 이미 가진 프로세스 핸들로 WaitForSingleObject(0)/GetExitCodeProcess를 조회하고, 읽기 핸들의 번호·GetHandleInformation 속성을 기록한다. 쓰기 핸들은 생성 시 정수 식별값만 보관하고 복제·추가 보유하지 않는다. 출력 본문·오류 본문·전체 명령 인자·환경 값은 진단 저널에 저장하지 않는다.
- reader가 닫은 사실이 기록됐으면 캐시 번호 조회를 생략한다. 그 외 번호 유효성도 같은 출력 파이프의 객체 동일성 증명이 아니라고 명시한다. 닫힌 번호는 다른 객체에 재사용될 수 있다.
- 스냅샷은 원자적이지 않다. 정확한 예외 발생 위치와 직후 여러 API로 조회한 상태를 구분한다. 원격 자손의 모든 쓰기 핸들 소유자나 시스템 전체 핸들·프로세스를 열거하지 않았다. CPU/파일 I/O 계측 오버헤드와 다른 호스트 활동도 통제하지 않았다.

[GetHandleInformation](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-gethandleinformation)은 핸들 속성만 조회한다. [익명 파이프 설명](https://learn.microsoft.com/en-us/windows/win32/ipc/anonymous-pipe-operations)에 따르면 쓰기 핸들이 모두 닫혀야 읽기 종료를 받을 수 있다. 따라서 reader 대기가 곧 reader 결함이라는 뜻은 아니다. [PeekNamedPipe 공식 경고](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-peeknamedpipe)처럼 멀티스레드의 동기 핸들 조회가 블로킹될 수 있어 추가 pipe read/peek는 사용하지 않았다.

### 확인한 진단 도구 결함과 보완

독립 로컬 리뷰에서 진단 자체의 두 결함을 확인해 실험 도구에서 수정했다. 제품 결함이 확인돼 운영 코드를 수정한 것은 아니다.

1. 로그 쓰기·상태 조회 실패가 원래 성공 결과/TimeoutExpired/kill 동작을 덮을 수 있었다. 진단 오류를 stage와 오류 종류로 별도 수집하고 원래 반환/예외/종료 전달을 보존했다. 프로세스 인스턴스별 완료 표식의 evidence_complete=false 또는 표식 누락은 관측 불완전으로 다루며, 제품 테스트 결과와 분리한다.
2. 캐시 핸들 번호가 유효하면 같은 출력 pipe라고 오인할 수 있었다. 번호와 객체 동일성을 구분하고 reader 닫힘 후 조회를 생략했다. PID도 재사용될 수 있으므로 PID 집합만 쓰지 않고 부모 호출의 생성~완료 시각과 자식 인스턴스를 대응했다. 초기 PID만으로 만든 목록에 섞였던 다른 Git 호출은 원본을 보존한 뒤 분석 목록에서 분리했다.

세 가지 합성15초 시나리오는 모두 자체 검사exit0이었다: 출력 EOF 대기/프로세스 생존, 출력은 닫혔으나 프로세스 wait, 부모 종료 뒤 자손이 출력 writer를 상속한 경우. 마지막 합성 사례는15초 예외가 발생했지만 기존 Windows kill 후 communicate 수거가 자손 종료까지 기다려 run 반환은 약21.127초였다. 실제 Git 실패의 재현이 아니며15초를 전체 wall-clock 상한으로 새로 정의한 것도 아니다. 두 관측 시점을 구분한다.

수정 후 오류 주입 검사5개도exit0으로 성공 반환값·stdout/stderr 보존, 원래15초 TimeoutExpired 유지, kill1회/반환값 보존, 핸들 동일성 미확인 표시, 불완전 관측 표식을 확인했다. 첫 검사는 Windows의 CRLF 출력4바이트를 LF3바이트로 가정해 실패했으며 원본 로그/소스를 보존했다. 고정 문자열 가정을 제거하고 동일 자식 환경에서 부모 Popen만 원본으로 사용한 기준 결과와 정확히 비교해 통과했다. 합성 실패와 의도한 불완전 표식을 실제 Git 장애로 집계하지 않았다. 독립 재검토는 두 지적 해소와 추가 차단 지적 없음을 확인했다.

### 실제 호출과 출력 방식 비교

기본 PATH의 실제 Git 명령4종을 최대200회/첫 timeout에서 중단하는 고정 절차로 실행해200회 모두 timeout 없이 끝났다(실제exit0, 재시도 없음). 이어진 최종 두 메인의 관측 Git 호출은각1175회이고 그중 기존15초 대상은각939회였다. 관측된 자연 timeout·reader 오류는0이었다. 이 수는 Python이 직접 실행해 관측한 경계이며 모든 native Git 자손 수가 아니다.

최종 정상15초 대상1878개 중 가장 느린 communicate 구간은 서브모듈 status의3.450초였다. 출력 read 반환까지3.449초, reader 닫힘 뒤 communicate 반환까지 약0.000927초였다. 프로세스 생성 시간을 포함한 명령 전체 wall time과 구분한다. 정상 표본의 구간 분해일 뿐, 과거15초 초과 원인이나 그때의 핸들 상태를 소급 입증하지 않는다.

같은 새 fixture에서 status/HEAD를 pipe와 TemporaryFile 출력으로 AB/BA/BA/AB 순서 교대했다.16회 모두 exit0이고 쌍별 stdout/stderr 길이와 SHA256이 같았다. 양쪽15초를 유지했고 출력 본문은 결과 저널에 남기지 않았다. 아래는 각4개 표본 중앙값이며 캡처 자원 생성과 subprocess 실행을 포함한 외부 시간이다.

| 명령 | pipe(초) | 임시 파일(초) |
|---|---:|---:|
| status | 1.787 | 1.771 |
| rev-parse HEAD | 1.696 | 1.781 |

파일 방식에서 일관된 지연 감소를 관측하지 못했다. 소표본의 시간 차이를 동등성이나 성능 효과로 주장하지 않으며, 실제 실패15초의 원인도 입증하지 않는다. 이 자료는 reader thread만의 원인설이나 제품의 캡처 방식 변경을 지지하기에 부족하다. 제품의 파이프 수집·실행기 선택·timeout·재시도 정책은 바꾸지 않았다.

### 최종 회귀와 관측 범위

| 실행 | 테스트 | 통과 | skip | unittest 시간(초) | 실제exit |
|---|---:|---:|---:|---:|---:|
| default-main | 224 | 222 | 2 | 2198.565 | 0 |
| default-delegation | 53 | 51 | 2 | 51.279 | 0 |
| explicit-main | 224 | 222 | 2 | 1456.194 | 0 |
| explicit-delegation | 53 | 51 | 2 | 56.491 | 0 |

합계554실행/546통과/8skip/실패·오류0이다. skip은 기존 Windows symlink 권한 제한이다. 저장소·generated --check90·위임 형식·evidence·보관 이력·diff6검사도 각각 실제exit0이다. Golden31은 메타데이터 검사이며 실제 모델 실행은 아니다. 최초 진단 버전의 중단된 default 부분 실행은 최종 전체 결과에서 제외하고 보존했다.

설정별 실제 기록된 Python 인스턴스는 메인54개(주 프로세스+자식53), 위임25개(주 프로세스+자식24)이며 모두 완료 표식이 있고 진단 오류가 없다. 호출별 PID와 생성/완료 시각을 대응하면 각 설정의 Python 자식71개 중53개, 위임 자식48개 중24개가 내부 진단과 대응된다. 메인18개와 위임24개 내부는 미관측이다. 소스 확인으로 payload 독립 실행의 PYTHONPATH 제거/-I, Golden runner의 -I, 위임 validator의 -S 경로임을 확인했다. 격리 옵션을 약화하지 않았다. 부모의 Popen 입출력 경계는 관측하지만 이 자식 내부까지 관측했다고 주장하지 않는다. 기존 문제6개의 주 in-process hook 경로는 부모에서 계측됐다.

검증 동안 소스457파일은 바이트 동일했고 HEAD·사용자/저장소 설정·CLAUDE/AGENTS도 모든 단계 전후 동일했다. 완료 후 기존 이 문서와 PROGRESS에만 기록한다. 로컬 실험 도구·원시 저널·자체 검사·PID/시각 대응·실제 명령 종료 코드는 checkout 옆 validation-20261025-exit-pipe-state 및 validation-20261025-exit-pipe-state-v2에 보존한다. 별도 스킬/런타임 API로 추가하거나 배포하지 않았고 plugin2.0.5/coding1.0.4/generated90을 유지한다.

**남은 한계:** 실제15초 실패 시점의 새 프로세스·출력 핸들 스냅샷은 이번에 확보하지 못했다. 정상 관측은 EOF 대기가 큰 구간임을 보여주지만 과거 실패의 단계/원인이나 특정 OS·보안 제품의 책임은 확정할 수 없다. 기존 stderr 없는1건도 소급 확정하지 않는다. 자동 우회·timeout 증가·판정 완화·시스템 전역 추적·운영 설정 변경·외부 모델 전송·원격CI·커밋·푸시는 하지 않았다.
