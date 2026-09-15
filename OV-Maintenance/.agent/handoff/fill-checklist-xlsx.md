# Task: fill_checklist.py — OCP-HCK-Score.sh 리포트를 xlsx 점검결과 열에 자동 반영

## Goal
`OCP-HCK-Score.sh`가 생성하는 `.txt` 리포트를 파싱해서, `check_reconstructed.xlsx`(또는 동일 구조의 사본)의 각 시트 `점검결과`(E열) 셀을 항목번호 기준으로 자동으로 채우는 독립 실행형 python3 스크립트를 작성한다.

## Acceptance Criteria
- `.txt` 리포트의 61개 항목(1-1~1-4, 2-1~2-32, 3-1-1~3-3-1, 4-1~4-5, 5-1~5-7) 전부가 xlsx 사본의 대응 시트·행 `점검결과` 열(E열)에 정확히 1:1로 채워진다.
- 원본 xlsx 파일은 건드리지 않고 별도 출력 파일(`checklist_filled_<YYYYMMDD-HHMM>.xlsx`)로 저장한다.
- 원본 서식(헤더 색상, 병합셀, 열 너비 등)은 그대로 유지된다 — `.value`만 쓰고 셀 스타일/서식 객체는 건드리지 않는다.
- 리포트에 없는 항목(스크립트 버전 불일치 등으로 매칭 실패)은 에러로 죽지 않고 경고 로그만 남기고 계속 진행한다.
- 결과 판정 매핑: `ok`→"정상", `attention`→"확인필요", `skip`→"건너뜀", `manual`→"수동확인". 2절(ClusterOperator)은 리포트의 판정 문자열("✅ 정상"/"⚠ 주의(...)"/"❌ 이상(...)")을 그대로 승계한다(재매핑하지 않음).
- 비-trivial 로직(파싱)에 대해 1개의 runnable self-check를 남긴다(합성 샘플 `.txt`를 만들어 파싱 결과를 assert하는 `if __name__ == "__main__"` 데모 또는 별도 `test_fill_checklist.py` 중 더 가벼운 쪽 — 프레임워크·픽스처 불필요).

## Constraints
- **파싱 로직은 새로 설계하지 말고 재사용/이식하라**: `OCP-HCK-Score.sh` 495~580행에 이미 내장된 python heredoc의 `ITEM_HDR`/`RESULT_LINE` 정규식과 `parse_items()` 함수, 그리고 2절(ClusterOperator)의 `2-N | Operator | AVAIL | PROG | DEG | 판정` 파이프 라인 파싱 로직(599~611행 부근)이 정확히 이 목적으로 이미 존재한다. 그대로 가져와서 재사용할 것 — 새 정규식을 만들지 말 것(YAGNI).
- xlsx의 시트명/열 구성은 이미 확정됨: 시트 `1.Cluster구성`/`2.ClusterOperator`/`3.API연동`/`4.Network`/`5.Virtualization`, 각 시트 1행이 헤더(`번호`/`점검 항목`/`Command`/`정상 판정 기준`/`점검결과`/`비고`), A열=번호, E열=점검결과. `3.API연동` 시트에는 항목이 아닌 소제목 배너 행(A열에 "3-1. ..." 같은 긴 문자열)이 섞여 있으니 번호 형식(`^\d-\d(-\d)?$`)으로 걸러야 한다.
- 이 저장소는 `bash -uo pipefail`을 쓰는 기존 `.sh`와 별개로 독립 python3 스크립트다. 새 bash 파일이나 기존 `.sh` 수정은 하지 말 것 — `fill_checklist.py` 1개 파일만 신규 작성.
- Windows(python 3.14)·RHEL(python 3.9.25) 양쪽에서 동작해야 하므로 3.9 호환 문법만 사용(f-string은 가능, match문/새 타입힌트 문법 금지).
- CLI 사용법: `python3 fill_checklist.py <report.txt> <template.xlsx> [output.xlsx]` (output 생략 시 `checklist_filled_<날짜시각>.xlsx` 자동 생성)
- 의존성은 이미 로컬에 설치된 openpyxl만 사용(추가 설치 금지).

## Inputs
- `OCP-HCK-Score.sh` (이 디렉터리) — 파싱 로직 원본(495~650행 부근), 항목 구조 확인용
- `check_reconstructed.xlsx` (이 디렉터리) — 템플릿 xlsx (읽기 전용으로 참고, 테스트 시 복사본 사용할 것 — 원본 건드리지 말 것)
- 실클러스터 실제 `.txt` 리포트는 현재 없음(rhel-prod 업로드 실패로 미확보) — self-check용 합성 리포트를 직접 만들어 사용할 것. 합성 리포트는 실제 `.sh`의 `item_header`/`run_cmd`/`raw "[결과] ..."` 출력 포맷을 정확히 재현해야 한다(포맷은 `.sh` 54~80행 참조).

## Output
- `fill_checklist.py` (이 디렉터리에 신규 파일)
- self-check 결과(성공/실패, 어떤 항목이 채워졌는지 요약)를 이 핸드오프 파일 하단에 "## Result" 섹션으로 append
- 실행해서 만든 테스트용 출력 xlsx/합성 txt는 임시 경로에 두고 저장소에는 커밋 대상 파일(`fill_checklist.py`)만 남길 것

## Result

- 구현 완료: `fill_checklist.py` (OV-Maintenance 디렉터리, 신규 1개 파일).
- 파싱 로직(`ITEM_HDR`/`RESULT_LINE`/`parse_items`, 2절 파이프 라인 파싱)은 `OCP-HCK-Score.sh` 542~611행에서 그대로 이식. 새 정규식 없음.
- self-check: `python3 fill_checklist.py --self-check` — **성공**.
  - `SAMPLE_REPORT`(내장 합성 리포트, `.sh`의 `item_header`/`run_cmd`/`[결과]` 포맷 재현)를 파싱해 1-1(rc=0→정상), 1-2(rc=1→확인필요), 2-1/2-2(판정 문자열 그대로 승계), 3-1-1(정상), 4-1(skip→건너뜀), 5-3(manual→수동확인) 상태 매핑을 assert.
  - 최소 workbook을 메모리에서 만들어 `fill_workbook()` 호출 → E열 채움, 리포트에 없는 항목(1-3)은 크래시 없이 "매칭 실패" 목록에만 기록됨을 assert. `3.API연동` 시트의 배너 행("3-1. ...")은 번호 정규식에 걸러져 E열이 그대로 `None`임을 assert.
- 추가로 실제 `check_reconstructed.xlsx` 템플릿을 대상으로 CLI 전체 경로(`python3 fill_checklist.py <report> check_reconstructed.xlsx <output>`)를 임시 출력 파일로 실행 확인: 리포트에 있는 7개 항목(1-1,1-2,2-1,2-2,3-1-1,4-1,5-3)은 정확히 채워지고 나머지 28개 항목은 stderr 경고만 남기고 정상 종료. 원본 `check_reconstructed.xlsx`는 읽기만 했으며 git status상 미변경 확인.
- 출력 xlsx의 E열 값 재확인: `1.Cluster구성!E2="정상"`, `E3="확인필요"`, `2.ClusterOperator!E2="✅ 정상"`, `E3="⚠ 주의(Progressing)"` — AC의 상태 매핑 및 2절 승계 규칙과 일치.
- 테스트용 산출물(합성 txt/출력 xlsx)은 `$CLAUDE_JOB_DIR/tmp`에만 남겼고 저장소에는 `fill_checklist.py` 1개만 신규.
