# PROGRESS.md - 세션 핸드오프 & 상태 관리

## 📍 현재 상태 (Session Status)
- 세션 시작: 2026-09-10 (다중 세션에 걸쳐 진행, 마지막 갱신 2026-09-11)
- 마지막 작업: **Codex + Opus 독립 적대적 리뷰로 `fill_checklist.py` 정밀 검토 → 발견된 결함 전부 수정, 동시에 리뷰에서 드러난 `OCP-HCK-Score.sh`의 rc 마스킹 Critical 버그(13개 항목)도 별도로 수정.** 둘 다 rhel-prod 실클러스터에서 재검증 완료.
- 진행률: `fill_checklist.py`는 이제 단일 인자(`<report.txt>`)만으로 실행 가능(템플릿/출력 경로 자동 결정, `Result > <output>.xlsx` 형식), 섹션별 색상·정렬된 브리핑 출력 + 요약 표 제공, README에 판단 기준 문서화 완료. `OCP-HCK-Score.sh`는 다중 명령 `bash -c` 블록 13곳의 rc 마스킹(마지막 명령/장식용 echo가 앞선 명령의 실패를 가려 항상 rc=0이 되던 문제)을 rc 전파 방식으로 수정, 실패 재현 테스트로 검증(수정 전 패턴은 rc=0, 수정 후 rc=1 확인). 원본 DRM `check.xlsx` 자체에 대한 자동 반영은 여전히 대상 밖(사용자 수작업).
- 블로커: `check.xlsx`가 NASCA DRM으로 wrapping되어 있어 Claude가 직접 열람/수정 불가 — `fill_checklist.py`는 DRM 없는 `check_reconstructed.xlsx`(또는 동일 구조 사본)만 대상으로 하며, 원본 DRM 파일 자동화는 범위 밖.

## ✅ 완료된 항목 (Done)
- **버그 수정 5건(정밀분석 1차)**: CO VERDICT 판정 우선순위(Degraded>Available>Progressing) if/elif 화, `run_cmd`의 `&&`체인/`if`무-else로 인한 성공·실패 오판정 다수 수정(3-1-1~3-1-6, 4-1~4-4, 5-4/5-5), 3-1-7 `bash -c` 내부 `set -o pipefail` 미상속 수정, 고정 32개 Operator 목록 밖 항목 탐지 로직 추가, SNO 자기ping 안내·CNV 스킵 사유 구분(VM없음/virtctl없음/정책스킵) | 파일: [OCP-HCK-Score.sh](OCP-HCK-Score.sh)
- **HTML/PDF 리포트 기능 내장**: python3 heredoc을 스크립트 안에 임베드해 .txt 생성 직후 자동으로 .html 대시보드까지 생성(노드 토폴로지, CO 상태 도넛, 섹션별 수집현황 바, 접이식 항목 카드). 브라우저 인쇄(Ctrl+P)로 PDF 저장 — 외부 라이브러리 의존성 없음, python3 없으면 텍스트 리포트만 생성(선택적 저하)
- **Codex + Opus 독립 적대적 리뷰 → Fable 종합**: 3단계 팀 리뷰로 Critical 4건(C1 jq없을때 파서 크래시, C2 "전체정상" 배지 신뢰성, C3 VM 파괴테스트 안전장치 부재, C4 run_cmd 실패 미누적/exit 항상 0) + Major 5건(M1 동시실행 파일충돌, M3 민감정보 권한, M4 비UTF-8 크래시, M5 폐쇄망 폰트요청, M6 meta charset)을 Top5 순서로 서브에이전트 통해 순차 수정·rhel-prod 실클러스터 검증 완료
- **리포트 디자인 고도화**: 따뜻한 종이톤 팔레트 + serif 표지 헤더 + 섹션 "01~05+부록" 번호화 + `@page A4` 인쇄 규격 — Google Fonts 외부요청은 재추가하지 않음(폐쇄망 정책 유지)
- **외부 OCP 점검 저장소 리서치(Deep Dive)**: 사용자가 제시한 15개 저장소 목록을 GitHub API로 실재 검증(`openshift/openshift-mcp-server`는 fork임을 확인, `guchen11/ocp-health-crew`는 신뢰도 과대평가로 판단 등) 후 `redhat-cop/openshift_virtualization_migration`의 healthcheck role을 실제로 읽어 반영 가치 있는 3개 항목 도출
- **신규 점검 항목 3개 추가**: `check.xlsx`(사용자 업로드, DRM으로 직접 열람 불가 — 스크린샷으로 내용 확인) 대조 결과 xlsx가 완전 고정 구조(1-1~1-3/2-1~2-32/3-1-1~3-3-1/4-1~4-4/5-1~5-6)임을 확인 → 사용자 선택("스크립트+xlsx 둘 다")에 따라 스크립트에 1-4(kubevirt.io/schedulable 라벨)/4-5(Multus·OVN-K Pod 상태)/5-7(KubeVirt/CDI 플랫폼 컴포넌트) 추가, 합성 리포트로 로컬 파싱 검증 완료
- **check_reconstructed.xlsx 생성**: DRM 걸린 원본을 대신할 실제(비-DRM) xlsx를 openpyxl로 새로 제작 — 점검개요/1~5.섹션/결과요약 7개 시트 전부, 원본 서식(남색 헤더·노란 점검결과 칸)과 원본의 오탈자("3.API연동" 시트 소제목이 3-2/3-3이 아니라 "5-2."/"5-3."인 것)까지 그대로 재현. 신규 항목 1-4/4-5/5-7은 연두색+"[신규] 2026-09-11 추가" 비고로 구분 표시 | 파일: [check_reconstructed.xlsx](check_reconstructed.xlsx)
- **fill_checklist.py 구현(서브에이전트 위임, 오케스트레이터 검증 후 병합)**: `OCP-HCK-Score.sh` `.txt` 리포트 → xlsx `점검결과` 열 자동 채우기 스크립트. `.sh` 495~611행에 이미 내장된 파싱 로직(`ITEM_HDR`/`RESULT_LINE`/`parse_items`, 2절 파이프 파싱)을 새로 설계하지 않고 그대로 이식. 상태 매핑(`ok`→정상/`attention`→확인필요/`skip`→건너뜀/`manual`→수동확인), 2절은 리포트의 판정 문자열을 그대로 승계. 원본 템플릿은 건드리지 않고 별도 출력 파일(`checklist_filled_<날짜시각>.xlsx`)로 저장. self-check(`--self-check`) 내장 | 파일: [fill_checklist.py](fill_checklist.py)
- **rhel-prod 실클러스터 end-to-end 검증 + 실버그 발견·수정**: 사용자가 원격 경로(`/home/jjyoo/OV-Maintenance`)에 파일이 없다고 지적 → uploadFile 재시도했더니 이번엔 성공(이전 2회 실패는 일시적). 최신 `OCP-HCK-Score.sh` 업로드 후 실제 클러스터에서 재실행해 58항목 전체를 담은 신규 리포트(`ocp-healthcheck-report-20260911-105254-2093740.txt`) 확보 → `fill_checklist.py` 최초 실행 결과 "채움 35개/매칭실패 0개"로 23개 항목(ClusterOperator 2-10~2-32)이 통째로 누락된 것을 발견. 원인: `ITEM_NUM_RE = r"^\d-\d(-\d)?$"`가 숫자를 한 자리로만 매칭 — 두 자리 항목번호를 걸러버림. `r"^\d+-\d+(-\d+)?$"`로 수정하고 self-check에 2자리 회귀 테스트 추가, 재실행으로 58개 전부 정확히 채워짐(매칭 실패 0) 확인, 4-2(명령 실패)가 "확인필요"로 실제 경고와 일치하게 반영됨을 표본 대조로 검증 | 커밋: `bd6869c`
- **fill_checklist.py UX 개선 라운드**: README.md 신규 작성(전체 실행 흐름·판단 기준 문서화, 정상=명령 성공이지 클러스터 건강 보증 아니라는 점 명시) · 실행 중 항목별 브리핑 출력 추가(`[번호] 설명 -> 판정`) · Windows cp949 콘솔 이모지 크래시 수정(stdout/stderr UTF-8 reconfigure) · 섹션별 색상+CJK 폭 기준 정렬+요약 표 추가(OCP-HCK-Score.sh와 동일 색상 팔레트) · CLI 단순화(`<template>`/`<output>` 생략 가능, 출력은 `Result > <report>.xlsx` 형식)
- **Codex + Opus 독립 적대적 리뷰 (fill_checklist.py) → 발견 결함 전부 수정**: 사용자 요청으로 codex-rescue + code-reviewer(model=opus) 병렬 실행, "결함 발굴" 목적 명시(엣지케이스 3개 이상·숨은 가정 지적 요구). 교차 확인된 결함을 전부 수정: (Codex Critical) xlsx 항목번호 공백 시 무경고 누락 → strip 처리 / (Major) `ITEM_HDR` 한 자리 숫자만 매칭 → `\d+`로 통일 / 매칭 실패해도 exit 0 → `missing` 있으면 exit 1 / E열 위치 하드코딩 → 헤더 텍스트("번호"/"점검결과") 기준 동적 탐색, 병합셀 감지 시 에러 처리 / 항목번호 중복 시 카운트 중복 → dedup / `parse_items`의 고정 4줄 오프셋 → 닫는 DASH를 실제로 탐색하는 방식으로 교체(Command 여러 줄일 때 블록 붕괴 방지) / `[결과]` 마커 중복 시 무경고 흡수 → 경고 로그 / SEP `startswith` 완화 → 정확 일치 / 2절 파싱 `2-`+`|` 아무 줄 매칭 → `^2-\d+\s*\|` 앵커 / 템플릿=출력 경로 동일 시 원본 파괴 가능 → 가드 추가 / 모듈 임포트 시 stdout 변형 부작용 → main()/self-check 진입 시로 이동. self-check에 각 수정의 회귀 테스트 추가, 실템플릿+실58항목 리포트로 재검증(exit 0) | 커밋: `4e9fac1`
- **Opus 리뷰 Critical(C1) — OCP-HCK-Score.sh rc 마스킹 버그 수정**: 제가 `.sh` 원본을 직접 읽어 독립 검증 — `bash -c "cmd1; cmd2"` 형태로 여러 명령을 묶어 실행하는 13개 항목(3-1-1~3-1-6/4-1~4-5/5-6/5-7)이 **마지막 명령(또는 장식용 `echo ''`)의 종료코드만** rc로 기록해, 앞선 명령이 실패해도 rc=0으로 "정상" 기록되는 구조적 결함이었음(4-4는 `describe pod` 실패해도 뒤의 `echo ''` 때문에 상시 rc=0). `rc=0; cmd || rc=$?; ...; exit $rc` 패턴으로 13개 블록 전부 수정 — 기존처럼 실패 후에도 나머지 명령은 계속 실행하되(set -e 미사용, 증거 수집 유지) 최종 rc는 실제 최악의 실패를 반영. 존재하지 않는 Pod로 수정 전/후 패턴을 직접 재현 테스트해 rc=0→rc=1 전환 확인, `bash -n`·임베드 python `py_compile`·rhel-prod 실행(58항목 정상) 전부 통과. 임베드 HTML 파서의 `ITEM_HDR`도 fill_checklist.py와 동일하게 `\d+` 다자리로 동기화 | 커밋: `dff2068`

## 🔄 진행 중 / 다음 우선순위 (Next)
1. **사용자: 원본 check.xlsx(DRM)에 반영 여부 결정** — `check_reconstructed.xlsx`의 신규 3행(1-4/4-5/5-7, 연두색 표시)을 그대로 원본 DRM 파일에 수동 입력하거나, 재구성본을 새 체크리스트로 채택할지 결정. Claude는 DRM 파일을 직접 열 수 없어 이 이상 자동화 불가 — `fill_checklist.py`도 DRM 원본은 대상으로 하지 않음.
2. **(낮은 우선순위, 보류 중 재검토)** Fable 리포트의 잔여 Minor 항목들(M7 4-2 dns-default ICMP fallback을 TCP체크로 교체, M9 플레이스홀더 치환 순서 리스크) 및 이번 Codex/Opus 리뷰에서 의도적으로 보류한 항목(2/1·3·4·5절 판정 어휘 혼재 — 이모지 vs 한글, `check_reconstructed.xlsx`의 병합셀 실제 여부 미확인) — 사용자가 명시적으로 요청할 때만 진행. (M2 bash -c 중간명령 실패 마스킹은 이번에 완료 처리됨.)

## ⚠️ 결정 및 트레이드오프 (Decisions)
- **HTML 생성은 python3 선택적 의존성으로 설계**: jq/virtctl과 동일한 선택적-저하 패턴 유지. 이유: 폐쇄망 bastion에 python3가 없을 가능성을 배제할 수 없음(실제로는 RHEL8/9 기본 포함이라 위험 낮음).
- **PDF는 별도 라이브러리 없이 브라우저 print-to-PDF만 지원**: `[Codex/Opus 리뷰]` 긴 로그 줄 잘림·DOM 폭증 등 실무 한계가 있음을 인지하고도 채택 — 폐쇄망에서 외부 PDF 라이브러리(CDN) 로드가 불가능하고, 순수 python PDF 생성 라이브러리 추가는 의존성 부담 대비 이득이 낮다고 판단(YAGNI).
- **xlsx 번호 체계는 고정, 스크립트가 임의로 새 번호를 만들지 않는다는 원칙을 재확인**: 사용자가 "왜 그냥 추가 못하냐"고 질문했을 때, 기술적 불가능이 아니라 "xlsx에 대응 행이 없으면 옮겨적을 곳이 없다"는 워크플로 문제임을 명확히 하고, 최종적으로 "스크립트+xlsx 둘 다 갱신"으로 사용자가 직접 선택.
- **`[Codex 리뷰]`**: run_cmd exit code 항상 0(cron 감지 불가)을 Critical로 지적 — Opus는 Minor로 봤으나 Fable 종합에서 "C2 오판정의 근본 원인"이라는 이유로 Critical 채택.
- **`[Codex 리뷰]`**: curl -k(TLS 검증 생략)을 Major로 지적했으나 Fable 검증에서 "OCP Route는 자체서명 CA가 일반적이고 목적이 도달성 확인"이라는 이유로 기각.

## 🧠 Handoff Notes (다음 세션에게)
- OCP-HCK-Score.sh는 이제 980+ 줄(HTML/PDF 기능 포함)로 커짐 — 수정 시 반드시 `bash -n`과 임베드 python heredoc의 `py_compile`(추출 후) 둘 다 확인.
- 로컬(Windows, python 3.14 + openpyxl 설치됨)과 rhel-prod(RHEL, python 3.9.25) 양쪽에서 동작 검증된 상태 — 로컬 python 버전 차이로 인한 문법 이슈 없음(f-string만 사용, 3.9 호환).
- `check.xlsx`는 NASCA DRM 파일이라 Claude Code에서 zip/openpyxl로 직접 열리지 않음(`BadZipFile`) — 향후 이 파일을 다시 열어야 할 일이 있으면 사용자에게 복호화 저장 요청 필요. 대신 사용자가 스크린샷으로 제공한 내용을 바탕으로 `check_reconstructed.xlsx`(DRM 없는 순정 xlsx, openpyxl로 생성)를 만들어뒀음 — 향후 항목을 더 추가/수정할 때는 이 파일이 진짜 소스 오브 트루스 역할을 할 수 있음(스크립트 빌드 스크립트: 스크래치패드의 `build_checklist_xlsx.py`, 세션 재시작 시 사라지므로 재사용하려면 다시 작성 필요 — 파일 자체는 OV-Maintenance/에 영구 저장됨).
- `fill_checklist.py` 사용법: `python3 fill_checklist.py <report.txt> check_reconstructed.xlsx [output.xlsx]`. rhel-prod(`/home/jjyoo/OV-Maintenance`)에 최신 `OCP-HCK-Score.sh`·`fill_checklist.py`·`check_reconstructed.xlsx` 모두 업로드되어 있어 바로 실행 가능.
- **self-check(합성 데이터)만으로는 부족하다는 교훈**: `--self-check`가 통과했고 로컬에서도 7항목짜리 합성 리포트로 "검증 완료"라고 판단했지만, 실제 58항목 전체를 처리하자 `ITEM_NUM_RE`가 두 자리 항목번호(2-10~2-32)를 걸러내는 버그가 드러났다. self-check/합성테스트가 커버하지 않는 값 범위(여기선 두 자리 번호)가 있으면 실데이터 전수 실행 전까지 숨어있을 수 있다 — 숫자 범위·개수 경계가 있는 파싱 로직은 실제 최대/최소 케이스를 self-check에 반드시 포함시킬 것.
- rhel-prod `uploadFile`은 2026-09-11 재시도에서 정상 동작함 — 이전 2회 연속 실패는 재현되지 않아 원인 미상으로 종결(더 이상 조사 안 함).

## 📈 MCP 상태
- 세션 도중 데스크톱 앱으로 환경 전환되며 다수 MCP 서버 재연결/해제됨(Notion, Figma, Slack 등 다수 UUID화된 커넥터). 이 프로젝트 작업에 필요한 것은 `mcp-ssh`(rhel-prod/rhel-storage)뿐이며 현재 rhel-prod 연결 불가 상태.

## 🤖 서브에이전트 현황 (해당 시)
- 전부 완료됨: code-reviewer(정밀분석), codex-rescue(적대적 리뷰), code-reviewer+model=opus(적대적 리뷰), fable 종합 리포트, fork×5(Top5 순차 수정: C1→C4→C2→C3→M-bundle), fork(외부 저장소 딥다이브 리서치). 브리프 파일은 별도로 남기지 않고 프롬프트 인라인 전달 방식 사용(.agent/handoff/ 미사용) — 향후 재현 필요 시 본 세션 대화 로그가 유일한 기록.

## 📎 Notion 기록 URL
- 미기록 (Notion MCP 미연결 상태로 세션 진행 — SESSION_LOG.md로 폴백)
