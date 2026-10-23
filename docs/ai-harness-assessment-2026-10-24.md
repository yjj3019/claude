# AI-Harness 비교 검토와 제한적 반영

검토일: 2026-10-24. 대상: [yjj3019/AI-Harness](https://github.com/yjj3019/AI-Harness/tree/ac4c59adcced5484c9e9c7952b5794c880838a97), commit ac4c59adcced5484c9e9c7952b5794c880838a97. 기본 브랜치의 shallow clone에서 .git을 제외한14파일을 확인했다. 원본 코드·설치 절차는 실행하지 않았다.

## 판단

문서와 역할 프롬프트 중심의 설계 참고 자료다. 동작하는 다중 에이전트 런타임이나 검증된 성능 개선 패키지로 취급하지 않는다. TaskForge에 이미 있는 최소 변경·선택 로딩·검증·컨텍스트 분리 원칙은 유지하고, 장기 작업의 근거 연결·재개·복구와 발표자료 검증 안내만 기존 소유 문서 안에서 보완했다.

## 주요 발견

| 우선순위 | 근거 | 적용 판단 |
|---|---|---|
| 높음 | [루프 스크립트](https://github.com/yjj3019/AI-Harness/blob/ac4c59adcced5484c9e9c7952b5794c880838a97/.claude/workflows/phase-harness.js#L14-L40)의 runPhase는 로그와 주석뿐이다. 에이전트 호출·판정·재시도·증거 저장·핸드오프 갱신이 없다. | 완료 메시지나 종료 코드만으로 작업 성공을 판정하지 않는다. 스켈레톤을 실행 엔진으로 도입하지 않는다. 소스 분석이며 실제 실행 결과 주장은 아니다. |
| 높음 | [에이전트 정의 예](https://github.com/yjj3019/AI-Harness/blob/ac4c59adcced5484c9e9c7952b5794c880838a97/.claude/agents/coding.md#L1-L11)를 포함한5파일에 YAML frontmatter 구분자가 없다. 루트에 패키지·테스트 설정이나 테스트 결과도 없다. | [Claude Code의 문서화된 subagent 형식](https://code.claude.com/docs/en/sub-agents#write-subagent-files)과 불일치한다. 실제 호스트 인식은 미검증이며 기존 TaskForge 에이전트를 교체하지 않는다. |
| 높음 | 원본14파일에서 LICENSE나 명시적인 재사용·재배포 허가를 찾지 못했다. README는 여러 외부 자료의 종합이라고 설명한다. | 원본 코드·프롬프트·템플릿을 복사하거나 TaskForge MIT 범위에 편입하지 않았다. 일반적인 운영 원칙을 독자적으로 서술하고 출처와 채택 범위를 기록했다. 권리 확정이나 법률 검토 결과는 아니다. |
| 중간 | [핸드오프 절차](https://github.com/yjj3019/AI-Harness/blob/ac4c59adcced5484c9e9c7952b5794c880838a97/docs/HANDOFF.md#L20-L32)는 커밋과 새 세션을 의무화한다. README·설계 문서는 context 약70%와 매 작업 전체 교훈 로그 로딩을 제시한다. | 사용자 승인·호스트 동작·선택 로딩과 충돌하므로 미채택. 기존 진행 기록을 재사용하고 실제 상태와 권한을 확인하도록 보완했다. 70%를 보편적 임계값으로 채택하지 않았다. |
| 중간 | [아키텍처 설명](https://github.com/yjj3019/AI-Harness/blob/ac4c59adcced5484c9e9c7952b5794c880838a97/docs/architecture-spec.md)은 자율 루프와 /phase-harness 실행 예를 제시하지만 대응 command/skill 정의나 호출 구현은 없다. | 사용자 정의 설계와 실제 설치·실행 증거를 구분한다. 명령·자동 세션 재시작·비용 절감·품질 보장 기능을 새로 광고하지 않는다. |

정적 코드 검토를 배제하는 규칙도 가져오지 않았다. 코드 검토, 동적 테스트, 결과물 검사는 서로 다른 근거이며 요구에 맞게 결합해야 한다. 독립 컨텍스트도 오류나 자기 평가 편향의 완전한 제거를 보장하지 않는다.

## 반영한 내용

| 원본에서 검토한 관점 | 기존 TaskForge 소유 문서 | 반영 범위 |
|---|---|---|
| 단계별 완료 기준·재시도 한도 | [Coding](../modules/Coding.md) | 큰 작업만 단계화, 요구·실제 명령/산출물·현재 작업 상태 연결, 수정 후 관련 재검증, 실패 기록 보존, 같은 원인의 반복 중단 |
| 핸드오프 | [Context Protocol](context-protocol.md) | 목표·미완료 변경·결정·검증·승인 경계·다음 작업 보존, 재개 시 실제 checkout 대조, 추가 상태 원장이나 자동 커밋 없음 |
| 독립 평가·blocking/nit 구분 | [Review](../policies/Review.md) | 구현자 요약 외 원본 근거 확인, 실패/차단/미실행 구분, 독립 검토 미실행 공개, 선택적 스타일 제안으로 루프를 늘리지 않음 |
| 교훈 축적 | [Knowledge Governance](knowledge-governance.md) | 확인된 재사용 가치가 있을 때만 프로젝트 기록, 원인과 가설 구분, 소유 문서로 통합, 관련 교훈만 선택 로딩 |
| [PPT 샘플·시각 QA](https://github.com/yjj3019/AI-Harness/blob/ac4c59adcced5484c9e9c7952b5794c880838a97/docs/ppt-harness-workflow.md) | [Presentation](../modules/Presentation.md) | 큰 자료의 대표 샘플, 렌더링과 전체 자료 검사, 필요한 편집 가능 객체 확인, 렌더러 부재 시 미검증 공개 |

이 지침은 사용자 정의 작업 절차다. Anthropic의 공식 내장 자동화나 추가 실행 권한을 뜻하지 않는다. [Anthropic의 장기 에이전트 하네스 연구](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)는 증분 작업과 다음 세션을 위한 명확한 산출물의 유용성을 설명하지만, 이 프로젝트의5단계 흐름이나 고정 에이전트 수를 보장하지 않는다.

## 호환성과 검증 경계

기존 Kernel·CLAUDE.md·AGENTS.md·라우트·스킬 ID·리뷰어 정의·훅·상태v1·검증 래퍼·Git 선택 정책은 변경하지 않았다. 새 의존성·명령·설정·상태 파일·런타임 오케스트레이터를 추가하지 않았다. 네이티브 배포본은 기존 생성기로 소유 문서5개를 동기화한다. 이 비교 보고서는 원본 checkout용이며 런타임 기본 로딩 목록에 넣지 않는다.

선택된 가이드의 길이는 늘었지만 기본 Kernel과 cold-start 로딩 경로는 유지한다. 실제 모델의 입력 토큰·지연·비용 변화나 품질 개선은 이번 정적 문서 반영으로 검증하지 않았다.

기존 Windows 기본 Git 경로의 간헐15초 timeout은 이 문서 변경으로 해결되지 않는다. 이전 연속 전체 검증의1차 통과와2차 실패를 유지하며, 이번 문서·배포본 검증을 안정적인 전체 회귀나 실제 모델 효능 증거로 확대하지 않는다. 원본 AI-Harness의 실제 Claude 인식·자율 실행·PPT 생성도 검증하지 않았다. 새 코드 로직이 없어 문장과 동일한 내용을 반복 검사하는 테스트는 추가하지 않고 기존 라우팅·컨텍스트 예산·배포·설치 회귀로 호환성을 확인한다. 실행 결과는 [작업 이력](../PROGRESS.md)에 기록한다.

## 후속 실제 실행 검증

이후 사용자 요청으로 TaskForge의 전체 Windows 회귀·실제 Claude 합성 코딩/새 세션 재개·PowerPoint 실제 생성물 열기/렌더/OOXML 검사를 수행했다. [후속 검증 보고서](verification-2026-10-24.md)에 성공·실패·한계를 분리했다. 전체 회귀는 Git timeout2건으로 미통과이며, 원본 AI-Harness 스켈레톤의 실행·공식 기능 여부·효능을 검증한 것은 아니다.
