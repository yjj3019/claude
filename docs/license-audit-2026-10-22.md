# 라이선스·출처 감사 — 2026-10-22

## 결론과 적용 상태

기준 커밋은 `11201b6859a06906237cf2b86b682cfca6d0a7d2`다. 감사 시작 시 루트와 생성본 `LICENSE`는 5행 MIT 자리표시자였다. 이후 사용자가 **`yjj3019` 명의 FEF 자체 저작분에 MIT를 부여할 권한이 있음**을 명시 확인했다. 이에 기존 저작권 표시를 유지해 표준 MIT 전문과 적용 범위를 완성했다.

MIT 허가는 권한을 보유한 FEF 자체 저작분에만 적용한다. DelegationLoop 관련 세 경로(`skills/ai-delegation-loop/`, `scripts/delegation/`, `docs/delegation-loop/`), 외부 인용·원문·과거 기록 및 대응 생성 복제본은 제외한다. 추가 허락 자료가 없다는 이전 답변을 제3자 허락으로 확대하지 않는다. 아래 `NOASSERTION`은 제외 자료의 라이선스를 확정하지 못했다는 감사 판정이며 새 라이선스·사용 금지 계약·SPDX 소스 헤더가 아니다.

## 범위별 판정

| 범위 | 확인한 출처·적용 근거 | 현재 판정 및 후속 조치 |
| --- | --- | --- |
| FEF Kernel, 정책, 모듈, 도메인, 워크플로, 리뷰어, 설정, 자체 훅·도구·스킬 | 현 저장소 파일과 제한된 Git 이력. 작성자·manifest owner 표시는 권리 양도 증거가 아님 | 사용자가 허가 권한을 확인한 자체 저작분은 MIT. 외부 유래 부분과 열거한 경로 예외는 제외 |
| FEF 문서, 예제, 테스트와 fixture | 현 파일·import·출처 표기 조사. 모든 표현과 fixture의 독립 창작 여부까지 입증하지는 못함 | 권한을 보유한 자체 저작분은 MIT. 외부 인용·기록의 권리는 부여하지 않으며 식별되지 않은 제3자 부분의 권리는 미확정 |
| `skills/ai-delegation-loop/` | 원본 main `1e35bf0a6d16bac0c6e1dccda1014a1e78b7bb96`, 최적화 커밋 `01351414e10df3c177939e4fef8393609ece6c55`. 통합 manifest의 원본 18파일 중 8개 unchanged, 10개 modified | 원본 LICENSE 없음. `NOASSERTION`. 수정했다는 이유만으로 원본 표현의 MIT 재허가 불가 |
| `scripts/delegation/`, `docs/delegation-loop/` | 통합·설치·검증 도구와 출처 기록. 원본·가이드와 결합된 범위 | 파일별 자체 저작 권한과 원본 이용 근거를 분리해야 함. 보수적으로 `NOASSERTION` 유지 |
| DelegationLoop 가이드 기반 프롬프트·매뉴얼 | 낭만빌더 김스듴의 아래 가이드. 복사·사용 안내와 포괄적인 수정·공개 재배포 허락은 구분 | 공개 재배포 허락을 확인하지 못함. 출처 표시만으로 해결되지 않음 |
| `docs/delegation-loop/source-history/` 및 보존된 v1.2 결과 | Git 번들, PR 본문·대화·리뷰 JSON, 작성자별 기록, 모델 실행 결과 | `NOASSERTION`. 과거 기록의 바이트·저작자·날짜 보존. 일괄 MIT 표기 또는 소급 변경 금지 |
| `plugins/fef-engineering/` | `scripts/build_plugin.py`가 생성하는 101파일. 자체 소스와 위 DelegationLoop 내용이 함께 포함됨 | 원본별 판정을 그대로 따르는 혼합 배포본. 자체 FEF에 MIT를 부여했지만 패키지 전체 MIT라고 표시할 수 없음 |
| `.github/`와 외부 실행 도구 | GitHub Actions 참조, Python/Git, 모델 CLI. 별도 실행 환경의 구성 요소 | 참조와 도구 호출은 해당 코드의 저장소 내 복제와 구분. 외부 도구 약관·라이선스는 별도 적용 |

예외 경로에 해당하지 않는다는 사실만으로 나머지 파일의 권리 보유가 입증되는 것은 아니다. 사용자의 권한 확인 후에도 자체 저작분에 대한 허락과 제3자 원문·인용의 권리를 분리해야 한다.

## 조사 근거와 완전성 한계

- `git ls-files`의 452개 추적 파일을 열거하고 바이트를 읽어 SHA-256, NUL 포함 파일, Python 구문·import를 확인했다. Python 구문 분석 오류는 없었다. 이는 파일 전체에 대한 기계 조사이며 452파일의 문장별 원저자 대조를 뜻하지 않는다.
- 경로별 수: 루트13, `.claude`9, `.claude-plugin`2, `.github`3, `config`3, `docs`34, `domains`9, `examples`4, `hooks`1, `kernel`3, `modules`11, `plugins`101, `policies`9, `reviewers`8, `scripts`28, `skills`25, `tests`182, `workflows`7. Git index에 symlink·gitlink는 없었다.
- 조사 manifest의 SHA-256은 `d0fe5fb29ad9de9c241437813c8eb32589dda169f96c8442bd8456bb2254580b`이다. 계산은 Git 순서의 각 파일에 대해 `경로 + NUL + 파일 SHA-256`을 만들고 LF로 연결한 UTF-8 바이트를 해시했다. 이 문서를 추가하기 전 기준이며 보관 번들 내부 객체를 개별 파일 수에 더하지 않았다.
- 유일한 NUL 포함 파일은 추적된 `docs/delegation-loop/source-history/DelegationLoop.bundle`이다. 실제 크기 68,724바이트, SHA-256 `bba18c87965baa407d1fcf9f51d3f0b0f8a60fcbc010dd4cb449d5d50a1437d4`로 기존 기록과 일치했다. 확장자만으로 바이너리를 판정하지 않았다. 번들 헤드는 manifest와 비교했으며 이번 감사에서 객체를 새로 추출하거나 과거 라이선스 검색을 재실행하지 않았다.
- 기존 `THIRD_PARTY_NOTICES.md`, 통합·출처 manifest, PR 보관 범위와 기존 권리 감사 기록을 검토했다. 가이드 원문과 파생 파일의 문장별 동일성·권리자별 별도 계약은 검증하지 못했다. GitHub의 공개 저장소 조회·fork 가능성은 별도 공개 재배포 허락으로 간주하지 않았다.
- 수정 전 원격 GitHub license API는 루트 파일을 `Other` / `NOASSERTION`으로 반환했다. 이는 자동 식별 결과이며 법적 권한 판정이 아니다. 원본 `yjj3019/DelegationLoop` API는 404로 접근할 수 없었다. 삭제·비공개 여부나 이후 허락 변경은 확정할 수 없다. 현 로컬 이력도 shallow이므로 저장소 전체 역사에 대한 독립 재감사는 아니다.
- 패키지 manifest·lockfile 형태의 Python 의존성 선언이나 vendored 라이브러리는 확인하지 못했다. import에는 표준 라이브러리·저장소 내부 모듈 외에 `scripts/delegation/validate_skill.py`의 선택적 `yaml` 교차 검사와 `scripts/delegation/test_scripts.py`의 선택적 PyYAML 교차 검사 테스트가 있다. 미설치 시 런타임 교차 검사는 생략되고 해당 테스트는 skip된다. 이는 PyYAML의 소스를 함께 배포한다는 뜻이 아니며, 설치 환경에 있을 때만 사용하는 외부 의존성이다. 모든 import를 표준 라이브러리라고 단정하지 않는다.

## 권한 확인 후 적용한 변경과 남은 조치

1. 확인된 권한에 따라 기존 `Copyright (c) 2026 yjj3019`와 MIT 전문을 적용하고, 원본·생성본의 적용 범위와 제3자 예외를 LICENSE 내부에 명시했다. README·현행 고지·Claude Code 안내도 같은 경계로 정리했다.
2. DelegationLoop·외부 가이드·과거 기록은 현재의 권리 미확정 고지를 유지한다. 공개 재배포가 필요하면 해당 권리자의 허락 또는 명시적 원본 라이선스를 확보한다. 제거·재작성으로 해결하려면 별도로 기능·출처·배포 영향 범위를 검토한다.
3. 생성기로 배포본을 동기화했다. 혼합 패키지의 plugin·marketplace에는 단일 MIT 식별자를 넣지 않는다. 과거 manifest·번들·검증 기록의 원본 바이트는 보존했다. 새 스킬 팩 설치와 명시적 `--force` 갱신에는 LICENSE를 포함하도록 복사 목록에 추가했다. manifest v1·기존 검증 필수 목록은 유지해 이전 설치의 무결성 검증을 보존하며 자동 덮어쓰기는 하지 않는다.
4. 라이선스는 코드 품질·CI 통과로 입증되지 않는다. 이번 변경은 설치 파일 선택 상수와 문구에 한정되며 설치 경로·저장 데이터·스킬 호출 계약을 변경하지 않고 커밋·푸시하지 않는다.

## 출처

- [GitHub: Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) — 라이선스가 없는 공개 저장소의 기본 권리와 라이선스 표시.
- [SPDX: MIT License](https://spdx.org/licenses/MIT.html) — 표준 MIT 전문과 조건.
- [REUSE FAQ](https://reuse.software/faq/)와 [REUSE Specification](https://reuse.software/spec/) — 파일별 실제 저작권·라이선스 정보의 구분. 본 감사는 REUSE 준수 인증이 아니다.
- [원본 AI 위임 루프 가이드](https://sdk-kim-builds.com/guides/ai-delegation-loop-playbook/) — 절차의 출처. 열람한 페이지에서 포괄적인 공개 재배포 라이선스를 찾지 못했다.
- [기존 권리 검증](verification-2026-10-21.md), [통합 및 보관 범위](delegation-loop/INTEGRATION.md), [제3자 고지](../skills/ai-delegation-loop/THIRD_PARTY_NOTICES.md).

## 이번 변경의 검증

- 저장소 validator, 생성 배포본 `--check`(101파일), `test_build_plugin.py` 8개 테스트, 기존 추적 변경의 `git diff --check`가 모두 통과했다. 테스트 출력의 의도적인 missing/extra/changed 메시지는 임시 fixture의 음성 테스트다.
- 위 8개 테스트는 최초 감사 문서 단계의 결과다. 이후 승인된 MIT 적용·설치 고지 보존 변경의 최종 검증은 아래에 별도로 기록한다. 실제 모델 세션·원격 CI는 재실행하지 않았으며 커밋·푸시하지 않는다.

- 승인 후 배포본 생성·8개 build-plugin 테스트 통과(59.483초), 제3자 패키지 validator·deterministic evidence `--check` 통과, 보관 source-history 모든 추적 파일의 바이트가 HEAD와 동일함을 확인했다.
- 최초 설치기 전체71개는 새 README의 standalone 로컬 고지 링크 때문에2개 실패했다. 원격 출처 링크로 교정 후 해당2개를 각각 다시 통과했다. 신규 LICENSE 복사/무결성·이전 v1 manifest 호환성 테스트2개도 통과했다. 기본 샌드박스의 임시 .codex 쓰기 제한으로 실패한 별도 실행은 제품 회귀 결과에서 제외한다. 허용된 실행 모드의 최종 설치기 전체 결과는 아래와 같다.

- 최종 Windows 설치기 회귀는 71개 실행/69개 통과/2개 skip/실패·오류0, 100.263초, exit0이었다. 추가한2개 회귀가 포함된다. 라이선스 메타데이터 회귀1개도 통과했다. 부모의 최종 제품 변경 후 build-plugin8개 통과와 합하면 세 검증군은80개 실행/78개 통과/2개 skip이다.
- 별도 runner의 기본 샌드박스 build-plugin 실행은 임시 트리 생성·정리 권한 오류로 실패했다(8개 실행,16errors). 부모의 허용된 실행 모드에서 통과한8개 결과와 구분하며, 기본 샌드박스 실패를 성공으로 표현하지 않는다.
- 최종 validator·배포본101파일 동기화·diff 공백 검사는 모두exit0. Git은 build_plugin.py의 향후 LF→CRLF 정규화 경고를 출력했으나 공백 오류는 없었고 Git 설정은 변경하지 않았다.
- 아키텍처/권리 경계 독립 검토와 최종 로컬 검토를 반영했다. 새 외부 모델로 diff를 전송하지 않았다. MIT 적용 직후 단계에는 전체 Windows 회귀·모델 실행·원격CI를 재실행하지 않았다. 후속 전체 회귀는 아래 최종 검증 절에 기록한다.

- Skip 사유 추가 확인: 설치기 symlink 회귀2개를 별도 실행해 파일·디렉터리 링크 생성이 모두 WinError1314(필요 권한 없음)로 skip됨을 확인했다. 권한 설정은 변경하지 않았다.


## 최종 리뷰·전체 회귀 — 커밋 전 기준

- 사용자 요청으로 누적17파일의 최종 로컬 리뷰, 전체 회귀, 문제 없을 때 커밋·정상 푸시와 해당 커밋 원격CI 확인이 승인됐다. 기존 절의 미커밋/전체 미실행 표시는 각 이전 단계의 기록이다.
- 최종 독립 로컬 리뷰와 메인 diff 검토에서 차단할 결함·권리 범위 모순·설치 호환성 문제를 찾지 못했다. MIT 권한은 사용자 확인을 근거로 FEF 자체 저작분에 한정하며 제3자 권리의 법적 완전성을 보증하지 않는다. 추가된 diff와 신규 감사 문서의 제한적 비밀정보 패턴 검사도 탐지0건이었다.
- Linux/Python3.12.3: main213실행/210통과/Windows전용3skip(12.273초), delegation49실행/48통과/Windows전용1skip(4.427초). 합계262실행/258통과/4skip/실패·오류0. 원본과 격리 복사본의 프로젝트453파일 전후 바이트 동일. 근거: Temp/fef-license-final-full.json.
- Windows/Python3.14.4: main213실행/211통과/2skip(1984.600초), delegation49실행/47통과/2skip(58.771초). 합계262실행/258통과/4skip/실패·오류0. Skip은 파일/디렉터리 symlink 생성 권한 제한이며 main2건은 실제 WinError1314를 기록했다. 파일 잠금·PowerShell wrapper·서브모듈 ignore 상태·최초 저장 실패 회귀도 통과했다.
- Windows validator·배포본101 동기화·diff 공백 검사 모두exit0. 프로젝트453파일의 목록·바이트 동일, changed_paths=[]이었다. 근거: Temp/fef-windows-full-4sblxs3a/report.json 및0.log~4.log. 최초 자동 승인 거절은 임시 하네스 전체와 쓰기 범위 안전성 확인 후 동일 명령 재요청이 승인돼 해소됐으며, 권한·보안·Git 설정 변경은 없었다.
- 테스트 중 제품·문서를 동결했고 완료 뒤 이 문서와 PROGRESS 기록만 갱신했다. 전체 실행은 실제 모델 품질·운영 설치·새 제3자 재배포 허락의 증명이 아니다. 제외 자료 권리 미확정, Windows symlink4개, 기존 간헐 Git 지연 원인·전체 저장 불가/동시 writer 한계는 유지한다. 새 릴리스·버전 변경·외부 모델 diff 전송은 하지 않는다.
- 위 결과는 커밋 전 작업트리 기준이다. 전달 커밋 해시와 그 커밋의 원격CI 결과는 최종 응답에서 보고한다.
