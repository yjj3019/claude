# FEF Claude Framework

[English](README.en.md) · 한국어

Framework for Engineering Excellence(FEF)는 Claude 중심의 엔지니어링 프롬프트 프레임워크입니다. 작은 공통 Kernel과 작업별 지침으로 근거가 있고 검토 가능한 기술 산출물을 만드는 데 도움을 줍니다.

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
/plugin install fef-claude@claude
```

설치 후 세션을 재시작하면 Skills, 훅, 리뷰어 에이전트가 사용 가능합니다.

### 업데이트

버전을 올리고 push하면 마켓플레이스에 반영됩니다.  
사용자는 `/plugin update fef-claude` 또는 플러그인 관리 메뉴에서 업데이트합니다.  
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

## 추가 안내

- [Claude Code 사용](docs/ClaudeCode.md)
- [설치 상세](docs/Installation.md)
- [스크립트 안내](scripts/README.md)
