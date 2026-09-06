# FEF Claude Framework

Framework for Engineering Excellence(FEF)는 Claude 지향 엔지니어링 프롬프트 프레임워크입니다.

목표는 Claude가 더 일관되고, 근거 기반이며, 검토 가능하고, 엔터프라이즈급 기술 산출물을 만들도록 돕는 것입니다.

**English:** [README.md](README.md)

## AI 에이전트용 (저장소 URL만)

```bash
git clone https://github.com/yjj3019/claude.git
cd claude
python3 scripts/install_pack.py --auto
# Claude Code → 이 저장소를 워크스페이스로 열기 (CLAUDE.md 로드)
# Claude Projects → CLAUDE.md를 Project Instructions에 붙여넣기
```

- `python3 scripts/install_pack.py --auto` — Claude / Codex / Grok / Cursor / AGENTS 호스트를 감지해 `fef-claude/`로 복사
- `python3 scripts/install_pack.py --print-claude` — Claude Project Instructions 붙여넣기 절차
- `python3 scripts/install_pack.py --check` — 설치 파일 검증(+ tests 있으면 validate)

권장: **클론을 Claude Code 워크스페이스로 열기**해 루트의 `CLAUDE.md`가 로드되게 합니다.

## 핵심 아이디어

FEF는 모델 자체를 바꾸지 않습니다. 작은 상시 Kernel, 작업별 모듈/도메인/리뷰어/워크플로, 골든 테스트, Claude Code/Projects 가이드를 제공합니다.

## Context Budget + Model-Invariant Floor

**Context Budget:** `CLAUDE.md`의 Kernel + `docs/loading-map.md`가 지정한 팩만 Load Limits 안에서 로드 (Module 1 / Domain ≤2 / Workflow 1 / Reviewer 1 / Policies ≤3). 모든 문서를 미리 넣지 않습니다.

**Model-Invariant Floor** (`docs/model-usage.md`): Opus 5 / Fable 5.1 / Sonnet 5 / Haiku 4.5 모두 같은 Kernel·무결성·예산·라우팅을 유지합니다. 막히면 **모델을 올리고**, 관련 없는 팩을 추가로 덤프하지 않습니다.

권장(가용성 확인): 일상 복잡 → Opus 5 · 최장/최난 → Fable 5.1 · 일상 루틴 → Sonnet 5 · 빠른 응답 → Haiku 4.5.


## 지연·경량성 (Latency & lightness)

**상시(단순/저위험 cold-start):** `CLAUDE.md` Kernel만. model-usage·README·CHANGELOG·PROGRESS·SESSION_LOG·최적화 리포트·전체 모듈/도메인을 자동 로드하지 않습니다. **지연(latency) > 팩 완전 로드.**

**지연 로드:** 본격 작업만 `docs/loading-map.md`와 지정 팩. 모델이 막히면 팩을 덤프하지 말고 모델을 올립니다. Project Knowledge에 저장소 전체를 붙이면 응답이 느려집니다 — `CLAUDE.md`만 Instructions에 넣고 필요한 팩만 첨부하세요.


## Adaptive Effort (적응형 노력)

요청 복잡도(L0 Quick → L3 Hardest)에 따라 모델을 자동 조절합니다: 단순 사실=Haiku(Kernel만), 일상 루틴=Sonnet, 일상 복잡=Opus, 최장/최난=Fable. 안전한 최저 티어에서 시작하고, 팩을 늘리기 전에 **모델을 먼저** 올리며, L0–L1에서는 model-usage/README/PROGRESS를 미리 로드하지 않아 cold-start를 유지합니다. 상세: `docs/adaptive-effort.md`.

## 시작

1. `CLAUDE.md`를 세션 부트스트랩으로 읽습니다.
2. 단순·저위험은 Kernel만 사용합니다.
3. 본격 작업은 loading-map / `detect_task.py`로 최소 팩만 고릅니다.

## 검증

```text
python scripts/validate_framework.py
python scripts/sync_kernel.py --check
python scripts/measure_load.py
python -m unittest discover -s tests -p "test_*.py"
```

구조/라우팅 시뮬레이션: [docs/simulation-10-report-2026-09-06.md](docs/simulation-10-report-2026-09-06.md)
