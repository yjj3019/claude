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
- 결과: `ocp-healthcheck-report-<YYYYMMDD-HHMM>-<PID>.txt`와 동일 이름의 `.html`이 현재 디렉터리에 생성됨. `.html`은 브라우저로 열어 우측 상단 "PDF로 저장"으로 PDF 변환 가능.

### 2단계 — 엑셀 자동 반영 (`fill_checklist.py`)

```bash
python3 fill_checklist.py <1단계에서 생성된 .txt> check_reconstructed.xlsx [output.xlsx]
```

- `output.xlsx`를 생략하면 `checklist_filled_<YYYYMMDD-HHMM>.xlsx`로 자동 생성됨.
- **템플릿(`check_reconstructed.xlsx`)은 절대 수정하지 않고**, 항상 새 파일로 결과를 저장함.
- 항목번호(1-1, 2-1~2-32, 3-1-1, 4-1, 5-1 ...)를 기준으로 `.txt` 리포트와 xlsx 행을 1:1 매칭해서 `점검결과`(E열)만 채움. 판정 기준·Command 등 다른 열과 서식(헤더 색상, 컬럼 너비)은 그대로 유지.
- 판정 매핑: `ok`→정상 / `attention`→확인필요 / `skip`→건너뜀 / `manual`→수동확인. ClusterOperator(2절)는 리포트의 판정 문자열(`✅ 정상` / `⚠ 주의(...)` / `❌ 이상(...)`)을 그대로 사용.
- 리포트에 없는 항목은 에러 없이 stderr 경고만 남기고 계속 진행(예: 옛 리포트를 신규 스크립트 버전 xlsx에 대입하는 경우).
- 로직 자체가 정상인지 빠르게 확인하려면:
  ```bash
  python3 fill_checklist.py --self-check
  ```
  (합성 데이터 기반 자체 점검 — 실클러스터 데이터 검증을 대체하지 않음)

### 3단계 — 사람이 해야 하는 부분

- 결과 `checklist_filled_*.xlsx`를 열어 값을 확인.
- 원본 `check.xlsx`(사내 실물 체크리스트)에 반영하려면 이 값을 **사람이 직접 옮겨 적어야 함** — DRM 때문에 자동화 불가(아래 참조).
- 5-3(VM Console 접속)은 대화형 명령이라 스크립트가 자동 실행하지 않음. 리포트에 안내된 명령을 직접 실행해 수동 확인.

## check.xlsx와의 관계 (DRM 제약)

사내 실물 체크리스트 `check.xlsx`는 NASCA DRM으로 wrapping되어 있어 openpyxl/zipfile로 열리지 않는다(`BadZipFile`). 이 저장소의 `check_reconstructed.xlsx`는 그 원본을 사람이 스크린샷으로 옮겨 적어 재현한 **DRM 없는 사본**이며, `fill_checklist.py`가 다루는 대상은 이 사본(또는 동일 구조의 비-DRM 사본)뿐이다. 원본 DRM 파일 자체에 대한 자동 쓰기는 범위 밖이다.

## 항목 수 (참고)

xlsx 5개 시트(1.Cluster구성/2.ClusterOperator/3.API연동/4.Network/5.Virtualization) 총 58개 점검항목. `fill_checklist.py`가 "채움: 58개, 매칭 실패: 0개"를 출력하면 전 항목이 정상 반영된 것.
