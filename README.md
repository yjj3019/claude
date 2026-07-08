# fable5

"GPT-5(Fable5) Thinking Mode" 프롬프트를 검토·축약해 Claude Code `.claude/skills/`용으로
재구성한 규칙 파일 3종. 전역 CLAUDE.md가 아닌 개별 스킬로 분리해 필요할 때만 명시 호출한다.

> 참고: 모델의 지능·추론 능력은 시스템 프롬프트로 이식되지 않는다. 아래 파일들은
> Fable5의 "지능"이 아니라 **행동 규칙**을 정리한 것이며, 실제 추론 품질은 모델 자체
> (Opus 4.8 / Sonnet 5 등) 선택에 따라 결정된다.

## 파일 구성

| 파일 | 호출 조건 | 요약 |
|---|---|---|
| [`deep-reasoning.md`](./deep-reasoning.md) | 고난도 설계 판단·아키텍처 결정·인시던트 분석·상충 정보 판정 | Fact/Inference/Opinion/Recommendation 라벨링, 근거 부족 시 3분할 명시, 비교 시 판정 기준 우선 정의, hedging 남발 방지 |
| [`tech-validation.md`](./tech-validation.md) | RHEL/OpenShift/Linux 기술 문서 작성·검토, 릴리스노트 분석 | 벤더 문서 우선 근거 서열, 버전·지원상태 필수 명시, 제품 경계(RHEL/OCP/Satellite 등) 혼용 금지, 5축 문서 검증 |
| [`proposal-mode.md`](./proposal-mode.md) | 제안서·제안 슬라이드·경쟁 포지셔닝 문서 작성 | Why/Why now/가치/차별성 체크리스트(조건부), 모호 표현 금지·정량화 우선, score-docs와 역할 분리(서식은 score-docs, 논리는 본 스킬) |

## 설치 위치

프로젝트 공유(git 커밋) 기준:

```
.claude/skills/
├── deep-reasoning.md
├── tech-validation.md
└── proposal-mode.md
```

전역 적용이 필요하면 `~/.claude/skills/`(Windows: `C:\Users\user\.claude\skills\`)에 배치한다.

## CLAUDE.md 연동

본 파일들은 200줄 하네스 예산 보호를 위해 전역 CLAUDE.md에는 포함하지 않는다.
대신 트리거 한 줄만 추가해 참조한다.

```
- 고난도 판단 시 skills/deep-reasoning.md 참조
- RHEL/OCP 기술 진술 검증 시 skills/tech-validation.md 참조
- 제안서 작성 시 skills/proposal-mode.md + score-docs 병행 참조
```

## 원본 대비 변경 사항

- 중복 규칙(불확실성 표현 반복 등) 통합
- 부정 명령(Never X) 다수를 조건부·긍정형으로 완화
- "모든 권고에 trade-off/대안 포함" 규칙을 고위험 판단에 한정 — 응답 미니멀리즘 원칙과 충돌 방지
- 근거 서열·제품 경계 규칙은 기존 release-note 요약 파이프라인과 DRY 유지

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-07-08 | 최초 등록. Notion `Custom Skill` 페이지에도 동일 내용 기록 |
