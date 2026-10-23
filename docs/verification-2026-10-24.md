# TaskForge 전체 회귀·실제 모델·PPT 실행 검증 — 2026-10-24

요청한 세 검증을 실행했다. **Windows 기본 설정 전체 회귀는 Git timeout 2건으로 미통과**다. 실제 Claude의 합성 코딩·새 세션 재개와 PowerPoint의 생성·열기·렌더링·구조 검증은 완료했으며, 모델의 제약 위반 시도와 보고 오류도 발견했다. 이 결과를 일반 효능이나 배포 승인으로 해석하지 않는다.

[구조화 증거](verification-2026-10-24.json), [적용한 AI-Harness 관점](ai-harness-assessment-2026-10-24.md), [기존 Windows 지연 진단](windows-git-latency-2026-10-23.md)을 구분한다. HEAD는 45de11e2dbe8548f2542fb677b023286592bda85, 미커밋 누적 작업트리461파일을 동결해 검증했다. 전체 실행 동안 제품 목록·바이트·HEAD와 관측 대상 사용자 settings.json/CLAUDE.md 해시는 동일했다. 이후 이 보고서와 JSON·작업 이력·평가서 후속 링크만 기록했다. 커밋·푸시는 하지 않았다.

## Windows 전체 회귀

FEF_GIT_EXECUTABLE은 자식 환경에서 제거했고 기본 PATH·15초 제한·검증 판정·권한은 유지했다. main/delegation 전체와6개 검사를 한 차례씩 수행했다. 모델·Office 검증이 같은 호스트에서 일부 겹쳤으므로 부하를 통제한 안정성·성능 실험은 아니다.

| 범위 | 실행 | 통과 | 실패 | 오류 | 건너뜀 | unittest 초 |
|---|---:|---:|---:|---:|---:|---:|
| main | 222 | 218 | 2 | 0 | 2 | 3684.720 |
| delegation | 49 | 47 | 0 | 0 | 2 | 79.236 |
| 합계 | 271 | 265 | 2 | 0 | 4 | — |

Skip은 기존 Windows symlink 권한 제한이며 권한을 바꾸지 않았다. 저장소 validator·10라우트·Kernel·payload101 동기화·위임 validator·deterministic evidence·보관 이력·diff 공백 검사는 모두exit0이다. Golden31개는 메타데이터 검증이며31개 실제 모델 과제를 실행했다는 뜻이 아니다.

실패2건은 다음과 같다.

- test_payload_alone_routes_and_supplies_kernel_and_baseline: test_build_plugin.py의 hook stderr 공백 기대에서 git_operation=head timeout 진단을 관측했다.
- test_bool_exit_code_is_not_integer_success: test_hooks.py의 setup에서 git_operation=repository timeout 진단을 관측했다.

둘 다 기존 Git15초 제한 초과다. 특정 Windows 구성요소나 새 제품 코드 결함을 확정하지 못했다. timeout 증가·자동 재시도·실행기 자동 우회·검증 완화는 하지 않았고, 통과만 얻기 위한 추가 전체 실행도 하지 않았다. 이전 통과나 이번 일부 테스트 통과로 실패를 지우지 않는다.

관측기의 초기 진행/집계 파서는 stdout만 읽었으나 unittest는 stderr에 기록했다. 원문 로그·commands.json을 유지하고 normalized_report.json에서 정정했다. 부모도 stderr의 최종 Ran/FAILED/OK 요약을 별도로 파싱해271/265/2/0/4를 확인했다. 사용자 파일 비교에서는 Windows 경로 구분자와 SHA256 문자열의 대소문자 차이도 정규화했다. 이 계측 문제는 제품 테스트 실패2건과 별개다.

## 실제 Claude 세션

Claude Code2.1.309, 요청·실제 모델 모두 claude-sonnet-5-5, medium이다. 원본 답안을 제외한 GT012 합성 fixture와 현재 native plugin 복사본을 사용했다. Skill 성공·SessionStart Kernel 전달·현재 Coding/Review/Context Protocol/Knowledge Governance 네 가이드 Read를 실제 도구/훅 이벤트에서 확인했다.

1. 새 세션이 실패를 재현하고 공유 money.py만 수정했다. 주문·환불 sibling은 유지됐고 기존6테스트를 승인된 래퍼로 통과했다.
2. 별도 session_id의 새 CLI 컨텍스트가 같은 진행 기록을 읽고 실제 소스를 대조한 뒤 한 번 재검증했다. fixture 변경 없이6테스트가 통과했고 실패 이력과 승인 경계를 유지했다.

모델 수정은 제품에 적용하지 않았다. 보호된 테스트와 plugin 바이트는 동일했고, 신뢰된 기존 채점기에서도6/6통과와 공유 파일 수정·테스트 불변·새 의존성 없음이 확인됐다. 저장된 returncode0과 현재 snapshot도 일치했다. 기계적 점수 상한을 실제 rubric100점이나 Golden PASS로 취급하지 않았다.

| 세션 | 모델 프로세스 초 | CLI 추정 USD | 결과 |
|---|---:|---:|---|
| 수정·검증 | 243.576 | 0.1326212 | exit0, money.py만 수정 |
| 새 컨텍스트 재개 | 113.162 | 0.1040054 | exit0, fixture 수정 없음 |

합계 CLI 추정0.2366266 USD는 구독 청구액이 아니다. 다른 작업과 부하가 겹치고 두 세션의 과제도 달라 성능·절감률 비교에 쓰지 않는다.

관찰된 한계:

- 첫 세션은 허용되지 않은 python -c 명령을1회 시도했고 실험 CLI의 allowlist가 차단했다. 이 차단을 TaskForge 자체의 강제 보안 기능으로 설명하지 않는다.
- 첫 보고서의 음수 미지원 설명은 틀렸다. 검토한 parser를 별도로 실행하자 문자열 -1은 정수 -1을 반환했다. 원본 응답·핸드오프는 보존하고 이 보고서에서 정정한다.
- 공백-only 입력은 ValueError, 잘못된 comma grouping은123으로 처리하는 등6테스트 밖의 한계가 남는다.
- 진행 기록은 이 합성 실험에서 의도적으로 Git ignore 대상이었다. tracked 진행 기록을 갱신하는 일반 프로젝트의 snapshot 상호작용까지 검증한 것은 아니다.
- 내장 cc 플러그인3개는 함께 로드됐다. 세션 설정에서 전역 설정 source와 auto-memory를 제한했지만 OS sandbox는 아니다. 이 단일 과제·두 컨텍스트에 A/B 비교·효능·분산·절감 보장은 없다.

## PPT 실제 실행

현재 Presentation/Review/Context/Knowledge 가이드를 따라 Office 검증 에이전트가 합성 소개 PPTX를 만들었다. Claude가 PPT를 생성한 실험으로 취급하지 않는다. 수치는 illustrative라고 표시하고 성능 의미를 부여하지 않았다.

대표2장 먼저 생성→PowerPoint 렌더·시각검사→전체4장 생성 순서로 진행했다. 원본 OOXML 검사기(스킬 office/validate.py)는 샘플·전체 모두 All validations PASSED/exit0이다. native chart1개·표1개·embedded workbook과 한국어 제목을 확인했다.

Windows PowerPoint16.0.20430.20182에서 전체4장을 실제 읽기전용으로 열고1600x900 PNG4개와 PDF를 내보냈다. 작성자와 부모가 각각 전 페이지 이미지를 확인해 눈에 띄는 잘림·겹침·글꼴 누락을 찾지 못했다. 수동 편집·저장 조작이나 스크린리더 검증은 수행하지 않았다.

산출물 이름: TaskForge_validation_20261024.pptx, 133576바이트. SHA256: 35db3f852a30d8de6bbcaa880521b1733a167d2de6b705ded39e23786bda64bb.

최초 defusedxml 의존성 부재와 COM0x80080005 시작 실패, 보호 guard2회 중단을 보존했다. 시작시각·automation 명령줄·빈 창·열린 문서0개로 확인된 작업 소유 orphan PID만 정리하고, 새 STA 인스턴스로 전체 렌더에 성공했다. 문서 Close·Quit 및 해당 프로세스 종료를 확인했다. 성공한 재시도가 간헐 COM 오류의 근본 해결을 증명하지는 않는다.

원본 검사기를 바꾸지 않고 검증 전용 .validator-deps에 defusedxml0.7.1만 준비한 뒤 검사기 자식 PYTHONPATH에만 적용했다. 제품·전역 의존성은 추가하지 않았다. Node24.19.0/pptxgenjs4.0.1/Python3.12.14를 사용했다. 공개 PyPI 휠 다운로드와 Claude API 호출은 수행했고, 누적 제품 diff 전송·외부 메시지·전역/운영 배포는 하지 않았다.

## 증거와 남은 범위

원시 증거는 source checkout과 나란한 workspace 폴더 validation-20261024-full-model-ppt 아래 regression/model/ppt에 있다. 회귀 전후 스냅샷·명령 원문·정규화 집계, 모델 이벤트·검토 diff·독립 채점·핸드오프, PPTX/PDF/PNG·구조 검사·COM 복구 이력을 보존했다. 원시 로그의 사용자 경로·세션 내용은 이 공개용 기록에 복사하지 않았다.

기본 Windows Git 지연 원인은 미확정이고 전체 회귀2실패가 남는다. 이번 Linux/다른 버전 행렬·원격CI·실운영/marketplace 배포·제3자 재배포 권리 확정은 수행하지 않았다. 실제 모델·PPT 실행 성공과 이 제한들을 분리해 유지한다.
