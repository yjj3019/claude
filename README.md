# TaskForge for Claude

[English](README.en.md) · 한국어

**by yjj3019 · 이전 이름: FEF (Framework for Engineering Excellence)**

TaskForge for Claude는 Claude Code용 작업 실행·검증 프레임워크입니다. 작은 공통 Kernel과 작업별 지침으로 근거가 있고 검토 가능한 기술 산출물을 만드는 데 도움을 줍니다. Anthropic이 제작·후원·보증하는 공식 제품이 아닌 독립 프로젝트입니다.

제품 표시 이름만 변경했습니다. 설치 ID `fef-engineering@fef-marketplace`, 기존 스킬 호출과 저장 데이터는 유지합니다. 새 이름으로 다시 설치할 필요는 없습니다. [이름 변경과 호환성](docs/ClaudeCode.md#product-name-and-retained-identifiers)을 참고하세요.

## 기능과 구성

- `CLAUDE.md`에 공통 Kernel을 담고, `AGENTS.md`는 이 진입점을 안내합니다.
- `modules/`, `domains/`, `reviewers/`, `workflows/`, `policies/`에서 필요한 지침만 선택합니다.
- `config/routes.json`과 `scripts/detect_task.py`는 결정적 라우팅 후보를 제시합니다.
- 네이티브 Skills, 리뷰어 에이전트, 검증 훅을 플러그인으로 제공합니다.
- 마켓플레이스를 통해 설치·업데이트를 관리합니다.

## 시작과 설치 (권장)

Claude Code 터미널에서:

```bash
/plugin marketplace add yjj3019/claude
/plugin install fef-engineering@fef-marketplace
```

설치 후 세션을 재시작하면 Skills, 훅, 리뷰어 에이전트가 사용 가능합니다.

플러그인의 SessionStart 훅이 공통 Kernel을 컨텍스트로 전달합니다. 작업별 팩과 보조 스크립트는 사용자 프로젝트가 아닌 플러그인 설치 경로에서 읽습니다.

훅은 사용자 권한으로 실행됩니다. 설치 전 `hooks/hooks.json`을 확인하세요.

마켓플레이스는 원본에서 생성한 `plugins/fef-engineering/` 배포본을 설치합니다. 원본 `CLAUDE.md`와 기존 `--plugin-dir .`는 유지합니다. 런타임 원본을 수정한 뒤에는 `python scripts/build_plugin.py`로 배포본을 갱신하세요. 생성물 검사와 검증 대상은 [플러그인 배포 안내](docs/ClaudeCode.md#generated-native-distribution)에 정리했습니다.

### 업데이트

버전을 올리고 push하면 마켓플레이스에 반영됩니다.  
사용자는 `/plugin update fef-engineering@fef-marketplace` 또는 플러그인 관리 메뉴에서 업데이트합니다.
과거 네이티브 ID `fef-claude` 사용자만 [기존 ID 이관 안내](docs/ClaudeCode.md#plugin-validation-and-compatibility)를 따릅니다. 현재 네이티브 스킬 호출은 `/fef-engineering:fef-coding` 등이며, 이번 표시 이름 변경으로 호출이 바뀌지는 않습니다. 별도 설치 팩 `fef-claude/`도 유지합니다.
`plugin.json`의 `version`을 바꾸기 전까지는 해당 버전이 고정됩니다.

## 기존 방식 (클론 + 스킬 팩)

Python 3.11 이상과 Git이 필요합니다.

```sh
git clone https://github.com/yjj3019/claude.git
cd claude
python scripts/install_pack.py --auto --dry-run
python scripts/install_pack.py --auto
```

`--auto`는 호스트 skills 루트에 `fef-claude/`를 설치합니다.  
상세 옵션과 형제 설치는 [docs/Installation.md](docs/Installation.md)를 참고하세요.

## 선택 로딩

새 세션은 `CLAUDE.md`를 먼저 읽습니다.  
본격 작업은 [docs/loading-map.md](docs/loading-map.md) 또는 라우팅 후보로 필요한 팩을 선택합니다.

```sh
python scripts/detect_task.py --task "RHEL 장애 RCA를 작성해줘"
```

로드 한도: Module 1 / Domain ≤2 / Workflow 1 / Reviewer 1 / Policies ≤3.

## 검증

플러그인 매니페스트:

```sh
claude plugin validate .
```

저장소 정적 검사:

```sh
python scripts/validate_repository.py
python scripts/validate_routes.py
python -m unittest discover -s tests -p "test_*.py"
```

정적 검사이며 모델 API를 호출하지 않습니다.

## 라이선스

FEF 자체 저작분에는 [MIT 라이선스](LICENSE)를 적용합니다. DelegationLoop 관련 경로,
외부 가이드·인용·보관 기록과 그 생성 복제본은 제외합니다. 저장소와 플러그인 전체가
MIT인 것은 아니며, 제외 자료의 재배포 권한은 미확정입니다.
[제3자 고지](https://github.com/yjj3019/claude/blob/main/skills/ai-delegation-loop/THIRD_PARTY_NOTICES.md)를 확인하세요.

스킬 팩의 새 설치와 명시적 `--force` 갱신에는 `LICENSE`가 포함됩니다. 기존 설치는
자동 수정하지 않으며, 갱신 시 기존 백업·덮어쓰기 정책을 유지합니다.

## 추가 안내

- [Claude Code 사용](docs/ClaudeCode.md)
- [Mods 공식 기능과 3계층 위임 설계](docs/mods-and-tiered-agents.md)
- [설치 상세](docs/Installation.md)
- [스크립트 안내](scripts/README.md)
