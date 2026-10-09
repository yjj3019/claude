# v1.3 검증과 역사 실험 구분

원본 v1.2 모델 실험은 HISTORICAL이며 현재 수정본에는 STALE_FOR_CURRENT_PACKAGE입니다. 기존 수치와 응답을 수정본 프롬프트의 검증으로 재사용하지 않습니다. [원본 보고서](simulation-report.v1.2.ko.md), [모델 결과](simulation-results.json), [네이티브 프로브 결과](native-probe-results.json)는 원본 바이트를 보존합니다.

현재 v1.3은 기존 수정에 산출물 계약 보존, 독립 프롬프트의 자료 불신 경계, 검증 기준 유지와 일반 규칙 재검증을 추가했습니다. [수용 사례](acceptance-cases.md)의 A16~A24는 정적 문서 계약과 격리된 양식·정책 fixture로 확인합니다. 400자 상한을 500자로 바꾸는 사례의 판정은 합성 정책 oracle이며 실제 에이전트 실행이 아닙니다. 채점기 self-check도 실행합니다. [결정적 결과](acceptance-results.json)와 [버전별 hash 및 상태](evidence-status.json)를 구분합니다. 모델 행동이나 실제 prompt injection 방어를 입증한 검사는 아닙니다.

수정본 모델 행동, 전체 인터뷰와 업무 운영은 UNVERIFIED입니다. Codex 보조 프롬프트 읽기도 기존 UNVERIFIED 상태입니다. 이번 수정에는 유료 또는 인증 모델 CLI를 실행하지 않았습니다.
