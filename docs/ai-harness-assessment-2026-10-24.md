# AI-Harness 비교 검토와 제한적 반영

최신 재검토: 아래 [업데이트 재검토](#업데이트-재검토-45664d3) 참조. 최초 검토 내용은 당시 revision에 대한 이력으로 보존한다.

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


## 업데이트 재검토 45664d3

2026-10-24 사용자 재요청으로 `ac4c59adcced5484c9e9c7952b5794c880838a97`부터
[45664d315faa13aab71f3b01bf270d50a42f4906](https://github.com/yjj3019/AI-Harness/tree/45664d315faa13aab71f3b01bf270d50a42f4906)까지 비교했다.
18커밋·변경32경로이며 최신 고정 snapshot은 일반 파일33개다. 별도 참조 저장소와
읽기 전용 소스 사본을 사용했고 upstream 코드·테스트·설치기는 실행하지 않았다.

### 이전 발견의 변경 상태

- 에이전트5개에 YAML frontmatter 구분자가 추가됐다. 이전 형식 누락 지적은 최신 snapshot에는 해당하지 않는다. 실제 Claude 호스트 인식은 이번에 검증하지 않았다.
- 로그 전용 스켈레톤 대신 `phase-gate.js`, `/phase-harness` command, 증거/읽기/파괴적 명령 가드, doctor, 코드 트리·명령 바인딩, attestation 재실행, 테스트와 CI가 추가됐다. gate는 증거 기록/검사를 담당하고 subagent 호출·재시도는 command 지침에 맡긴다. 완전한 자율 실행 보장으로 확대하지 않는다.
- [Apache-2.0 LICENSE](https://github.com/yjj3019/AI-Harness/blob/45664d315faa13aab71f3b01bf270d50a42f4906/LICENSE)가 추가됐다. 이전의 LICENSE 부재는 최초 revision 한정 관찰이다. 파일 존재만으로 모든 외부 참고 자료의 권리·출처가 검증되거나 별도 보존 DelegationLoop 자료가 허가됐다고 간주하지 않는다. 이번에도 원본 코드·프롬프트는 가져오지 않았다.

### 최신 구현에서 확인한 경계

아래는 고정 소스의 분기와 fixture를 읽은 정적 분석이며 실제 호스트·공격 재현 결과가 아니다.

| 우선순위 | 확인한 구현·조건 | TaskForge 적용 판단 |
|---|---|---|
| 높음 | [`run`과 체인 검사](https://github.com/yjj3019/AI-Harness/blob/45664d315faa13aab71f3b01bf270d50a42f4906/.claude/workflows/phase-gate.js#L281-L359)는 실행 명령의 exit0을 PASS로 기록한다. 의도한 테스트인지, 테스트0건/전부skip인지는 판별하지 않는다. | 성공한 준비 명령·아무 일도 하지 않는 명령을 기능 검증으로 오인하지 않도록 실제 명령·최종 요약·가능한 실행/실패/skip 수를 기존 Coding 모듈과 스킬에서 확인한다. |
| 높음 | [CI](https://github.com/yjj3019/AI-Harness/blob/45664d315faa13aab71f3b01bf270d50a42f4906/.github/workflows/ci.yml#L21-L29)는 존재하는 attestation만 순회한다. 최신 tree에는 required-test-command.json이 없고, [명령 고정](https://github.com/yjj3019/AI-Harness/blob/45664d315faa13aab71f3b01bf270d50a42f4906/.claude/workflows/phase-gate.js#L472-L519)은 선택 사항이다. attestation은 tree 해시 대상에서 제외되므로 핀이 없는 경우 다른 exit0 argv로 바꿔도 명령 불일치를 거부하지 않는다. | 로컬 attestation을 CI 보장으로 광고하지 않는다. 기존 Review 정책/리뷰어에서 실제 필수 작업·검증 명령과 결과를 확인하도록 보완한다. 현재 TaskForge CI를 이 방식으로 교체하지 않는다. |
| 중간 | [읽기 검사](https://github.com/yjj3019/AI-Harness/blob/45664d315faa13aab71f3b01bf270d50a42f4906/.claude/workflows/phase-gate.js#L227-L260)는 설정 문자열로 활성 여부를 판별하고 경로+해시 기록을 찾는다. 읽은 범위·이해·검증 적합성·기록자 권한은 증명하지 않는다. | read receipt와 해시를 내용 검토나 독립 검증의 대체물로 쓰지 않도록 기존 Review 정책에 명시한다. |
| 중간 | [가드](https://github.com/yjj3019/AI-Harness/blob/45664d315faa13aab71f3b01bf270d50a42f4906/.claude/hooks/evidence-guard.sh#L1-L56)는 jq/입력 파싱 실패 시 통과하며 명령 문자열 패턴에 의존한다. main session은 제한하지 않는다. [read-tracker](https://github.com/yjj3019/AI-Harness/blob/45664d315faa13aab71f3b01bf270d50a42f4906/.claude/hooks/read-tracker.sh)는 Bash 도구·GNU 경로/해시 도구와 host event 필드를 전제한다. | 보안 경계·OS 격리로 취급하지 않고 기존 Windows/Python 훅을 유지한다. doctor의 진단 아이디어는 유용하지만 새 Node/Bash/jq 의존성은 추가하지 않는다. |
| 중간 | [treeHash](https://github.com/yjj3019/AI-Harness/blob/45664d315faa13aab71f3b01bf270d50a42f4906/.claude/workflows/phase-gate.js#L84-L108)는 tracked+nonignored 파일 범위다. ignored 의존성/런타임 환경은 별도이며 check는 Git 부재 시 경고로 진행할 수 있다. | 해시가 포괄하는 입력/환경 한계를 공개한다. 기존 TaskForge snapshot/state v1이나 Git 실패 처리를 변경하지 않는다. |

### 선별 반영과 보류

- 기존 Coding 모듈과 native coding 스킬: 의도한 동작을 실행한 명령인지와 최종 결과를 확인한다. 제공되는 테스트/실패/skip 수를 공개하며 zero/all-skipped는 요구 충족으로 취급하지 않는다. 원시 로그는 요약과 별도로 보존하되 비밀정보를 노출하지 않는다.
- 기존 Review 정책과 CodeChangeReviewer: 원본 로그·최종 요약, 실제 CI 필수 작업/명령을 확인하고 해시·읽기 기록의 보장 범위를 구분한다. 문장은 독자적으로 작성했다.
- 기존 long-running/handoff/lesson/PPT 지침과 겹치는 내용은 중복 반영하지 않았다. 강제 전체 교훈 로딩·상시 phase 파일·고정70% 컨텍스트 임계값·무조건 TDD/세션 전환·외부 MCP 자동 설치도 도입하지 않았다.
- 증거 해시 체인·attestation·doctor와 새 guard runtime은 보류했다. 현재 TaskForge 검증 래퍼/훅과 중복되고 명령 의미·신뢰 경계·Windows 의존성까지 설계해야 한다. 필요가 확인되면 별도 영향 검토 후 다룬다.

Coding `1.0.3`/plugin `2.0.4`로 호환 패치 갱신하고 기존 생성기로 배포본을 동기화한다.
RCA/standalone entry 버전, 기술ID·라우트·권한·Kernel·state v1·검증 래퍼 동작은 유지한다.
새 런타임 로직이 없어 문장을 그대로 재검사하는 테스트는 추가하지 않는다.
실제 관련 검증·실패와 제한은 [작업 이력](../PROGRESS.md)의 해당 업데이트 항목에 기록한다.
이번 지침 보강은 테스트 수 자동 강제·실제 모델 효능·비용 절감·운영 안정성을 보장하지 않는다.
