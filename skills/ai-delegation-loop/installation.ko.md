# Grok · ChatGPT(Codex) · Claude 설치

2026-10-09 공식 문서 기준. 같은 `ai-delegation-loop` 폴더를 사용한다. `SKILL.md`만 복사하면 프롬프트와 양식 링크가 깨지므로 폴더 전체를 복사한다. 설치는 파일 접근이나 외부 행동 권한을 추가하지 않는다.

## 1. 공통 준비

저장소를 내려받고 압축을 풀거나 다음처럼 복제한다.

```sh
git clone https://github.com/yjj3019/claude.git
cd claude
```

원본은 `skills/ai-delegation-loop/`다. 서로 다른 버전을 여러 검색 경로에 설치하지 않는다. 같은 이름이 이미 설치돼 있으면 내용을 비교하고 백업한 후 갱신한다.

### 설치 스크립트 (권장)

`scripts/delegation/install.py`는 표준 라이브러리만 쓰는 Python 스크립트(3.9 이상 문법)다. 명령줄에 지정한 도구와 범위의 경로에만 쓰며, 부모 폴더를 훑거나 다른 저장소를 건드리지 않는다. 설치본이 원본과 같으면 아무것도 쓰지 않고, 다르면 `--force` 없이는 중단한다. `--force`는 기존 폴더를 지우지 않고 해당 도구 폴더의 `.backups/`로 옮긴다. 이 폴더는 스킬 검색 경로 밖이라 중복 스킬로 잡히지 않는다.

```sh
# 사용자 전체 설치. 먼저 --dry-run을 붙여 계획만 볼 수 있다.
python scripts/delegation/install.py install --target claude codex --scope user
# 특정 업무 프로젝트에만 설치
python scripts/delegation/install.py install --target codex --scope project --project-dir /path/to/work-project
```

스크립트를 쓸 수 없을 때만 아래 수동 복사를 **첫 설치**에 쓴다.

## 2. 로컬 에이전트: Grok Build, Codex, Claude Code

| 도구 | 프로젝트별 설치 위치 | 사용자 전체 설치 위치 | 명시 호출 |
| --- | --- | --- | --- |
| Grok Build | `.grok/skills/ai-delegation-loop/` | `~/.grok/skills/ai-delegation-loop/` | `/ai-delegation-loop` |
| Codex CLI·앱 | `.agents/skills/ai-delegation-loop/` | `~/.agents/skills/ai-delegation-loop/` | `/skills`로 고르거나 `$ai-delegation-loop` 입력 |
| Claude Code | `.claude/skills/ai-delegation-loop/` | `~/.claude/skills/ai-delegation-loop/` | `/ai-delegation-loop` |

프로젝트별 경로는 **실제 업무 프로젝트** 기준이다. 사용자 전체 경로는 홈 폴더 기준이다. 세 도구 모두 프로젝트별 경로를 현재 폴더에서 저장소 루트까지 올라가며 찾는다.

검색 경로가 겹치는 점에 주의한다. Codex는 같은 이름의 스킬을 합치지 않아 선택기에 둘 다 보이므로 사용자 전체와 프로젝트별 중 한 범위에만 설치한다. Grok은 `~/.grok/skills` 외에 `~/.agents/skills`(Codex 사용자 경로)와 Claude Code 스킬도 읽는다고 문서에 적혀 있다. Claude 쪽 정확한 경로는 명시되지 않았다. 같은 이름이 여러 경로에 있을 때의 우선순위와 중복 처리도 문서에 없다. 그래서 Codex나 Claude Code를 사용자 범위에 이미 설치했다면 Grok 사본을 먼저 추가하지 않는다. Grok의 `/` 입력에서 `ai-delegation-loop`이 보이는지 확인하고, 보이지 않을 때만 `~/.grok/skills`에 추가한다. 이 동작은 이 저장소에서 직접 시험하지 않았다.

### Windows PowerShell

저장소 루트에서 도구별 해당 명령만 실행한다.

```powershell
# Grok Build
New-Item -ItemType Directory -Force "$HOME/.grok/skills" | Out-Null
Copy-Item -Recurse -LiteralPath './skills/ai-delegation-loop' -Destination "$HOME/.grok/skills/ai-delegation-loop"

# Codex
New-Item -ItemType Directory -Force "$HOME/.agents/skills" | Out-Null
Copy-Item -Recurse -LiteralPath './skills/ai-delegation-loop' -Destination "$HOME/.agents/skills/ai-delegation-loop"

# Claude Code
New-Item -ItemType Directory -Force "$HOME/.claude/skills" | Out-Null
Copy-Item -Recurse -LiteralPath './skills/ai-delegation-loop' -Destination "$HOME/.claude/skills/ai-delegation-loop"
```

### macOS · Linux

```sh
# 해당 도구 하나만 선택한다.
mkdir -p ~/.grok/skills
cp -R skills/ai-delegation-loop ~/.grok/skills/ai-delegation-loop

mkdir -p ~/.agents/skills
cp -R skills/ai-delegation-loop ~/.agents/skills/ai-delegation-loop

mkdir -p ~/.claude/skills
cp -R skills/ai-delegation-loop ~/.claude/skills/ai-delegation-loop
```

설치 후 새 세션을 열고 명시 호출한다. Grok과 Claude Code는 `/`를 입력해 이름이 보이는지, Codex는 `/skills` 또는 `$` 입력으로 확인한다. 첫 요청: “매주 고객 업데이트를 작성하는 업무를 AI 위임 루프로 매뉴얼화해줘. 인터뷰부터 시작해줘.” 질문 하나가 오고 파일을 바로 생성하지 않는지 확인한다.

스킬 본문이 불러와져도 보조 프롬프트 읽기가 차단될 수 있다. 이때 필요한 파일의 읽기만 승인 요청하고, 실제 읽기 성공까지 `UNVERIFIED`로 남긴다. Codex의 승인 심사는 수동 또는 지원되는 계정의 자동 심사를 사용할 수 있으며, 자동 심사도 읽기 전용 샌드박스와 보호 경로를 없애지 않는다. ACL 변경이나 Full Access를 설치 해결책으로 쓰지 않는다. [Codex 승인 심사 설명](https://learn.chatgpt.com/docs/sandboxing/auto-review)

근거: [Grok Build](https://docs.x.ai/build/features/skills-plugins-marketplaces), [Codex 설치 경로](https://developers.openai.com/codex/skills), [Claude Code](https://code.claude.com/docs/en/skills).

## 3. 웹·앱 네이티브 스킬

### ChatGPT

공식 지원 대상은 적격 Business·Enterprise·Healthcare·Edu 계정이며, 조직 설정과 제품 제공 상태에 따라 다르다. 개인 계정이나 메뉴가 없는 계정에서 지원된다고 가정하지 않는다.

1. 사이드바 **Plugins → Skills → Create → Upload from your computer**를 연다.
2. 아래 방식으로 만든 스킬 패키지를 선택하고 업로드 검사를 마친다. 업로더가 요구하는 형식을 확인한다. 공식 도움말은 업로드 동작을 설명하지만 모든 화면의 허용 확장자를 보장하지 않는다.
3. 설치된 스킬에서 이름·설명을 확인하고 새 채팅에서 위 첫 요청을 실행한다. 실제로 스킬을 불러왔는지 확인한다.

로컬 Codex 설치와 ChatGPT 설치는 별도다. 자동 동기화를 가정하지 않는다. 근거: [Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt).

### Claude 웹·데스크톱·Cowork

Code execution and file creation을 켠 뒤 **Customize → Skills → + → Create skill → Upload a skill**에서 스킬 ZIP을 업로드하고 활성화한다. 조직 정책에 따라 생성·업로드가 제한될 수 있다. 로컬 `~/.claude/skills` 복사만으로 웹·Cowork에 설치되지는 않는다.

업로드하는 `SKILL.md`의 frontmatter에는 `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` 외의 키를 넣지 않는다. 다른 키가 있으면 업로드가 오류로 끝난다고 Claude Code 문서에 적혀 있다. 이 저장소의 `SKILL.md`는 이 조건을 지키며 `scripts/delegation/validate_skill.py`가 매번 확인한다.

ZIP의 최상위에는 `ai-delegation-loop` 폴더가 있고 그 안에 `SKILL.md`, 매뉴얼, 프롬프트와 양식이 있어야 한다. 저장소 전체 ZIP을 그대로 업로드하지 않는다. 근거: [Claude 스킬 사용](https://support.claude.com/en/articles/12512180-use-skills-in-claude), [패키지 구조](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).

### Grok 웹·iOS·Android

Grok은 대화·파일 업로드로 커스텀 스킬을 만들 수 있다. `SKILL.md`와 필요한 지원 파일을 제공하고 “이 지침과 첨부 자료를 ai-delegation-loop 스킬로 저장해줘”라고 요청한다. 이름과 저장 결과를 확인한 뒤 새 대화에서 위 첫 요청으로 확인한다. 공개 안내가 이 저장소 ZIP의 자동 설치나 로컬 경로 동기화를 보장하지 않으므로, 업로드 성공과 스킬 저장 성공을 구분한다. 근거: [Grok Skills 공식 발표](https://x.ai/news/grok-skills).

### ZIP 만들기

권장: `python scripts/delegation/install.py package`는 `dist/ai-delegation-loop.zip`을 만든다. 최상위가 `ai-delegation-loop/` 폴더이고 `__pycache__`와 `.pyc`를 제외한다. 운영체제 메타데이터와 시각을 고정하고 무압축으로 저장하여 압축 라이브러리 버전에 따른 바이트 차이를 없앤다. 같은 파일 입력이면 같은 바이트가 나온다. 기존 ZIP이 있으면 `--force` 없이는 쓰지 않는다. 스크립트를 쓸 수 없을 때만 아래 명령을 쓴다.

저장소 루트에서:

```powershell
Compress-Archive -LiteralPath './skills/ai-delegation-loop' -DestinationPath './ai-delegation-loop.zip'
```

```sh
cd skills
zip -r ../ai-delegation-loop.zip ai-delegation-loop
```

출력 ZIP이 이미 있다면 비교·백업 후 갱신한다. 업로더별 지원 형식과 검사 결과는 해당 화면에서 확인한다.

## 4. 네이티브 메뉴가 없는 채팅 환경

로컬 또는 승인된 드라이브에 업무별 마스터 폴더를 하나 둔다. `SKILL.md`와 필요한 매뉴얼·프롬프트를 대화 또는 Project에 첨부하고 “첨부한 AI 위임 루프 지침을 따라 인터뷰부터 시작해줘”라고 요청한다. 이것은 지침 제공 방식이며 네이티브 설치·자동 호출 검증이 아니다.

실제 쓰기 도구가 없으면 AI가 출력한 파일을 사람이 마스터에 저장한다. 업로드본이 사본인 환경에서는 옛 사본을 확인 후 교체한다. 연결된 자료의 실시간 동기화 여부는 연결 방식별로 확인한다. 스킬 저장·실제 파일 쓰기·Project 사본 교체를 각각 확인하고, 완료 증거가 없으면 `UNVERIFIED`로 남긴다.

## 5. 업무 폴더 위치

인터뷰로 만든 `[job-name]/` 폴더도 스킬이다. 아래 위치에 두면 다음 실행부터 따로 첨부하지 않아도 도구가 불러온다. 같은 업무를 여러 도구에서 쓴다면 마스터를 하나만 정하고, 나머지는 갱신할 때 교체한다.

| 도구 | 프로젝트별 | 사용자 전체 |
| --- | --- | --- |
| Grok Build | `.grok/skills/<job-name>/` | `~/.grok/skills/<job-name>/` |
| Codex | `.agents/skills/<job-name>/` | `~/.agents/skills/<job-name>/` |
| Claude Code | `.claude/skills/<job-name>/` | `~/.claude/skills/<job-name>/` |

- 폴더 이름과 `SKILL.md`의 `name`을 같게 하고, 소문자·숫자·하이픈만 쓴다.
- 웹 업로드까지 쓸 업무 폴더는 frontmatter에 `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` 외의 키를 넣지 않는다. [양식](templates/job-playbook/SKILL.template.md)은 이 조건을 지킨다.
- `description`에는 실제 호출 문장을 넣는다. 도구는 이 문장으로 스킬을 고른다.
- 양식의 `description`은 인용부호로 감싸져 있다. 대괄호로 시작하는 값을 인용 없이 쓰면 YAML에서 문자열이 아니라 목록이 된다.
- Codex는 심볼릭 링크 스킬 폴더를 따라간다고 문서에 적혀 있다. Claude Code와 Grok의 링크 동작은 확인하지 못했으므로, 링크 대신 마스터를 복사하고 갱신할 때 교체한다.
- 업무 폴더에 개인정보나 고객 자료가 들어 있다면 프로젝트별 경로를 저장소에 커밋하지 않는다.
