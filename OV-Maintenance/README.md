# OV-Maintenance — RHOCP/CNV 정기점검 자동화

RHOCP(+ OpenShift Virtualization) 클러스터를 점검하고, 결과를 점검 체크리스트 xlsx의 `점검결과` 열에 자동으로 반영하는 2단계 도구 모음.

## 구성 파일

| 파일 | 역할 |
|---|---|
| `OCP-HCK-Score.sh` | 클러스터를 점검해 `.txt` 원시 리포트 + `.html` 대시보드를 생성 |
| `fill_checklist.py` | `.txt` 리포트를 파싱해 xlsx 템플릿의 `점검결과` 열을 자동으로 채움 |
| `check_reconstructed.xlsx` | 점검 체크리스트 템플릿 (DRM 없는 사본 — 아래 "check.xlsx와의 관계" 참조) |
| `PROGRESS.md` / `SESSION_LOG.md` | 세션 간 작업 이력 (읽기 전용 참고용, 직접 실행과 무관) |

## 실행 흐름

### 1단계 — 클러스터 점검 (`OCP-HCK-Score.sh`)

사전조건: 실행 서버에 `oc login`이 되어 있어야 함(`oc whoami` 성공).

```bash
cd OV-Maintenance
./OCP-HCK-Score.sh
```

- `jq`가 있으면 ClusterOperator 판정이 더 정확해짐(없어도 동작 — 선택적 저하).
- `virtctl`이 없으면 VM 관련 점검(5-1/5-2/5-3)은 자동으로 건너뜀.
- VM 재기동/실시간 마이그레이션(5-1/5-2)은 운영 영향을 피하기 위해 **기본 비활성**. 필요할 때만:
  ```bash
  RUN_VM_DISRUPTIVE=yes ./OCP-HCK-Score.sh
  ```
- 결과: `ocp-healthcheck-report-<YYYYMMDD-HHMMSS>-<PID>.txt`와 동일 이름의 `.html`이 현재 디렉터리에 생성됨. `.html`은 브라우저로 열어 우측 상단 "PDF로 저장"으로 PDF 변환 가능.

### 2단계 — 엑셀 자동 반영 (`fill_checklist.py`)

가장 간단한 형태 — report.txt 하나만 넘기면 나머지는 자동으로 결정됨:

```bash
python3 fill_checklist.py <1단계에서 생성된 .txt>
# ...
# Result > <같은 이름>.xlsx
```

- `template.xlsx`를 생략하면 이 스크립트와 같은 디렉터리의 `check_reconstructed.xlsx`를 자동으로 사용. 다르게 지정하려면 두 번째 인자로: `fill_checklist.py report.txt other_template.xlsx`
- `output.xlsx`를 생략하면 입력 `.txt`와 같은 이름(`.xlsx` 확장자)으로 저장. 세 번째 인자로 직접 지정 가능: `fill_checklist.py report.txt template.xlsx custom_output.xlsx`
- **템플릿은 절대 수정하지 않음** — output 경로가 템플릿과 같으면 즉시 에러로 거부(원본 파괴 방지).
- 항목번호(1-1, 2-1~2-34, 3-1, 4-1, 5-1 ...)를 헤더 텍스트("번호"/"점검결과")로 열 위치를 찾아 기준 삼아 `.txt` 리포트와 xlsx 행을 1:1 매칭해서 `점검결과` 열만 채움. Command 등 다른 열과 서식(헤더 색상, 컬럼 너비)은 그대로 유지.
- 판정 매핑: `ok`→정상 / `attention`→확인필요 / `skip`→건너뜀 / `manual`→수동확인. ClusterOperator(2절)는 리포트의 판정 문자열(`정상` / `주의(...)` / `이상(...)`)을 그대로 사용 — 2026-09-14부터 이모지 없이 전체 절이 같은 순수 텍스트 어휘를 쓰도록 통일(폐쇄망 구형 Excel에서 이모지가 깨지는 문제, `COUNTIF` 등 엑셀 집계 시 2절만 빠지던 문제 해소).
- 실행 중 섹션별로 그룹핑된 색상 브리핑(`[번호] 설명 -> 판정`)과 마지막에 섹션별/전체 요약 표를 출력함. 터미널이 아니면(파일 리다이렉트 등) 색상은 자동으로 꺼짐.
- 리포트에 없는 항목은 stderr 경고를 남기고 계속 진행하되, 하나라도 있으면 **종료코드 1**로 끝남(자동화/CI가 불완전한 결과를 감지할 수 있도록). 템플릿에 항목번호가 중복되거나 `점검결과` 셀이 병합돼 있는 경우도 경고와 함께 안전하게 스킵됨(크래시하지 않음).
- 로직 자체가 정상인지 빠르게 확인하려면:
  ```bash
  python3 fill_checklist.py --self-check
  ```
  (합성 데이터 + 회귀 케이스 기반 자체 점검 — 실클러스터 데이터 검증을 대체하지 않음)

### 3단계 — 사람이 해야 하는 부분

- 결과 `checklist_filled_*.xlsx`를 열어 값을 확인.
- 원본 `check.xlsx`(사내 실물 체크리스트)에 반영하려면 이 값을 **사람이 직접 옮겨 적어야 함** — DRM 때문에 자동화 불가(아래 참조).
- 5-3(VM Console 접속)은 대화형 명령이라 스크립트가 자동 실행하지 않음. 리포트에 안내된 명령을 직접 실행해 수동 확인.

## 판단 기준 (점검결과가 어떻게 결정되는가)

`fill_checklist.py`는 스스로 판정을 내리지 않는다 — `OCP-HCK-Score.sh`가 리포트에 이미 남긴 기계판독용 마커(`[결과] rc=N` / `skip` / `manual`, 2절의 판정 문자열)를 그대로 옮길 뿐이다. 실제 판단은 아래 두 곳에서 이뤄진다.

### 1) 1·3·4·5절 (run_cmd 기반 항목) — 명령의 종료코드(exit code) 기준

| 리포트 마커 | xlsx 점검결과 | 의미 |
|---|---|---|
| `[결과] rc=0` | **정상** | 해당 항목의 명령이 에러 없이 종료(exit code 0) |
| `[결과] rc=N` (N≠0) | **확인필요** | 명령이 에러 코드로 종료 — 사람이 원본 리포트의 명령 출력을 직접 봐야 함 |
| `[결과] skip` | **건너뜀** | 정책상(예: 5-1/5-2 파괴적 테스트 기본 비활성) 또는 도구 부재(`virtctl` 없음 등)로 애초에 실행하지 않음 |
| `[결과] manual` | **수동확인** | 5-3(VM Console 접속)처럼 대화형이라 자동화가 원천적으로 불가능한 항목 |

→ **"정상"이라도 클러스터가 실제로 건강하다는 뜻이 아니라, 조회 명령 자체가 에러 없이 실행됐다는 뜻**이다. `oc get nodes`가 rc=0으로 성공해도 그 안의 노드 상태가 `NotReady`일 수 있으므로, 정상 판정이 붙은 항목도 리포트 본문(`.txt`의 명령 출력)을 사람이 대조 확인해야 한다(`.sh` 자체가 이 판정을 넘어서는 의미 판단은 하지 않는다고 CLAUDE.md에도 명시).

### 2) 2절 (ClusterOperator) — AVAILABLE/PROGRESSING/DEGRADED 조건 기준

`OCP-HCK-Score.sh`가 34개 Operator마다 `oc get co <name>`(VERSION/SINCE)과 `-o json`의 `status.conditions`(AVAILABLE/PROGRESSING/DEGRADED)를 확인해 우선순위대로 판정한다(`.sh` 140행 부근). 원래 32개 고정 목록에 없던 `control-plane-machine-set`/`olm`은 2026-09-14에 목록 끝에 추가(기존 2-1~2-32 번호·순서는 그대로 유지, 2-33/2-34로만 신규 추가):

1. `DEGRADED=True` → **이상(Degraded)** (최우선)
2. `AVAILABLE≠True` → **이상(Available)**
3. `PROGRESSING=True` → **주의(Progressing)**
4. 위 셋 다 아니면 → **정상**

VERSION/SINCE는 항상 `oc get co <name>` 원본 라인에서 가져오고, `jq`가 있으면 AVAILABLE/PROGRESSING/DEGRADED만 JSON conditions로 더 정확하게 덮어쓴다(2026-09-14부터 jq 유무와 무관하게 모든 컬럼이 채워짐 — 과거의 `[jq 없음 - 원본 확인]` 표기는 제거됨). `oc get co` 자체가 조회 실패면(오브젝트 없음 등) `[조회 실패/미존재]`로 채워지며 이 경우는 사람이 원본을 봐야 한다.

### 브리핑 출력의 색상

`fill_checklist.py` 실행 중 표시되는 색상도 이 판정 문자열을 그대로 분류한 것뿐이다: "이상"·"실패" 포함 → 빨강, "확인필요"·"주의" 포함 → 노랑, "정상" 포함 → 초록, 그 외(건너뜀/수동확인) → 파랑.

## check.xlsx와의 관계 (DRM 제약)

사내 실물 체크리스트 `check.xlsx`는 NASCA DRM으로 wrapping되어 있어 openpyxl/zipfile로 열리지 않는다(`BadZipFile`). 이 저장소의 `check_reconstructed.xlsx`는 그 원본을 사람이 스크린샷으로 옮겨 적어 재현한 **DRM 없는 사본**이며, `fill_checklist.py`가 다루는 대상은 이 사본(또는 동일 구조의 비-DRM 사본)뿐이다. 원본 DRM 파일 자체에 대한 자동 쓰기는 범위 밖이다.

## 항목 수 (참고)

xlsx 5개 시트(1.Cluster구성/2.ClusterOperator/3.API연동/4.Network/5.Virtualization) 총 66개 점검항목(2026-09-14: ClusterOperator 목록에 control-plane-machine-set/olm 추가로 62→64, 이어서 3-11 정지된 Pod 확인·5-12 VM 실행 정책 확인 추가로 64→66). `fill_checklist.py`가 종료코드 0으로 끝나고 요약 표에 "총 66개 채움, 0개 리포트 매칭 실패"가 나오면 전 항목이 정상 반영된 것.

## xlsx 파일은 Windows가 아니라 rhel-prod에서 수정할 것

`check_reconstructed.xlsx`를 새로 만들거나 행을 추가/수정하는 작업은 **반드시 rhel-prod(Linux)에서** 해야 한다. Windows 로컬에는 사내 NASCA DRM 에이전트가 상주하면서 xlsx 파일이 Windows에서 생성/저장되면 자동으로 DRM을 씌우는데, 그러면 openpyxl이 `BadZipFile`로 열지 못하게 된다(원본 `check.xlsx`가 애초에 못 열렸던 것과 동일한 증상 — 2026-09-11/14에 "원인불명 손상"으로 오인했던 현상의 정체). Windows 로컬의 xlsx 사본은 rhel-prod에서 완성한 결과를 내려받아 열어보는 용도로만 사용할 것.

## rc(종료코드) 정확도에 대한 주의 — 2026-09-11 수정됨

"판단 기준" 절에서 설명한 대로 1·3·4·5절의 정상/확인필요 판정은 `run_cmd`가 실행한 명령의 종료코드(rc)에 의존한다. 과거에는 여러 `oc` 명령을 `bash -c "cmd1; cmd2"`처럼 한 블록에 묶어 실행하는 13개 항목(3-1~3-6, 4-1~4-5, 5-6, 5-7 — 2026-09-14 넘버링 변경 전 표기로는 3-1-1~3-1-6)에서 **블록의 마지막 명령(또는 장식용 `echo`)의 종료코드만** rc로 기록되는 결함이 있었다 — 예를 들어 4-4는 `oc describe pod`가 실패해도 그 뒤의 `echo ''`가 성공하기 때문에 rc는 항상 0이었다. 이는 Codex/Opus 적대적 리뷰에서 발견되어 수정됐다(각 블록이 이제 `rc=0; cmd || rc=$?; ...; exit $rc` 패턴으로 실행된 모든 명령 중 최악의 실패를 rc에 반영함). 이 수정 이전에 생성된 `.txt` 리포트는 위 13개 항목에 한해 "정상"이 실제로는 부분 실패였을 가능성이 있으니, 오래된 리포트를 근거로 삼고 있다면 재실행을 권장한다.
