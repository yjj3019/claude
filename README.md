# TaskForge for Claude

[English](README.en.md) · 한국어

Claude Code에서 **코딩과 장애 분석을 작업별 지침·리뷰·검증으로 연결하는 프레임워크**입니다.
필요한 지침만 선택해 읽고, 변경 근거와 검증 결과를 남기는 작업을 돕습니다.

작성: yjj3019 · 이전 이름: FEF (Framework for Engineering Excellence)

Anthropic이 제작·후원·보증하는 공식 제품이 아닌 독립 프로젝트입니다.

## 빠른 시작

**준비:** Claude Code, Python 3.11 이상, Git.

새로 설치할 때 Claude Code 터미널에서 실행합니다. 기존 사용자는 먼저 [이관 안내(영문)](docs/ClaudeCode.md#plugin-validation-and-compatibility)를 확인하세요.

```text
/plugin marketplace add yjj3019/claude
/plugin install taskforge-for-claude@taskforge-marketplace
```

설치 후 세션을 재시작하면 공통 지침(Kernel), 스킬, 리뷰어 에이전트와 검증 알림 훅을 사용할 수 있습니다.
훅은 사용자 권한으로 실행되므로 설치 전 [실행 설정](https://github.com/yjj3019/claude/blob/main/hooks/hooks.json)을 확인하세요.

## 사용하기

| 작업 | 스킬 호출 |
|---|---|
| 코드 구현·수정 | `/taskforge-for-claude:coding` |
| 장애·오류 원인 분석 | `/taskforge-for-claude:rca` |

작업에 따라 필요한 지침과 리뷰어를 선택하고, 실제 검증 결과와 남은 한계를 확인합니다.
세부 동작은 [Claude Code 사용 안내](docs/ClaudeCode.md), 지침 선택은 [로딩 규약(영문)](docs/loading-map.md)를 참고하세요.

### 업데이트와 기존 설치

```text
/plugin update taskforge-for-claude@taskforge-marketplace
```

`3.0.0`부터 설치 ID와 스킬 호출명을 TaskForge로 통일합니다. 과거 `fef-engineering`·네이티브 `fef-claude` 호출은 새 호출명으로 바꿔야 합니다.
기존 설정·캐시를 삭제하지 말고 [이관 안내(영문)](docs/ClaudeCode.md#plugin-validation-and-compatibility)에 따라 별도 환경에서 확인한 뒤 전환하세요. 검증 상태·환경 변수와 독립 설치 `fef-claude/`는 유지합니다.

## 상세 문서

공통 지침·운영 문서·코드 설명은 영어로 작성합니다. 한국어 README는 자연스러운 한국어로 정리하고, [영문 소개](README.en.md)는 별도로 제공합니다. 명령·설정 키·한국어 테스트 입력은 원문을 유지하며, 위 설치·호출명 변경은 승인된 이관 범위에만 적용합니다. 과거 검증 기록과 제3자 원문은 보존합니다.

| 목적 | 안내 |
|---|---|
| 설치 옵션·클론 기반 스킬 팩 설치 | [설치 가이드](docs/Installation.md) |
| 스킬·훅·리뷰어·이름 변경 호환성 | [Claude Code 사용 안내](docs/ClaudeCode.md) |
| 작업별 지침 선택·라우팅 | [로딩 안내](docs/loading-map.md) |
| 스킬 버전·변경 이력 | [스킬 버전](docs/skill-versions.md) |
| 공식 기능과 사용자 정의 위임 설계 구분 | [Mods와 3계층 에이전트](docs/mods-and-tiered-agents.md) |
| 스크립트·생성 배포본 관리 | [스크립트 안내](scripts/README.md) |

### 저장소 검증

소스를 수정한 경우 저장소 루트에서 실행합니다. 아래 검사는 모델 API를 호출하지 않습니다.

```sh
python scripts/validate_repository.py
python -m unittest discover -s tests -p "test_*.py"
```

## 라이선스와 배포 범위

FEF 자체 저작분에는 [MIT 라이선스](LICENSE)를 적용합니다.
DelegationLoop 관련 자료·외부 가이드·인용·보관 기록 및 해당 생성 복제본은 제외되며, 저장소 전체를 MIT로 해석하지 않습니다.

재배포 권한이 미확정인 위임 스킬은 플러그인 배포본에서 제외하고 신규 설치·ZIP 생성을 차단합니다.
원본과 기존 설치 데이터는 보존하며, 기본 코딩·장애 분석 스킬 호출은 유지합니다.
[제3자 고지](https://github.com/yjj3019/claude/blob/main/skills/ai-delegation-loop/THIRD_PARTY_NOTICES.md)와 [권리 확정 절차](docs/third-party-clearance.md)를 확인하세요.
