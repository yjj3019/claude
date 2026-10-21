# 재배포 권한 및 실제 모델 세션 검증 — 2026-10-21

최신 후속 결과: 해시를 확인한 Linux 복사본에서 245개 실행·242개 통과·Windows 전용 3개 건너뜀, 실패·오류 0건. 승인 기록을 갖춘 합성 로컬 매뉴얼을 새 모델 세션에서 두 번 실행했고 결과를 독립 대조했다. 검증 기록 커밋의 Linux·Windows CI도 통과했다. 사용자는 추가 허락 자료 없이 기존 라이선스 정책을 따르도록 지시했다. 기존 라이선스·권리 고지를 유지하며 공개 재배포 허가를 새로 추정하지 않는다. 실제 업무 전체는 여전히 미검증이다. 아래는 각 시도의 실패·보완 과정을 포함한 누적 기록이다.

재배포 허가는 현재 확인된 자료만으로 확정할 수 없다. 실제 Claude 모델 호출에서는 세션 컨텍스트 전달, 네이티브 스킬 호출, 합성 코드 수정·재검증, 읽기 전용 RCA와 위임 인터뷰 시작을 관찰했다. 코딩 중 기록 훅 타임아웃 1회가 있었으며 종료 훅의 피드백 후 모델이 재검증해 복구했다. 무오류 실행이나 일반적인 품질 보장을 뜻하지 않는다.

## 재배포 권한

| 대상 | 확인한 근거 | 판단 |
|---|---|---|
| FEF 및 생성 배포본 | 루트/배포본 LICENSE가 `Permission is hereby granted...`에서 끝남 | 완전한 허가 조건을 확인하지 못함 |
| DelegationLoop 코드와 보관 번들 | 보관된 원본에 LICENSE가 없다는 고지·출처 이력; 현재 GitHub 저장소/라이선스 조회는 404 | 권한 부여를 찾지 못함. 404만으로 삭제·비공개를 구분하지 않음 |
| 원본 가이드와 재사용 문구 | 가이드의 프롬프트 복사·사용 안내, 저작자/저작권 표시 | 사용 안내와 공개 저장소의 수정·재배포 허용 범위를 구분해야 함. 명시적 공개 재배포 근거를 찾지 못함 |

확인 범위는 현재 저장소의 LICENSE·출처 고지·보관 이력과 공개 원문/홈페이지에 노출된 안내이다. 별도 계약, 비공개 허락, 사이트 전체의 모든 법적 문서와 각 기여자의 권리 관계까지 확인한 것은 아니다. 공개 저장소, 출처 표기, 이력 복원만으로 재배포 허가를 추론하지 않았다.

필요한 추가 근거는 FEF/DelegationLoop 코드 권리 보유와 완전한 라이선스 또는 권리자의 허가, 재사용한 원문 문구에 대한 허락 범위·조건이다. 사용자에게 해당 근거를 요청했으며 이 기록 시점에 답변을 받지 못했다. 저작자에게 메시지를 보내거나 라이선스를 새로 부여하지 않았다.

근거:

- [검증 기준 커밋의 LICENSE](https://github.com/yjj3019/claude/blob/9cd2f8b03678b4d036795f5f533a16dbc933f6d9/LICENSE)
- [통합 패키지 출처·권리 고지](https://github.com/yjj3019/claude/blob/9cd2f8b03678b4d036795f5f533a16dbc933f6d9/skills/ai-delegation-loop/THIRD_PARTY_NOTICES.md)
- [원본 AI 위임 루프 가이드](https://sdk-kim-builds.com/guides/ai-delegation-loop-playbook/)
- [GitHub 저장소 라이선스 안내](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository): 공개 열람·포크와 라이선스에 따른 복제·배포 권한을 구분한다.

## 실제 모델 세션

네이티브 훅·도구 호출과 공개 응답의 개인정보 제거 기록은 [구조화된 세션 증거](verification-2026-10-21.json)에 보존했다. Read 원문/중복 Kernel은 해시로 대체하고, Stop 결정·오류·테스트 결과·최종 상태는 남겼다.

- 기준 코드: `9cd2f8b03678b4d036795f5f533a16dbc933f6d9`; Claude Code 2.1.304, 네이티브 플러그인 1.3.1.
- 기존 로그인으로 실제 first-party 모델 응답과 usage를 수신했다. 호스트가 보고한 모델은 `claude-sonnet-5`이다. 모의 응답이나 과거 응답을 재사용하지 않았다.
- 101파일 배포본을 독립된 임시 폴더에 복사하고 `--plugin-dir`로 세션에만 로드했다. 사용자 설정 소스와 외부 MCP는 제외했고, `--restricted`와 `dontAsk` 권한을 유지했다. bypass 옵션은 쓰지 않았다.
- `--no-session-persistence`를 사용했다. 계정 인증값·비밀정보·모델 내부 추론은 이 보고서에 저장하지 않았다. 경로는 개인 사용자 디렉터리를 남기지 않도록 설명/예제에서 대체했다.

| 검증 | 실제 응답 소요 | 관찰 결과 |
|---|---:|---|
| 컨텍스트 전달 | 11.546초 | 관찰 범위 통과 |
| 코딩 최초 시도 | 72.647초 | 미검증: 명령 권한 불일치 |
| 코딩 재검증 | 191.978초 | 재시도 복구 후 통과; 타임아웃 1회 |
| RCA 읽기 전용 | 59.074초 | 합성 로그 분석 범위 통과 |
| 위임 스킬 인터뷰 시작 | 40.236초 | 첫 질문·파일 미작성 범위 통과 |

### 확인한 동작과 실패를 구분한 기록

1. **컨텍스트:** 도구가 없는 세션에서 프롬프트에 제시하지 않은 Kernel 첫 규칙·설치 루트·loading-map 경로를 정확히 반환했다. SessionStart/Stop 네이티브 훅 실행과 상태 파일 생성도 관찰했다.
2. **최초 코딩:** 스킬 호출과 코드 수정은 됐으나 모델이 명령 앞에 `cd … &&`를 붙여 허용한 명령 접두사와 불일치했다. Windows Read 경로의 `/tmp` 별칭도 거부됐다. 테스트 수행·검증 기록은 미완료로 보존했으며, CLI 종료 코드 0을 테스트 통과로 해석하지 않았다.
3. **코딩 재검증:** 허용 권한은 그대로 두고 실제 Windows 경로와 현재 cwd에서의 명령 사용을 명시했다. 모델이 `fef-engineering:fef-coding`을 호출해 실패 테스트를 재현하고 `calculator.py` 한 줄만 수정했다. 보호한 테스트 파일은 바뀌지 않았다. 래퍼를 통한 테스트 3건이 통과했고 독립 재실행도 3건 통과했다.
4. **기록 오류와 복구:** 첫 성공 테스트 뒤 PostToolUse 훅 stderr에 `TimeoutExpired`가 기록됐다. Stop 훅 stdout에 `decision: block`이 나와 미기록 상태의 종료를 보류했고 모델이 래퍼를 다시 실행했다. 이후 기록은 returncode 0과 현재 snapshot 일치, 마지막 Stop은 비차단이었다. 정확한 지연 하위 명령/시스템 원인은 미확정이며, 예전 간헐 회귀 실패와 동일한 원인이었다고 단정하지 않는다. 이 훅은 무한 반복을 막는 알림 장치이며 모든 종료를 강제 금지하는 보안 경계가 아니다.
5. **RCA:** `fef-engineering:fef-rca`를 실제 호출해 합성 설정·로그를 Read로 읽었다. 8081 listen/8080 healthcheck 불일치를 식별하고 별도 health 포트 설계 가능성 등 미확인 사항을 분리했다. 명령·수정·실제 서비스 복구를 수행했다고 주장하지 않았고 입력 파일도 그대로였다.
6. **위임 스킬:** `fef-engineering:ai-delegation-loop`를 실제 호출하고 현재 단계의 인터뷰 프롬프트를 읽었다. 시작 계기에 관한 질문 하나를 하고 기다렸으며 업무 파일을 만들지 않았다. 8문답 전체·사용자 승인·업무 실행·재실행까지 검증한 것은 아니다.

코딩에서 실제 실행한 검증 명령은 아래 형태다. `{{INSTALLED_ROOT}}`는 임시 배포본의 절대 경로를 대체한 표기다.

```text
python "{{INSTALLED_ROOT}}/scripts/run_verification.py" -- python -m unittest discover -s . -p test_calculator.py -v .
```

최종 상태와 세션 식별자:

```json
{
  "source_head": "9cd2f8b03678b4d036795f5f533a16dbc933f6d9",
  "cli_version": "2.1.304",
  "plugin_version": "1.3.1",
  "reported_model": "claude-sonnet-5",
  "provider": "firstParty",
  "sessions": {
    "context": {
      "id": "e0b93462-f1ca-4d73-b963-09419f41c4b5",
      "duration_ms": 11546,
      "turns": 1
    },
    "initial_coding": {
      "id": "e3a4dfc9-0eac-4d33-b3cf-05c803e35f57",
      "duration_ms": 72647,
      "turns": 13
    },
    "coding": {
      "id": "b078c893-5366-468d-a42f-2f32b48b250b",
      "duration_ms": 191978,
      "turns": 11
    },
    "rca": {
      "id": "0529bea5-68b1-456a-927f-0cb4dfdd5941",
      "duration_ms": 59074,
      "turns": 6
    },
    "delegation": {
      "id": "a0133b2e-a975-464c-b589-84b06bb9e4e2",
      "duration_ms": 40236,
      "turns": 4
    }
  },
  "coding_verification": {
    "returncode": 0,
    "snapshot": "dd365b27b063b2ed2fc2009355ed32f4d3c96d979bfff128eff0d4aa307ea926"
  },
  "coding_current_snapshot": "dd365b27b063b2ed2fc2009355ed32f4d3c96d979bfff128eff0d4aa307ea926",
  "coding_protected_tests_unchanged": true,
  "coding_independent_test_exit": 0,
  "payload_file_count": 101,
  "payload_unchanged": true,
  "payload_manifest_sha256": "16b9fc63d30d99be99e7fe5ed6b3e9296f4037f27edd8aee5ec40b4683adbfa8",
  "user_settings_json_unchanged": true,
  "observed_post_tool_timeout_count": 1,
  "observed_stop_block_count": 1
}
```

## 한계와 남은 작업

- 관찰은 한 Windows 호스트, 한 CLI 버전과 한 설정 모델에서 수행한 사례다. 자동 스킬 선택, marketplace 캐시 설치 후의 모델 세션, 다른 모델/호스트, Codex/ChatGPT 경로를 모두 검증한 것은 아니다.
- 실제 모델 API 호출은 확인했지만 업무 데이터는 합성 fixture다. 실제 운영 서비스·사용자 업무 전체·외부 게시/메일/배포를 검증하거나 실행하지 않았다.
- 기록 훅 타임아웃이 실제 1회 발생했다. 재검증 복구와 상태 일치는 확인했지만 지연 원인을 고치거나 안정성을 보장한 것은 아니다.
- 원본 배포본 101파일과 사용자 settings.json은 전후 해시가 같았다. 제품 코드·라이선스·전역 권한·플러그인 설치 설정은 수정하지 않았다.
- CLI가 보고하는 비용은 list 기준 환산값이므로 실제 청구·구독 차감액이나 비용 절감의 근거로 사용하지 않았다.
- 현재 요청에서는 검증 기록만 로컬에 남긴다. 커밋·푸시 또는 새 라이선스 선언은 수행하지 않았다.

## 추가 확인 — 2026-10-21

### 재배포 권한의 추가 조사

- 보관 번들의 `list-heads`가 알리는 main·feat·optimize와 remote 참조를 모두 임시 bare 저장소로 가져와 조사했다. 기본 clone의 main만 보지 않고 `+refs/*:refs/*`를 명시해 참조를 복구했다. 중복 참조를 포함한 advertised refs는 HEAD 포함 6개, 도달 가능한 고유 커밋은 5개다.
- 해당 이력과 세 고유 tip에서 LICENSE/COPYING/NOTICE 및 저작권·재배포 허가 문구를 조사했으나, 명시적 권한 부여를 찾지 못했다. 커밋 작성자 표시는 권리 보유·양도의 증명이 아니다.
- FEF checkout은 shallow이며, 현재 로컬에서 보이는 58개 커밋의 LICENSE 이력만 확인했다. 현재 LICENSE는 여전히 불완전한 MIT 자리표시자다. 전체 원격 이력·비공개 계약을 조사한 결과로 확대하지 않는다.
- 루트 LICENSE의 확인 가능한 두 과거 버전(`1770df0`, `58ae7d8`)도 모두 같은 불완전한 허가 문구다. 원격 전체 이력 확인을 위한 `git ls-remote`는 `getaddrinfo() thread failed to start`로 실패했다. 번들은 당시 보관된 도달 가능한 이력이며, 삭제·도달 불가 참조나 GitHub 전용 자료를 모두 포함한다는 뜻은 아니다.
- 원본 가이드·홈·[문의 페이지](https://sdk-kim-builds.com/contact/)를 다시 확인했다. 프롬프트의 복사·사용 안내와 저작권 표시는 있지만 공개 수정본·번들 재배포의 명시적 허락 범위는 확인하지 못했다. 문의 경로만 확인했으며 연락하거나 양식을 제출하지 않았다.

판정은 여전히 **재배포 허가 미확정**이다. 아래 근거가 있어야 이를 해소할 수 있다.

1. FEF 자체 코드의 권리 보유·기여 권리 관계와 적용할 완전한 라이선스.
2. DelegationLoop 원본 코드·Git 번들 및 재사용한 가이드 문구·프롬프트의 권리자가 허용한 범위: 공개 저장소 게시, 수정, 배포와 필요하다면 상업적 이용·재허락, 유지할 표시와 조건.
3. 허락 대상의 저장소·커밋·문서와 권리자·허락 일자를 확인할 수 있는 기록.

FEF의 LICENSE만 완성해도 제3자 부분의 권리가 자동으로 해결되는 것은 아니다. 단순 아이디어·업무 절차와 복제한 문구·코드·번들을 구분하고, 실제 재사용 범위를 근거와 함께 확인해야 한다. 사용자에게 권리 자료를 요청했고, 후속 답변은 아래 '사용자 확인 및 전달'에 반영했다. 임의로 라이선스를 새로 부여하지 않았다.

### 타임아웃 추가 진단

격리된 임시 Git 저장소에서 현재 배포본의 `repository()`와 `snapshot()`을 20회 호출했다. 19회는 완료했고, 1회는 **`git rev-parse --show-toplevel`에서 15.460초 후 TimeoutExpired**가 발생했다. 이번 재현에서는 정확한 하위 명령을 기록했으나, 이전 모델 세션에서 지연된 명령도 이것이었다고 소급 단정할 수 없다. 새 Git 저장소여서 `rev-parse --verify HEAD`의 반환값 128은 HEAD가 아직 없는 정상 조건으로 구분했다.

별도 오류 주입에서는 기록 훅이 진단 메시지를 출력하고 성공 검증을 새로 만들지 않았다. 이 검사는 타임아웃 처리 경로의 확인이며, 과거의 성공 기록이 모든 오류 상황에서 삭제된다거나 모든 종료를 강제 차단한다는 보장이 아니다. Git 프로세스 지연이 재현됐다는 수준이며 OS·보안 프로그램·부하 중 어느 것이 원인인지는 미확정이다. 제한 시간을 늘리거나 제품 코드를 바꿔 실패를 가리지 않았다.

추가 실제 모델 세션·정적 검증 결과는 [추가 구조화 증거](verification-followup-2026-10-21.json)에 기록한다.

### 추가 실제 모델 세션과 범위별 판정

기존과 같은 `claude-sonnet-5`에서 추가 4세션을 실행했다. 임시 폴더의 합성 자료만 사용했고, 8문답의 답변과 승인 표시는 시험용으로 제공했다. 실제 사람의 인터뷰·업무 승인을 했다는 증거로 사용하지 않는다.

| 항목 | 관찰 | 판정 |
|---|---|---|
| 업무 설명으로 스킬 선택 | 첫 세션이 이름을 강제 지정하지 않은 요청에서 `fef-engineering:ai-delegation-loop` 호출 | 이 사례의 자동 선택 확인; 일반적인 선택 정확도 보장 아님 |
| 최초 매뉴얼 초안 | `--restricted`의 cwd 밖에 둔 플러그인 프롬프트·템플릿 Read 거부. 초안은 생성했지만 필수 frontmatter 누락 | 형식 수용 기준 FAIL |
| 저장 매뉴얼의 새 세션 로딩 | 두 세션 모두 실제 SKILL.md와 서로 다른 W1/W2 입력을 Read. 초안의 미승인 상태를 이유로 report.md 미작성 | 파일 재로딩 관찰; 업무 실행·재실행 완료는 UNVERIFIED |
| 명시한 파일 접근 범위의 재시도 | 복사한 플러그인 폴더만 `--add-dir`로 추가하고 restricted/dontAsk 유지. 원문 프롬프트·템플릿 Read 성공, 다른 폴더에 교정 초안 생성 | frontmatter와 필수 섹션 정적 확인 통과; 실행 완료 아님 |

접근 범위 재시도는 임시 테스트 세션에만 적용했다. 전역 권한·설치 설정·제품 코드는 바꾸지 않았다. 두 번째 입력은 새 세션 전에 시험기가 바꾼 합성값이며, 모델이 입력을 고쳐 결과를 맞춘 것이 아니다. 원래 초안은 보존했다.

초안의 파일 내부 미승인 표시와 시험용 승인 메시지가 충돌한 상황에서 모델은 업무를 진행하지 않았다. 이를 실제 사람의 승인 보장, 모든 무단 행동 차단 또는 성공적인 전체 위임 루프로 해석하지 않는다. 실제 인터뷰, 승인 기록 확정, 첫 업무 통과, 툴박스 저장, 검증 규칙 확정, 두 번째 업무 완료까지 이어지는 전체 검증은 남아 있다. 이 범위를 통과시키려고 초안의 게이트나 판정 기준을 삭제하지 않았다.

임시 시험기는 한글 터미널 출력의 cp949 인코딩 오류로 한 번 중단됐다. 저장된 완료 세션 증거는 보존했고, UTF-8 출력으로 수정한 시험기에서 나머지 세션만 이어 실행했다. 제품 런타임 결함이나 완료 모델 세션의 재실행으로 혼동하지 않는다.

### 추가 검증 집계와 남은 제한

- `python scripts/validate_repository.py`: exit 0, 저장소 구조 통과. Golden Test 31개는 인덱스 확인이며 31개 모델 작업을 실행한 뜻이 아니다.
- `python scripts/build_plugin.py --check`: exit 0, 배포본 101파일 동기화 통과.
- `python -m unittest discover -s tests -p test_hooks.py -v`: 샌드박스에서는 40 tests / 75 errors / 0 failures / 0 skips, exit 1. setUp의 Git 초기화와 cleanup의 WinError 5가 반복됐다. 하나의 테스트에서 준비·정리 오류가 각각 집계될 수 있다.
- 샌드박스 밖 재실행은 완료된 10개가 통과했으나 긴 지연 때문에 시험기 프로세스를 중단했다. **전체 훅 회귀의 최종 통과는 확인하지 못했다.** 제품 오류와 실행 환경 문제의 구분을 위해 두 결과를 함께 보존한다. 새 전체 회귀를 통과했다고 기록하지 않는다.
- 실제 marketplace 캐시 설치 후 모델 세션, 다른 모델·호스트와 Codex/ChatGPT의 전체 경로는 이번 추가 시험에서도 실행하지 않았다. 사용자 설치·계정 설정을 바꾸지 않는 세션 전용 플러그인 범위의 결과다.
- 외부 서비스 복구·전송·게시·배포, 실제 업무 데이터, 실제 사람 인터뷰·승인, 별도 계약과 삭제·도달 불가 이력은 미검증이다. 원본 저작자에게 연락하지 않았다.
- 자동 승인 검토가 감사용 bare clone의 재귀 삭제를 거절했다. 사유는 사용자가 명시적 삭제 승인을 하지 않았고 AGENTS.md가 사전 승인을 요구한다는 것이다. 임시 복제본 `{{VISUALIZATION_ROOT}}/DelegationLoop-rights-audit-8f75dba3`는 보존했으며 우회 삭제하지 않았다. 모델 시험용 임시 fixture도 보존했다.
- 이번 추가 작업도 검증 문서·비식별 증거·이력만 로컬에 기록한다. 커밋·푸시·새 라이선스 선언은 하지 않았다.

## 후속 실행 — 합성 업무 재사용과 원격 권리 이력

### 검토한 합성 매뉴얼의 새 세션 실행

이전의 미승인 초안 중단 기록은 그대로 보존했다. 검증 에이전트가 교정 초안의 입력·출력 계약, 네 가지 완료 기준, 미지 status 중단과 외부 행동 금지를 읽고 검토한 뒤, 별도 임시 복사본에 **합성 자료의 로컬 시험만 허용하는 검토 기록**을 추가했다. 실제 사람의 업무 승인이나 8문답을 대신했다는 기록은 만들지 않았다. 원래 초안과 완료 기준은 삭제하거나 완화하지 않았다.

두 새 실제 모델 세션이 같은 저장 매뉴얼과 검토 기록을 읽고, 매번 다른 입력으로 `report.md`를 생성했다. 보호한 입력·매뉴얼·검토 기록은 실행 전후 해시가 같았다. 모델의 자체 PASS 선언과 별도로 메인 검증기가 실제 결과 파일의 각 항목과 집계 값을 합성 원본과 대조했다.

| 세션 | 입력 | 결과 | 독립 대조 |
|---|---|---|---|
| `b721fc0d-c368-48da-b436-85a40b1cdbfd` | W3, Alpha/Beta/Gamma | done 2, pending 1 | 항목·상태·이름 1회·주차·15줄 이하 모두 통과 |
| `630e11ad-1e73-44cb-90b6-0b079e6b5a85` | W4, Delta/Epsilon/Zeta/Eta | done 1, pending 3 | 같은 기준 모두 통과; 이전 결과 재사용 아님 |

모델에 셸 도구는 제공하지 않았으므로 모델이 단위 테스트나 해시 계산을 실행했다고 주장하지 않는다. 검토 기록의 해시는 승인 주석을 덧붙인 현재 복사본이 아니라 **검토 대상인 원래 초안**을 가리킨다. 메인 검증기가 해당 해시의 일치와 복사 배포본 101파일의 원본 일치를 별도로 확인했다.

비식별 세션·합성 입력·독립 대조 근거는 [합성 업무 실행 증거](verification-approved-fixture-2026-10-21.json)에 있다. 확인 범위는 승인 기록을 갖춘 합성 로컬 매뉴얼의 두 번 실행(L3)이며, 8문답 전체·실제 담당자 검토·툴박스 저장·검증 규칙 보완·운영 업무 전체의 증거는 아니다.

### 원격 LICENSE 이력 조회 보완

네이티브 Git의 원격 조회 실패와 별개로 GitHub 연결의 GET 요청으로 다음을 확인했다.

- 원격 main은 검증 기준 `9cd2f8b03678b4d036795f5f533a16dbc933f6d9`와 일치했다.
- [해당 main 기준 LICENSE 변경 목록](https://api.github.com/repos/yjj3019/claude/commits?path=LICENSE&sha=9cd2f8b03678b4d036795f5f533a16dbc933f6d9&per_page=100)은 2개를 반환했다. [최초 버전](https://github.com/yjj3019/claude/blob/1770df0c8e7aa3ef08487053f222a76f77593f4e/LICENSE)과 [권리자 표시 수정 버전](https://github.com/yjj3019/claude/blob/b0f48dfa3e72c6421e9157b51517b6a7040709d3/LICENSE) 모두 허가 본문이 불완전하다.
- 따라서 로컬 shallow 이력만 보았다는 한계를 LICENSE 경로의 원격 main 조회로 보완했다. 모든 브랜치·삭제/도달 불가 이력·권리 관계·비공개 계약 전체를 확인했다는 뜻은 아니다.
- 원본 `yjj3019/DelegationLoop` GET은 현재 연결에서도 404였다. 삭제·비공개·접근권한 부족 중 어느 원인인지 단정하지 않는다.

추가 확인 후에도 **공개 재배포 허가는 미확정**이다. 권리 보유·양도·허락 자료가 필요하며, 라이선스 변경이나 원본 저작자에게 연락하는 작업은 하지 않았다.

### Linux 전체 회귀와 실행 전후 무변경 확인

WSL의 기본 샌드박스 조회는 접근 거부였지만, 허용된 격리 밖 읽기·검증 실행에서는 Ubuntu에 접근했다. Windows 공유 경로에서 테스트하지 않고, 바이너리 stdin으로 원본 파일과 Git 메타데이터를 Linux 네이티브 임시 디렉터리에 복사했다. 전송과 HEAD를 검증한 후 테스트를 실행했다. 전역 설정·패키지를 바꾸지 않고 검증 프로세스의 임시 PATH에만 `python` 별칭을 제공했다.

첫 완주도 main 196개·위임 49개를 실행해 실패 없이 끝났으나, 후속 조회에서 임시 복사본이 없어 테스트 후 파일별 대조를 하지 못했다. 이 증거 누락을 보완해 같은 프로세스 안에서 테스트와 전후 대조를 마치는 최종 검증을 한 번 수행했다. 처음의 빈 전송과 잘못 지정한 0개 테스트 경로는 통과 집계에서 제외했다.

최종 원본 증거는 [Linux 실행·전후 해시 증거](verification-linux-final-2026-10-21.json)에 있다.

| 명령 | 결과 |
|---|---|
| `python -m unittest discover -s tests -v` | 196개 실행, 194 통과, 2 건너뜀, 7.555초, exit 0 |
| `python -m unittest discover -s scripts/delegation -p test_*.py -v` | 49개 실행, 48 통과, 1 건너뜀, 2.659초, exit 0 |
| `python scripts/validate_repository.py` | exit 0, 10 routes와 Golden Test 인덱스 31개 확인; 모델 실행 제외 |
| `python scripts/build_plugin.py --check` | exit 0, 배포본 101파일 동기화 |

- 기준 HEAD는 `9cd2f8b03678b4d036795f5f533a16dbc933f6d9`, 실제 Python은 3.12.3이다.
- 전송 559개 파일의 manifest SHA-256은 `696a19f77aa873f50fbfaaea0725308b6ad7a02774880d7e4e3c89c8f5a874c2`로 수신 후 일치했다.
- 프로젝트 파일 451개의 실행 전후 파일 집합·바이트는 동일했다. 양쪽 manifest SHA-256은 `6e90f7784c780ac76af0b99b949fa41b80a53f257052dcdfc2f4c7da0bf82b6c`이다. 변경 가능한 `.git` 메타데이터와 Python bytecode cache는 사후 무변경 비교에서 제외했다. 원본 프로젝트의 기존 파일 내용도 그대로였다.
- 건너뛴 항목은 `test_short_path_alias_normalized_after_link_check`, `test_real_windows_junction_source_and_destination_refused`, `test_windows_junction_parent_refused`이며 모두 실제 출력과 `os.name == "nt"` 조건으로 확인했다.
- 따라서 최신 **Linux 전체 회귀**는 245개 중 242 통과·3 Windows 전용 건너뜀이다. Windows 전체 재실행 완료나 간헐 Git 지연의 근본 원인 수정으로 표현하지 않는다. Windows의 이번 별도 시도도 진행 표시 8개 후 중단돼 판정에서 제외했다.
- 현재 Windows Git은 `C:\Program Files\Git\cmd\git.exe`, 2.54.0.windows.1이며 현재 저장소의 한 번 조회는 약 2.37초에 완료됐다. 이전 15.460초 실패는 별도 임시 저장소에서 재현한 결과다. 같은 지연 원인이었다고 단정하지 않는다.
- 합성 업무 실행은 저장된 매뉴얼 경로를 명시한 방식이며, 새 업무 스킬 설치·자동 선택이나 marketplace 설치 상태의 검증은 포함하지 않았다. 외부 행동·실제 담당자 승인·운영 전체·저작권 계약도 여전히 범위 밖이다.
- 최종 증거 저장 이후의 변경은 이 검증 문서와 이력뿐이다. 제품 코드·생성 배포본·라이선스는 바꾸지 않았다. 임시 검증 파일은 보존했으며 커밋·푸시는 하지 않았다.

### 사용자 확인 및 전달

- 사용자는 추가 허락 자료가 없으며 기존 라이선스 정책을 따르도록 지시했다. 이 답변을 모든 코드의 권리 보유 또는 재배포 허가로 해석하지 않는다. 권리 자료의 답변 대기 단계는 종료했으며, 재배포 허가 미확정 상태를 유지한다.
- 기존 LICENSE·권리자 표시와 THIRD_PARTY_NOTICES의 고지를 보존한다. 불완전한 MIT 자리표시자를 완전한 허가로 간주하거나 제3자 부분을 MIT로 재선언하지 않는다. 새 릴리스·추가 패키지 재배포의 허용 근거도 이 검증 기록에서 만들지 않는다.
- 사용자의 별도 명시 요청에 따라 검증 문서·비식별 증거·이력 7개 파일을 `f1ba32252ec5e3f75a617b713b26a5cfff1a9817`로 커밋해 origin/main에 정상 푸시했다. 기존 코드 수정은 이미 main에 포함돼 별도 병합 대상이 없었다. 앞 절들의 미커밋·미푸시 표시는 각 검증 시점의 이력이다.
- 해당 커밋의 [Validate FEF Harness](https://github.com/yjj3019/claude/actions/runs/39506459166)와 [Validate Delegation Loop](https://github.com/yjj3019/claude/actions/runs/39506459335)는 모두 success였다. Linux Python 3.11/3.12/3.14, Windows installer/hooks/build-plugin Python 3.11/3.14와 위임 패키지의 Linux·Windows 행렬이 포함된다. CI 통과는 실제 업무·모델 품질·권리 허가 또는 로컬 Windows 지연 원인의 증명이 아니다.
- 이 사용자 확인도 문서·이력에만 반영한다. 코드·생성 배포본·라이선스 본문은 변경하지 않는다.

### 미해결 훅 오류 후속 수정 — 로컬 미커밋 변경

기준 HEAD `edd862cd09821a6c636197a15ca1db9d6f64ce6b`에서 이전 성공 뒤 새 검증의 스냅샷 수집, 결과 처리 또는 최종 상태 저장이 실패하면 기존 성공 기록이 남는 결함을 재현했다. 수정 전 관련 4개 테스트는 1개 통과·새 회귀 3개 실패였다. 이제 인식된 검증 시도가 세션 상태를 읽은 직후 기존 성공을 먼저 무효화해 저장하고, 실제 결과가 준비됐을 때만 다시 기록한다. 기존 상태 스키마·일반 셸 호출·wrapper footer·권한 설정은 유지한다.

Git 시간 초과는 정확히 알려진 argv에 한해 `repository`, `status`, `head`, `index` 중 고정 작업명을 출력한다. 명령 인자·경로·stdout/stderr·예외 메시지는 출력하지 않는다. 알 수 없는 명령은 예외 유형만 표시하며, 테스트에 민감 문자열 canary를 넣어 누출 여부를 검사했다. 이것은 Windows 지연 원인 해결을 뜻하지 않는다.

| 검증 | 실제 결과 |
|---|---|
| 훅 대상 테스트 | 45개 실행·45 통과, 2.699초, exit 0 |
| 전체 `tests` | 201개 실행·199 통과·2 Windows 전용 건너뜀, 11.776초, exit 0 |
| `scripts/delegation` | 49개 실행·48 통과·1 Windows 전용 건너뜀, 3.772초, exit 0 |
| 저장소 검증 / 생성 배포본 검사 | 각각 exit 0, 101파일 동기화; Golden 31개는 인덱스 확인이며 모델 실행 아님 |

Ubuntu native 임시 복사본 / Python 3.12.3에서 실행했다. 합계 250개 실행·247 통과·3 건너뜀, 실패·오류 0이다. 건너뛴 테스트는 앞 Linux 검증과 같은 Windows short-path 및 junction 3개다. 전송 576파일 archive SHA-256은 `8d0b03b4c63c72bcca21681175f44fd62c5447bfa7603566de2c0d9163f018ce`, 프로젝트 452파일의 실행 전후 manifest는 양쪽 모두 `6a3b7274dc1fcbcbc48f9ae8c97b8a1be2cd7b60b781cd1f72a7b0fac71b4303`였다. `.git` mutable metadata와 bytecode는 비교에서 제외했고 원본 프로젝트 바이트도 불변이었다. 임시 원본 결과는 `fef-hook-red.json`, `fef-hook-targeted.json`, `fef-hook-full.json`에 보존했다. 위 해시는 이후 이 검증 기록·진행 이력 갱신 전의 코드·문서 스냅샷에 해당한다.

로컬 최종 diff 검토에서 상태·호출자·실패 경로·생성본 동기화와 새 회귀 5건을 확인했다. 최초 필수 `code-change-reviewer` 실행은 외부 Claude CLI 모델에 diff를 전송하는 명시적 승인 부재로 자동 승인 검토가 차단했다. 당시 외부 전송을 우회하지 않았으며, 이후 아래의 사용자 승인과 성공한 독립 리뷰로 대기 상태를 해소했다.

저장소 조회 또는 최초 무효화 저장부터 실패하면 이전 성공을 지우지 못할 수 있는 fail-open 한계는 유지한다. Windows 전체 재실행·시스템 지연 원인·marketplace 캐시 모델 세션·유효한 ablation 비교는 이번 범위에서 검증하지 않았다. 추가 재배포 허가는 여전히 미확정이며 기존 LICENSE·고지를 유지한다. 현재 변경은 커밋·푸시하지 않았다.

### 명시 승인 후 독립 리뷰와 관련 회귀 재실행

사용자는 이번 변경 diff의 외부 Claude 전송과 독립 리뷰, 필요한 수정·관련 검증을 명시적으로 승인했고 커밋·푸시는 금지했다. 전송 범위는 위 코드 3파일·테스트·사용 안내의 diff이며 SHA-256은 `45e5453c20247aea8eae3111ccd9968c01d54e0cf769bc071fb7ced06de92c57`이다.

`--setting-sources ""` 실행에서 프로젝트 역할을 찾지 못해 초기 시도는 리뷰 결과 없이 종료됐다. CLI `--agents`에 기존 `.claude/agents/code-change-reviewer.md`의 같은 정의를 명시하고 `--agent code-change-reviewer`로 실행했다. 실제 init에서 역할 등록, 모델 `claude-sonnet-5`, 허용 도구 Read/Grep/Glob을 확인했다. 설정·권한 변경, 셸/쓰기 도구, MCP 연결, 임의 역할·모델 대체는 없었다. 성공한 리뷰는 1회이며 12턴·190.389초·모델 exit0으로 완료했다. 저장 후 콘솔 인코딩 오류는 UTF-8 결과 JSON 조회로 해소했고 추가 모델 리뷰를 실행하지 않았다.

- 판정: **Approve, Critical/Major 없음**. 선 무효화의 순서, 세 가지 실패 경로 회귀, 정확한 Git argv의 고정 라벨과 민감 정보 비출력, 문서의 fail-open 한계가 일치한다고 확인했다.
- Minor: 인식된 시도마다 상태 쓰기가 1회에서 2회로 증가한다. 최종 저장 이전 오류에서도 이전 성공을 제거하기 위한 추가 저장이므로 유지했다. 큰 snapshot 수집을 추가한 변경은 아니다.
- 제안: 저장소 조회/최초 쓰기 실패 경계의 테스트와 Git argv 공유 상수. 현재 결함이나 차단 항목이 아니므로 추가 테스트·리팩터링은 이번 범위에서 하지 않았다. 기존 fail-open 한계도 유지한다.
- 리뷰는 정적 분석이며 테스트 실행은 별도다. 승인 후 훅 대상 테스트를 native Linux 복사본에서 다시 실행해 **45개 실행·45 통과·skip/실패/오류 0**을 확인했고, 프로젝트452파일의 전후 집합·바이트도 같았다. 직전 전체 **250실행·247통과·3 Windows전용skip**은 제품 코드가 같은 별도 선행 검증 결과다.

제품 코드의 추가 수정은 필요하지 않았고 리뷰·이력 기록만 갱신했다. 리뷰 결과는 임시 `fef-hook-review.json`에 보존했다. Windows 전체·시스템 지연 원인·marketplace 모델 세션·유효 ablation과 추가 재배포 권리는 기존 제한 그대로이며 커밋·푸시는 하지 않았다.

### Windows 지연 및 최초 상태 저장 실패 후속 재현·수정

사용자가 남은 두 문제의 재현·분석과 호환 수정·회귀 검증을 요청했다. 아래는 앞 절 이후의 추가 변경이며, 기존 미해결 표시를 범위별로 보완한다.

#### Windows 지연 측정

전역 PATH·Git 설정·자격증명·보안 제품 설정을 바꾸지 않고, 동일 Python 프로세스에서 Popen 생성 시간·전체 wall 시간·GetProcessTimes CPU 시간과 Git TRACE2의 고정 이벤트 시간만 수집했다. 원시 TRACE2는 임시 폴더에 보존하고 경로·환경 내용은 보고서에 복사하지 않았다.

첫 진단은 Python noop, Git version, 임시 저장소 조회, 작업 저장소 조회 각 4회로 총16표본이었다. timeout은 0이며 최대 wall은1.663초였다. 평균 wall은 각각0.687/1.488/1.338/1.179초, Git TRACE2 start→exit는 평균0.0737초(0.0585–0.0870초)였다. 이 표본에서는 Git 내부 조회보다 실행 전후 비용이 컸다. 이는 Windows의 특정 드라이버·보안 제품·OS 결함을 식별한 증거는 아니다.

이어서 같은 설치의 `cmd/git.exe`(46,480bytes)와 `mingw64/bin/git.exe`(4,422,544bytes)를 비교했다. 두 실행 파일은 `git version 2.54.0.windows.1`을 동일하게 출력했다. 4회씩 총16표본, timeout0:

| 작업 | 기본 프록시 평균 wall | 실제 바이너리 평균 wall |
|---|---:|---:|
| `--version` | 1.409초 | 0.729초 |
| 작업 저장소 `rev-parse --show-toplevel` | 1.267초 | 0.656초 |

정상 실행의 시작 비용 중 프록시 경유 비용이 기여한다는 근거다. [Git for Windows 공식 wrapper 안내](https://gitforwindows.org/git-wrapper.html)는 `cmd/git.exe`가 환경을 준비하고 실제 프로그램을 실행하며, 반복 호출 시 시작 비용이 발생할 수 있다고 설명한다. 이 측정만으로 과거15.460초 timeout의 원인을 입증하거나 보안 제품 탓으로 단정하지 않는다. [Python subprocess 문서](https://docs.python.org/3/library/subprocess.html#subprocess.run)도 최초 프로세스 생성 시간이 timeout에 의해 즉시 중단되지 않을 수 있음을 명시한다.

사용자가 선택한 PATH의 Git을 존중하고 설치 내부 경로를 추정해 우회하지 않았다. timeout을 늘리거나 전역 Git·권한·보안 설정을 변경하지 않았다. 원본 측정 JSON은 임시 `fef-windows-latency.json`과 `fef-windows-proxy.json`에 보존했다.

#### 저장 실패 결함과 호환 수정

최초 SessionStart baseline 저장 실패와 기존 성공 뒤 첫 무효화 저장 실패를 `os.replace` PermissionError로 재현했다. 수정 전 두 회귀는 Stop의 빈 stdout을 JSON으로 읽는 오류로 종료됐다(2실행/2error). 이는 앞선 PermissionError·이전 파일 보존 검사는 통과했지만 필요한 block 결정이 없었기 때문이다. Windows에서는 실제 CreateFileW 핸들에 FILE_SHARE_DELETE를 허용하지 않아 기존 JSON의 교체를 실패시켰다. 이 실제 잠금 회귀도 수정 전1실행/1error로 같은 Stop 허용을 확인했다. [Microsoft CreateFile 설명](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea)의 파일 공유·삭제/rename 계약과 일치한다.

- `save_state`는 생성·직렬화·교체·정리 실패를 같은 세션 해시의 `.failed` 표식으로 남긴 뒤 원래 예외를 다시 전달한다. 추가 표식/정리 실패가 최초 예외를 덮거나 민감한 예외 문자열을 출력하지 않는다. 표식도 쓸 수 없으면 고정 경고를 출력한다.
- Stop은 baseline/이전 성공을 읽기 전에 표식을 확인해 상태 저장 오류라는 정확한 이유로 한 번 차단한다. `stop_hook_active` 반복 방지는 그대로다. 정상 저장에 성공해야 표식을 해제한다. 실패한 검증 결과 저장은 정상 저장이어도 결과 코드에 따라 계속 차단한다.
- JSON version1·경로·기존 baseline/custom fields와 다른 세션을 보존한다. 표식 없는 missing/corrupt 상태의 기존 fail-open도 유지한다. 자동 timeout 재시도나 새 의존성·잠금 구조는 추가하지 않았다.
- 독립 방향 검토 후 이 최소안을 적용했다. 전체 파일시스템 쓰기 불가·루트 조회 실패·병렬 writer의 원자성은 보장하지 않는다. missing baseline 복구나 clear는 그 시점의 새 baseline이므로 이전 변경 검증을 보장하지 않는다.

#### 회귀 결과

| 검증 | 실제 결과 |
|---|---|
| Linux hook suite | 51실행/50통과/Windows 잠금1skip, 2.417초 |
| Linux main suite | 207실행/204통과/Windows 전용3skip, 8.813초 |
| Linux delegation suite | 49실행/48통과/Windows 전용1skip, 2.690초 |
| Windows 최초 저장 실패 | 2실행/2통과, 88.480초 |
| Windows 실제 잠금 경계 | 1실행/1통과, 29.666초 |
| Windows 저장·표식·정리 단위 테스트 | 3실행/3통과, 0.017초 |

Linux 전체 합계는 **256실행/252통과/4 Windows전용skip/실패·오류0**이다. 새 Windows 잠금 테스트는 Linux에서 건너뛰었지만 위 Windows 실행에서 실제 통과했다. 나머지 Windows-only3개는 이번에 다시 실행하지 않았다. 저장소 검증 및 payload101 동기화는 exit0이었다. Golden31개는 인덱스 확인이며 모델 실행은 아니다.

Linux native snapshot/Python3.12.3, 기준 HEAD `edd862cd09821a6c636197a15ca1db9d6f64ce6b`. 전송576파일 archive SHA-256 `630568ed07b39c46bfe197e894bb773d763a8b724d8f8eac5853b35e2ca27d03`, 프로젝트452파일 전후 manifest `58fc73d0e68088dec4aec2724c376ae610ff4852cef3df83d93d5b075f34fc2a`로 동일했다. mutable Git metadata/bytecode는 제외했고 원본 프로젝트 바이트도 불변이었다. 임시 `fef-storage-red.json`, `fef-storage-targeted.json`, `fef-storage-full.json`에 근거를 보존했다. 이 해시는 이후 보고서·이력 갱신 전 스냅샷에 해당한다. 커밋·푸시는 하지 않았다.

후속 code-change-reviewer는 같은 프로젝트 정의·claude-sonnet-5·Read/Grep/Glob으로 성공한 단일 리뷰를 완료했다(exit0/9턴/323.989초). 검토 diff SHA-256은 `d1e4a6038159f7c14112d8633d845df020d1b65b2d2644177ea36ad206ded95d`이며 결과는 임시 `fef-storage-review.json`에 보존했다. Critical/Major 없음; minor 주석 표현은 이후 명확히 했고 생성본에도 반영했다. 저장 성공 후 정리만 실패해도 표식이 남아 차단하는 동작은 안전한 보수적 처리로 유지했다. 별도 cleanup 진단 태그 추가는 선택 제안이며 이번에 도입하지 않았다. 부모 디렉터리 자체 생성 불가·루트 조회 실패·동시 writer 한계는 미해결로 명시했다.

Windows의 기존 민감 정보 비노출 진단2개도 다시 실행해 통과했다. 마지막 전체 회귀 이후 동작 변경은 없고 주석·검증 기록·이력만 갱신했다. Windows 전체 suite 재실행이나 현재 변경의 원격 CI 실행을 수행했다고 표현하지 않는다.

### Windows 전체 회귀 및 누적 코드·문서·생성본 최종 리뷰

사용자 요청에 따라 앞 절의 Windows 전체 미검증을 보완했다. 실행 중 프로젝트 파일을 수정하지 않았고 기본 PATH/Git·권한·보안 설정을 유지했다. 아래 결과는 Python3.14.4의 Windows 실제 실행이며, 앞 절 Linux/Windows 대상 실행의 대체·합산 결과가 아니다.

| 명령 | 실제 결과 |
|---|---|
| `python -X utf8 -m unittest discover -s tests -v` | 207실행/205통과/2권한skip, 1584.776초, exit0 |
| `python -X utf8 -m unittest discover -s scripts/delegation -p test_*.py -v` | 49실행/47통과/2권한skip, 47.649초, exit0 |
| `python scripts/validate_repository.py` | exit0, routes10/Kernel/Golden31 인덱스 확인; 모델 실행 아님 |
| `python scripts/build_plugin.py --check` | exit0, 생성 배포본101파일 동기화 |
| `git diff --check` | exit0, 공백 오류 없음 |

합계는 **256실행/252통과/4skip/실패·오류0**이다. 실제 Windows 파일 잠금, 최초 저장 실패와 복구, 서브모듈 ignore-all, Windows junction 및 short-path 사례가 전체 실행에서 통과했다. 건너뛴 사례는 다음과 같으며, symlink 생성 권한 부재(WinError1314 또는 symlinks unavailable)가 이유다. 권한·Developer Mode·보안 설정을 바꿔 통과를 만들지 않았다.

- `test_installed_symlink_cannot_reference_external_file`
- `test_source_directory_symlink_is_refused`
- `test_parent_and_nested_symlinks_refused`
- `test_symlink_destination_refused`

기준 HEAD는 `edd862cd09821a6c636197a15ca1db9d6f64ce6b`다. 프로젝트452파일의 전후 집합·바이트는 같고 변경경로는 없었다. manifest SHA-256은 `faa1387f21f7852122be259165207c37ba8a427e4a1f286b7dbc6ac3ec5a34ef`이다. Git-visible 프로젝트 파일 기준이며 mutable Git metadata/bytecode는 제외한다. 원본 결과와 개별 로그는 임시 `fef-windows-full-cvpehfqn/report.json` 및 `0.log`–`4.log`에 보존했다. 이 무변경 판정은 이후 보고서·이력 갱신 전까지의 검증이다.

최종 리뷰 범위는 미커밋14파일: canonical 코드4파일, 회귀테스트1파일(누적11개 추가), 사용안내1파일, 진행/세션/검증기록3파일, 생성본5파일이다. 전체 diff의 외부 전송은 최초 자동 승인 거절 후 사용자가 명시적으로 승인했다. 같은 프로젝트 code-change-reviewer 정의·claude-sonnet-5·Read/Grep/Glob으로 성공한 최종 단일 리뷰를 수행했다(exit0/22턴/352.219초). 별도 읽기 전용 문서 검토도 완료했다. 판정은 **Approve, Critical/Major 없음**이며 추가 제품 코드 수정은 필요하지 않았다.

리뷰 diff SHA-256은 `6df73b13d344c85ce97f518a513787fb5d50981aa1329e5b50b773c5e291c865`이며 임시 `fef-cumulative-review.json`에 결과를 보존했다. 리뷰어의 생성 wrapper hunk 누락 가능성은 동일 SHA의 실제 diff에서 해당 파일의2개hunk와 `2 additions/2 deletions`를 확인해 오탐으로 판단했다. 생성본 전체5파일도 목록에 있었으며 과거의 특정 generator 실행에서4파일 업데이트됐다는 이력은 그 시점의 기록이다. `shortcut` 주석 표현과 CreateFileW 오류 진단 보완은 차단 결함이 아닌 선택 제안으로 두었다.

Claude CLI의 `plugin validate .`와 `plugin validate ./plugins/fef-engineering`도 각각exit0이었다. 루트는 clone 설치 호환을 위한 CLAUDE.md가 plugin context로 자동 로드되지 않는다는 기존 경고를 유지한다. Kernel 전달은 별도 SessionStart 훅의 역할이다. 두 경로 모두 catalog용 `ICON_MISSING` 권고가 추가로 표시됐으며, CLI 출력은 이 directory 권고가 validation 결과를 바꾸지 않는다고 명시한다. 카탈로그 제출용 아이콘은 이번 기능 수정 범위에서 만들지 않았다. 이 CLI 검사는 카탈로그의 전체 안전 스캔·정책 심사를 대신하지 않는다.

남은 제한: 현재 Windows 권한에서 위 symlink4개 미실행, 다른 Python 버전/현재 미커밋 트리의 원격CI 미실행, 과거15초 timeout 원인 미확정, 전체 쓰기 불가·루트조회 실패·동시 writer 원자성 미보장. marketplace 캐시 모델 세션·실제 업무 전체·유효 ablation·추가 재배포 허가도 기존 범위를 넘겨 주장하지 않는다. 기존 LICENSE·고지를 보존했고 커밋·푸시는 하지 않았다. 전체 실행 이후의 갱신은 이 검증 기록과 두 이력 파일뿐이다.
