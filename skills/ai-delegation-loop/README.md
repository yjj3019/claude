# AI Delegation Loop

반복 업무 하나를 인터뷰로 매뉴얼화하고, 재사용 도구와 증거 기반 검증을 쌓는 Agent Skill 모음입니다. v1.3은 [실행 절차](SKILL.md)에 산출물 계약을 보존하고, 독립 프롬프트의 자료 불신 경계와 검증 기준 유지·다른 입력 재검증을 보완했습니다. 기본 설치는 실행 자료만 포함하며 원본 이력과 실험은 저장소에 보존합니다. 재실행 전 검증 저장과 사람 확인, 실행별 승인, 복수·외부 원인 분류는 유지합니다.

## 빠른 시작

1. [적용 조건](manual.ko.md#1-어떤-일을-고를까)을 확인해 반복 업무 하나를 고릅니다.
2. [Grok·ChatGPT(Codex)·Claude 설치 안내](installation.ko.md)를 따라 폴더 전체를 설치합니다. 로컬 설치는 `python scripts/delegation/install.py install --target claude codex grok --scope user` 중 필요한 도구만 골라 실행합니다(`--dry-run`으로 계획 확인). 로컬 경로 설치와 웹 스킬 업로드는 별도입니다.
3. 네이티브 스킬 메뉴가 없는 채팅 환경에서는 실제 마스터 폴더를 따로 두고 읽기용 사본을 제공합니다. 사본을 사용하는 경우 마스터 저장 후 업로드본을 교체합니다.
4. [프롬프트 1](prompts/01-interview.md)로 인터뷰하고, 프롬프트 2로 통과한 도구를 저장하고, 프롬프트 3으로 검증을 만들고, 실패할 때 프롬프트 4로 매뉴얼을 고칩니다.
5. [완료 기준과 검증 단계](manual.ko.md#5-증거로-완료를-판정한다)를 정하고, 같은 업무를 두 번째로 실행해 저장된 도구가 실제로 쓰였는지 확인합니다.

## 구성

- `SKILL.md`: 에이전트가 읽는 간결한 절차와 안전 경계
- `manual.ko.md`: 후보 선정부터 운영·유지보수까지의 실전 설명
- `installation.ko.md`: 세 플랫폼의 로컬·웹 설치와 권한별 대체 절차
- `prompts/`: 인터뷰, 툴박스, 검증, 실패 수정 프롬프트 네 개
- `templates/`: 업무별 매뉴얼과 인덱스·수정 기록 양식
- `tests/acceptance-cases.md`: 실행 중 참고하는 수용 기준. 나머지 tests의 실험·실행기는 저장소에 보존하며 기본 설치·ZIP에서는 제외한다(`--with-evidence`로 포함 가능).
- `agents/openai.yaml`: Codex·ChatGPT 앱에 보이는 이름·설명·기본 프롬프트(선택 파일)
- 대상 저장소의 `scripts/delegation/`: 설치·ZIP 패키징(`install.py`), 패키지 검증(`validate_skill.py`)과 단위 테스트
- 대상 저장소 루트의 `AGENTS.md`·`CLAUDE.md`: FEF의 기존 지침과 선택 로딩 규칙을 유지한다. 위임 패키지를 전부 자동 로딩하지 않는다.

통과가 확인된 실제 산출물이 제공되지 않았으므로 `examples/`에는 예시 결과물을 넣지 않았습니다. 예시는 개인정보와 비밀정보를 제거하고 담당자가 승인한 완성본만 추가합니다.

## 검증

Agent Skills의 공식 `SKILL.md` frontmatter 형식에 맞췄습니다. 대상 저장소 루트에서 `python scripts/delegation/validate_skill.py`는 형식·링크·JSON·hash·버전·민감정보를 검사하고, `python -m unittest discover -s scripts/delegation -p "test_*.py"`가 검증기와 설치 스크립트를 시험합니다. 공식 [skills-ref validator](https://github.com/agentskills/agentskills/tree/main/skills-ref)도 사용할 수 있습니다. 전체 모델 시뮬레이션은 별도 승인과 모델 접근이 필요한 저장소 개발 작업입니다. 기본 스킬 실행에 필요하지 않습니다. 조건·결과·제한은 [시뮬레이션 보고서](https://github.com/yjj3019/claude/blob/main/skills/ai-delegation-loop/tests/simulation-report.ko.md)에 보존합니다.

v1.2 모델 결과는 HISTORICAL이며 v1.3에는 STALE_FOR_CURRENT_PACKAGE입니다. 현재 버전은 `python scripts/delegation/refresh_evidence.py --check`로 문서 계약·격리된 양식·채점기 self-check와 별도 hash 기록을 확인합니다. 이 명령은 모델 CLI를 실행하지 않습니다. 수정본의 모델 행동과 Codex 보조 프롬프트 읽기는 UNVERIFIED입니다. 새 변경 뒤에는 `refresh_evidence.py`로 결정적 검사를 실행하고 현재 기록만 갱신합니다. 원본 모델 결과는 덮어쓰지 않습니다.

## 출처와 범위

- 절차의 기반: [AI 위임 루프: 에이전트 대신 매뉴얼으로 일 넘기기](https://sdk-kim-builds.com/guides/ai-delegation-loop-playbook/) (낭만빌더 김스듴, 2026-09-18)
- 파일 형식: [Agent Skills specification](https://agentskills.io/specification)

원문의 업무 예시는 출발점으로만 제시합니다. 합성 시뮬레이션의 지침 준수율과 실제 조직의 시간 절감·운영 성과를 구분합니다. 승인·보안·Git 지침과 검증 수준은 재사용 시의 안전 경계를 명확히 하도록 덧붙였습니다.

## 통합 출처와 라이선스

이 패키지는 yjj3019/DelegationLoop의 main 및 optimize/three-platforms 이력에서 가져왔다. 원본 저자·커밋·원문 출처는 대상 저장소의 `docs/delegation-loop/source-history/`에 보존했다. 원본에 LICENSE가 없었고 대상 LICENSE도 불완전한 MIT placeholder다. 라이선스는 미확정이며, 이 통합은 MIT 부여나 저작권 소유자 지정이 아니다. 재배포 권한을 별도로 확인한다.
