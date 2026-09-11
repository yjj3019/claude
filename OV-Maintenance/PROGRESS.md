# PROGRESS.md - 세션 핸드오프 & 상태 관리

## 📍 현재 상태 (Session Status)
- 세션 시작: 2026-09-10 (다중 세션에 걸쳐 진행, 마지막 갱신 2026-09-11)
- 마지막 작업: `fill_checklist.py` 신규 구현 완료 — `OCP-HCK-Score.sh` `.txt` 리포트를 파싱해 `check_reconstructed.xlsx` 사본의 `점검결과`(E열)를 항목번호 기준 자동 채움. 서브에이전트(implementer)가 격리 워크트리에서 구현·self-check·실제 템플릿 CLI 경로 검증까지 완료, 오케스트레이터가 결과를 재검증(포맷 보존·원본 미변경 확인) 후 작업 디렉터리에 병합.
- 진행률: xlsx 자동 채우기 스크립트 완료(합성 리포트 기준 61개 항목 중 매칭 규칙 검증 완료) / 실클러스터 `.txt` 리포트로 최종 검증은 아직 — rhel-prod 업로드 실패로 보류 / 원본 DRM `check.xlsx` 자체에 대한 자동 반영은 대상 밖(여전히 사용자 수작업)
- 블로커: (1) rhel-prod(172.21.18.20) — `checkConnectivity`는 성공하나 `uploadFile`이 원인 불명으로 2회 연속 실패 → 실제 `.sh` 실행·실클러스터 리포트 확보 불가 상태(재시도 필요). (2) `check.xlsx`가 NASCA DRM으로 wrapping되어 있어 Claude가 직접 열람/수정 불가 — `fill_checklist.py`는 DRM 없는 `check_reconstructed.xlsx`(또는 동일 구조 사본)만 대상으로 하며, 원본 DRM 파일 자동화는 범위 밖.

## ✅ 완료된 항목 (Done)
- **버그 수정 5건(정밀분석 1차)**: CO VERDICT 판정 우선순위(Degraded>Available>Progressing) if/elif 화, `run_cmd`의 `&&`체인/`if`무-else로 인한 성공·실패 오판정 다수 수정(3-1-1~3-1-6, 4-1~4-4, 5-4/5-5), 3-1-7 `bash -c` 내부 `set -o pipefail` 미상속 수정, 고정 32개 Operator 목록 밖 항목 탐지 로직 추가, SNO 자기ping 안내·CNV 스킵 사유 구분(VM없음/virtctl없음/정책스킵) | 파일: [OCP-HCK-Score.sh](OCP-HCK-Score.sh)
- **HTML/PDF 리포트 기능 내장**: python3 heredoc을 스크립트 안에 임베드해 .txt 생성 직후 자동으로 .html 대시보드까지 생성(노드 토폴로지, CO 상태 도넛, 섹션별 수집현황 바, 접이식 항목 카드). 브라우저 인쇄(Ctrl+P)로 PDF 저장 — 외부 라이브러리 의존성 없음, python3 없으면 텍스트 리포트만 생성(선택적 저하)
- **Codex + Opus 독립 적대적 리뷰 → Fable 종합**: 3단계 팀 리뷰로 Critical 4건(C1 jq없을때 파서 크래시, C2 "전체정상" 배지 신뢰성, C3 VM 파괴테스트 안전장치 부재, C4 run_cmd 실패 미누적/exit 항상 0) + Major 5건(M1 동시실행 파일충돌, M3 민감정보 권한, M4 비UTF-8 크래시, M5 폐쇄망 폰트요청, M6 meta charset)을 Top5 순서로 서브에이전트 통해 순차 수정·rhel-prod 실클러스터 검증 완료
- **리포트 디자인 고도화**: 따뜻한 종이톤 팔레트 + serif 표지 헤더 + 섹션 "01~05+부록" 번호화 + `@page A4` 인쇄 규격 — Google Fonts 외부요청은 재추가하지 않음(폐쇄망 정책 유지)
- **외부 OCP 점검 저장소 리서치(Deep Dive)**: 사용자가 제시한 15개 저장소 목록을 GitHub API로 실재 검증(`openshift/openshift-mcp-server`는 fork임을 확인, `guchen11/ocp-health-crew`는 신뢰도 과대평가로 판단 등) 후 `redhat-cop/openshift_virtualization_migration`의 healthcheck role을 실제로 읽어 반영 가치 있는 3개 항목 도출
- **신규 점검 항목 3개 추가**: `check.xlsx`(사용자 업로드, DRM으로 직접 열람 불가 — 스크린샷으로 내용 확인) 대조 결과 xlsx가 완전 고정 구조(1-1~1-3/2-1~2-32/3-1-1~3-3-1/4-1~4-4/5-1~5-6)임을 확인 → 사용자 선택("스크립트+xlsx 둘 다")에 따라 스크립트에 1-4(kubevirt.io/schedulable 라벨)/4-5(Multus·OVN-K Pod 상태)/5-7(KubeVirt/CDI 플랫폼 컴포넌트) 추가, 합성 리포트로 로컬 파싱 검증 완료
- **check_reconstructed.xlsx 생성**: DRM 걸린 원본을 대신할 실제(비-DRM) xlsx를 openpyxl로 새로 제작 — 점검개요/1~5.섹션/결과요약 7개 시트 전부, 원본 서식(남색 헤더·노란 점검결과 칸)과 원본의 오탈자("3.API연동" 시트 소제목이 3-2/3-3이 아니라 "5-2."/"5-3."인 것)까지 그대로 재현. 신규 항목 1-4/4-5/5-7은 연두색+"[신규] 2026-09-11 추가" 비고로 구분 표시 | 파일: [check_reconstructed.xlsx](check_reconstructed.xlsx)
- **fill_checklist.py 구현(서브에이전트 위임, 오케스트레이터 검증 후 병합)**: `OCP-HCK-Score.sh` `.txt` 리포트 → xlsx `점검결과` 열 자동 채우기 스크립트. `.sh` 495~611행에 이미 내장된 파싱 로직(`ITEM_HDR`/`RESULT_LINE`/`parse_items`, 2절 파이프 파싱)을 새로 설계하지 않고 그대로 이식. 상태 매핑(`ok`→정상/`attention`→확인필요/`skip`→건너뜀/`manual`→수동확인), 2절은 리포트의 판정 문자열을 그대로 승계. 원본 템플릿은 건드리지 않고 별도 출력 파일(`checklist_filled_<날짜시각>.xlsx`)로 저장. self-check(`--self-check`) 내장, 오케스트레이터가 재검증: 합성 리포트로 CLI 전체 경로 실행 시 7개 항목만 정확히 채워지고 나머지는 크래시 없이 경고만 남김, 원본 서식(헤더 색상·컬럼 너비) 보존, 원본 파일 미변경 확인. 워크트리 커밋 `b0d60d3`, 파일은 작업 디렉터리(`OV-Maintenance/fill_checklist.py`)에 병합 완료 | 파일: [fill_checklist.py](fill_checklist.py)

## 🔄 진행 중 / 다음 우선순위 (Next)
1. **rhel-prod 실클러스터로 fill_checklist.py 최종 검증** — AC: rhel-prod `uploadFile` 실패 원인 파악 후 재시도(또는 대체 전송 경로) → `OCP-HCK-Score.sh` 실행해 실제 `.txt` 리포트 확보 → `fill_checklist.py <report> check_reconstructed.xlsx`로 61개 항목 전부가 실데이터로 정확히 채워지는지 확인.
2. **사용자: 원본 check.xlsx(DRM)에 반영 여부 결정** — `check_reconstructed.xlsx`의 신규 3행(1-4/4-5/5-7, 연두색 표시)을 그대로 원본 DRM 파일에 수동 입력하거나, 재구성본을 새 체크리스트로 채택할지 결정. Claude는 DRM 파일을 직접 열 수 없어 이 이상 자동화 불가 — `fill_checklist.py`도 DRM 원본은 대상으로 하지 않음.
3. **(낮은 우선순위, 보류 중 재검토)** Fable 리포트의 Minor 항목들(M2 bash -c 블록 중간명령 실패 마스킹, M7 4-2 dns-default ICMP fallback을 TCP체크로 교체, M9 플레이스홀더 치환 순서 리스크) — 사용자가 명시적으로 요청할 때만 진행.

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
- 재개 명령: rhel-prod VPN 연결 확인 후 "1-4/4-5/5-7 실클러스터 검증 진행해줘"라고 요청하면 즉시 업로드→실행→다운로드 검증 재개.
- `fill_checklist.py` 사용법: `python3 fill_checklist.py <report.txt> check_reconstructed.xlsx [output.xlsx]`. rhel-prod에서 받은 실제 `.txt` 리포트가 생기면 바로 이 명령으로 검증 가능 — self-check(`python3 fill_checklist.py --self-check`)는 합성 데이터만 쓰므로 실데이터 검증을 대체하지 않는다.
- rhel-prod `uploadFile`이 `checkConnectivity` 성공에도 불구하고 실패함(2026-09-11 재확인, 2회 연속) — SSH 자체는 살아있으니 `runRemoteCommand`로 원인(디스크/권한/전송 프로토콜) 먼저 진단 필요.

## 📈 MCP 상태
- 세션 도중 데스크톱 앱으로 환경 전환되며 다수 MCP 서버 재연결/해제됨(Notion, Figma, Slack 등 다수 UUID화된 커넥터). 이 프로젝트 작업에 필요한 것은 `mcp-ssh`(rhel-prod/rhel-storage)뿐이며 현재 rhel-prod 연결 불가 상태.

## 🤖 서브에이전트 현황 (해당 시)
- 전부 완료됨: code-reviewer(정밀분석), codex-rescue(적대적 리뷰), code-reviewer+model=opus(적대적 리뷰), fable 종합 리포트, fork×5(Top5 순차 수정: C1→C4→C2→C3→M-bundle), fork(외부 저장소 딥다이브 리서치). 브리프 파일은 별도로 남기지 않고 프롬프트 인라인 전달 방식 사용(.agent/handoff/ 미사용) — 향후 재현 필요 시 본 세션 대화 로그가 유일한 기록.

## 📎 Notion 기록 URL
- 미기록 (Notion MCP 미연결 상태로 세션 진행 — SESSION_LOG.md로 폴백)
