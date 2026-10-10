# FEF Claude Framework

[English](README.en.md) · 한국어

Framework for Engineering Excellence(FEF)는 Claude 중심의 엔지니어링 프롬프트 프레임워크입니다. 작은 공통 Kernel과 작업별 지침으로 근거가 있고 검토 가능한 기술 산출물을 만드는 데 도움을 줍니다. 반복 업무를 위한 AI Delegation Loop v1.3도 독립 스킬로 제공합니다.

## 기능과 구성

- `CLAUDE.md`에 공통 Kernel을 담고, `AGENTS.md`는 이 진입점을 안내합니다.
- `modules/`, `domains/`, `reviewers/`, `workflows/`, `policies/`에서 필요한 지침만 선택합니다. Coding·Research 절차는 해당 모듈에 통합되어 있습니다.
- `config/routes.json`과 `scripts/detect_task.py`는 결정적 라우팅 후보를 제시하며 모델 판단을 대체하지 않습니다.
- 구조·라우팅·골든 테스트와 설치 무결성을 검사합니다. Claude Code의 로컬 훅은 세션과 실제 파일 상태에 맞는 검증을 상기시킵니다.
- `skills/ai-delegation-loop/`는 반복 업무 인터뷰, 산출물 계약, 재사용 도구와 증거 검증을 위한 별도 패키지입니다.

FEF의 `workflows/`는 Markdown 작업 지침입니다. 실행 가능한 Claude Code `.claude/workflows/`와는 별개이며, 이 저장소는 동적 워크플로를 배포하지 않습니다.

## 시작과 설치

Python 3.11 이상과 Git이 필요합니다. 스크립트는 Python 표준 라이브러리만 사용합니다. 아래 명령은 클론 루트에서 실행하며, 환경에 따라 `python` 대신 `python3`를 사용하세요.

```sh
git clone https://github.com/yjj3019/claude.git
cd claude
python scripts/install_pack.py --auto --dry-run
python scripts/install_pack.py --auto
```

`--auto`는 현재 사용자 HOME의 Claude·Codex·Grok·Cursor·AGENTS 호스트 표시를 찾아 skills 루트에 `fef-claude/`를 설치합니다. 호스트가 없으면 `~/.agents/skills`를 사용합니다. 기본값은 호스트 skills 설치만 하며 형제 프로젝트 폴더를 탐색하거나 설치하지 않습니다.

Claude Code에서는 이 클론을 워크스페이스로 열어 루트 `CLAUDE.md`를 읽도록 합니다. 다른 프로젝트의 호스트 skill 복사본은 그 프로젝트의 `CLAUDE.md`를 대체하지 않습니다. Claude Projects에서는 `CLAUDE.md`를 Project Instructions에 붙이고 필요한 팩만 Project Knowledge에 첨부합니다. Code의 명령·훅·네이티브 에이전트는 Projects에서 실행되지 않습니다.

### 설치 대상과 기존 파일

```sh
python scripts/install_pack.py --dest /path/to/skills --dry-run
python scripts/install_pack.py --dest /path/to/skills
python scripts/install_pack.py --check --dest /path/to/skills
python scripts/install_pack.py --siblings /other/project --dry-run
python scripts/install_pack.py --siblings /other/project
```

`--dest`는 skills 루트입니다. FEF는 그 아래 `fef-claude/`에 설치됩니다. 형제 설치는 `--siblings`, `FEF_SIBLING_ROOTS`, `--siblings-only` 또는 `--scan-sibling-parent`로 명시적으로 선택합니다. 부모 폴더 탐색은 기본으로 꺼져 있습니다. `FEF_SIBLING_ROOTS`의 경로 구분자는 운영체제의 `os.pathsep`을 따릅니다.

기존 FEF 팩은 배포 파일 지문과 설치 무결성이 같으면 건너뛰고, 다르면 덮어쓰기를 거부합니다. `--force`는 기존 팩을 교체하며 FEF의 로컬 수정·추가 파일을 보존하지 않으므로 먼저 별도로 백업하세요. `--dry-run`은 파일을 쓰지 않습니다. 기본 설치는 실행 문서만 포함하고, `--with-tests`로 tests·examples를 추가할 수 있습니다.

`--print-bootstrap`은 설치 명령, `--print-claude`는 Projects 설정 절차를 출력합니다. 전체 옵션은 `python scripts/install_pack.py --help`와 [설치 안내](docs/Installation.md)를 확인하세요.

## 선택 로딩과 안전 기준

새 세션은 `CLAUDE.md`를 먼저 읽습니다. 단순·저위험 작업의 기본 로딩은 인라인 Kernel뿐입니다. 본격 작업은 [로딩 맵](docs/loading-map.md) 또는 라우팅 후보로 필요한 팩을 선택합니다.

```sh
python scripts/detect_task.py --task "RHEL 장애 RCA를 작성해줘"
python scripts/measure_load.py
```

로드 한도는 Module 1 / Domain ≤2 / Workflow 1 / Reviewer 1 / Policies ≤3입니다. 작업에 필요한 Evidence·FileHandling·Freshness·ToolExecution 무결성 정책은 유지합니다. README·전체 저장소·이력 보고서·모델 안내를 상시 미리 로드하지 않습니다. Projects에도 전체 저장소를 첨부하지 않습니다.

모델과 관계없이 근거·검증·승인·불확실성 표기(`[unverified]`)와 같은 예산을 유지합니다. [Adaptive Effort](docs/adaptive-effort.md)의 모델 표는 날짜가 있는 참고 선호이며 자동 모델 전환이나 현재 가용성을 보장하지 않습니다. 보통은 현재 호스트 모델을 유지하고, 능력 부족이 확인될 때 지원되는 노력 수준과 모델을 검토합니다. 필요한 자료가 없으면 그 자료를 확보해야 합니다.

`measure_load.py`는 파일 바이트·추정 토큰을 측정하며 실제 비용·응답 시간·모델 품질을 증명하지 않습니다. 훅은 검증 알림이며 샌드박스나 완전한 테스트 증거가 아닙니다. 실제 환경의 Python·셸·훅 연결을 확인하세요.

## AI Delegation Loop: 별도 선택 설치

[독립 스킬](https://github.com/yjj3019/claude/blob/main/skills/ai-delegation-loop/README.md)은 반복 업무의 독자·목적·형식·길이·필수/제외 범위·저장 경로를 계약으로 보존합니다. 참조 자료를 실행 지시나 승인으로 취급하지 않고, PASS를 위해 검증 기준을 완화하거나 시험 답을 하드코딩하지 않습니다. 재실행 전 증거 확인과 각 재실행의 외부 효과에 필요한 승인도 유지합니다.

아래는 클론에서 실행합니다. `--dest`는 `fef-claude/` 폴더가 아닌 두 패키지의 공통 skills 루트입니다. delegation은 명시적인 `--dest`가 필요하며 자동 호스트·형제 탐색을 사용하지 않습니다.

```sh
python scripts/install_pack.py --pack ai-delegation-loop --dest /path/to/skills --dry-run
python scripts/install_pack.py --pack ai-delegation-loop --dest /path/to/skills
python scripts/install_pack.py --pack ai-delegation-loop --dest /path/to/skills --check
python scripts/delegation/install.py package --output /path/to/ai-delegation-loop.zip
```

같은 루트 아래 `fef-claude/`와 `ai-delegation-loop/`가 형제 패키지로 설치됩니다. FEF의 기본 설치와 Kernel은 바뀌지 않습니다. delegation도 다른 기존 설치를 거부하지만, 명시적 `--force` 교체 시에는 skills 검색 경로 밖에 백업을 남깁니다.

기본 delegation 설치·ZIP은 실행 자료와 수용 기준을 포함합니다. `--with-evidence`를 설치 또는 package 명령에 추가하면 보존된 시험 실행기·보고서·JSON도 포함합니다. 전체 canonical 패키지와 원본 Git 이력은 저장소에 계속 남습니다. `--with-evidence`는 FEF 선택에는 사용할 수 없습니다.

플랫폼별 경로는 [delegation 설치 안내](https://github.com/yjj3019/claude/blob/main/skills/ai-delegation-loop/installation.ko.md), 변경과 측정 범위는 [최적화 기록](https://github.com/yjj3019/claude/blob/main/docs/delegation-loop/OPTIMIZATION.md)을 확인하세요.

## 검증과 한계

클론 루트에서 실행합니다. 아래 검사는 모델·유료 API를 호출하지 않습니다.

```sh
python scripts/validate_repository.py
python scripts/validate_routes.py
python scripts/run_golden_tests.py --validate-only
python scripts/sync_kernel.py --check
python -m unittest discover -s tests -p "test_*.py"
python scripts/delegation/validate_skill.py
python -m unittest discover -s scripts/delegation -p "test_*.py"
python scripts/delegation/refresh_evidence.py --check
python scripts/delegation/verify_history.py
python skills/ai-delegation-loop/tests/run_simulation.py --output ./sim --self-check
```

CI는 FEF를 Ubuntu/Python 3.11·3.12·3.14에서, FEF installer를 Windows/Python 3.11·3.14에서, delegation을 Ubuntu·Windows/Python 3.11·3.14에서 검사합니다. delegation CI는 원본 이력 복원과 플랫폼별 ZIP 체크섬 일치도 확인합니다. 로컬 운영체제의 symlink 권한 등으로 일부 검사가 건너뛰어질 수 있으므로 실행 결과를 확인하세요.

v1.2의 원본 모델 결과는 HISTORICAL이며 현재 v1.3에는 STALE입니다. 현재 문서 계약·격리 fixture·채점기 self-check는 별도 hash로 기록합니다. 현재 모델 동작, prompt injection 방어, Codex 보조 프롬프트 읽기는 UNVERIFIED입니다. 정적 검사를 실제 전 플랫폼 업무 검증이나 모델 품질 향상으로 해석하지 않습니다.

원본 DelegationLoop에는 LICENSE가 없고 대상 LICENSE도 불완전한 MIT placeholder입니다. 통합이 새 MIT 권한을 부여하지 않으며 원본 라이선스·재배포 권한은 미해결입니다. 원문 출처·저자·Git 이력·PR 논의 보존과 원본 삭제 전 조건은 [통합 기록](https://github.com/yjj3019/claude/blob/main/docs/delegation-loop/INTEGRATION.md)에 있습니다.

## 추가 안내

- [Claude Code 사용·에이전트 선택·훅 제한](https://github.com/yjj3019/claude/blob/main/docs/ClaudeCode.md)
- [Claude Projects 설정](https://github.com/yjj3019/claude/blob/main/docs/ClaudeProjects.md)
- [스크립트 안내](scripts/README.md)
- [FEF 최적화 근거와 한계](https://github.com/yjj3019/claude/blob/main/docs/precise-analysis-2026-10-09.md)

- [합성 사용 예시와 검증 기준](https://github.com/yjj3019/claude/blob/main/docs/Examples.md)
