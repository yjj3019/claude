# 2026-10-24 Windows 사용자 운영 배포

## 배포 상태

- 사용자 승인 범위: 이 Windows 계정의 Claude Code 사용자 범위, 권리 미확정 자료 제외, 원본 보존.
- 소스 커밋: `77f447e9bb673fc4bd68f6bea1b3559964004ddf`. 로컬 배포 버전: `1.3.2-local.20261024`.
- 운영 ID: `fef-engineering@fef-marketplace`, user/enabled. 기존 `fef-engineering@synced` 1.3.1은 공식 CLI로 비활성화했으며 파일·저장 데이터는 삭제하지 않았다. 실행 중이던 기존 세션은 강제로 종료하지 않았다. 적용 확인에는 새 세션을 사용했다.
- 고정 로컬 marketplace: `%USERPROFILE%/.claude/local-marketplaces/taskforge-restricted-77f447e-20261024`. GitHub marketplace를 새로 배포하거나 원격 버전·태그를 변경하지 않았다.
- 원본 generated payload 101파일은 보존했다. 운영 사본에서 `skills/ai-delegation-loop/` 14파일을 제외해87파일로 만들고, manifest의 로컬 버전과 README/ClaudeCode/Installation의 배포 범위 안내만 바꿨다. `/fef-engineering:ai-delegation-loop`는 제공하지 않는다. 기본 coding/RCA 호출·리뷰어·훅·state v1은 유지했다.
- 설치 전후87파일 해시 일치. SHA256 맵의 정렬 JSON aggregate: `c76b0543f96f79f5d3c1eaadf282f571b5f6772f327bbbcfd362909139f7a1c2`. 실행 후 만들어진 Python bytecode2파일은 원본 배포87파일과 별도로 구분했다. 고정 원본87파일의 해시는 그대로다.

## Windows Git 진단과 운영 완화

- 정상 호출 Trace2 3쌍 비교에서 기본 wrapper는 전체4.107~5.184초, Git 내부 exit0.142~0.178초였다. 명시 Git은 전체1.815~2.521초였다. 여섯 호출 모두 exit0/출력일치였다. 이는 지연 구간을 좁히는 표본이며 실패 당시 OS 원인·보안 제품·wrapper의 책임을 확정하지 않는다. 이번 표본에서는15초 timeout이 재현되지 않았다.
- 기존 지원 설정인 사용자 `settings.json`의 `env.FEF_GIT_EXECUTABLE`을 `C:\Program Files\Git\mingw64\bin\git.exe`로 명시했다. 다른 env·설정 키는 보존했다. 전역 PATH·보안 설정·15초 timeout·자동 fallback·재시도·검증 판정은 바꾸지 않았다. 기본 PATH 모드의 근본 해결이나 향후 timeout 부재는 보장하지 않는다.
- 명시 Git 환경의 관련 회귀: `GitExecutableTest`8개와 기존 실패2개, 합계10/10통과·exit0·123.992초. 원문 요약 `Ran 10 tests in 123.992s` / `OK`. 최종 실행 직전 자식 환경 설정 invocation을 확인했으며 그 실행의 별도 원시 로그 파일은 저장하지 못했다. 전체 회귀 재실행 결과로 표현하지 않는다.
- 설치된 실제 경로에서 SessionStart → 수정 → 검증 래퍼 → 기록 → Stop 허용 → 재수정 → Stop 차단을 확인했다.5개 호출 모두 exit0, 훅 stderr0바이트, 래퍼의 stderr137바이트는 정상 unittest 1개 통과 출력이었다.
- 최초 검사에서 자식 Python을 절대 경로로 넣어 기존 runner 인식 범위를 벗어났다. 실제 테스트는 통과했지만 verification returncode가 null로 남아 Stop이 차단됐다. 원문은 보존했으며 문서의 `python -m unittest` 형식으로 다시 검사해 통과했다. 인식 범위를 넓히거나 차단을 우회하지 않았다.

## 새 실제 모델 세션

- Claude Code의 사용자 설정을 읽는 새 세션에서 `claude-sonnet-5-5`/medium, 도구 사용 없는 합성 응답 검사를 수행했다. 프로세스 exit0, is_error=false,85.842초, 응답 `TASKFORGE_DEPLOYMENT_SMOKE_OK`.
- 실제 init 이벤트에서 운영 플러그인1개·위 로컬 버전/경로, `fef-engineering:fef-coding`과 `fef-engineering:fef-rca`를 확인했다. 미확정 위임 스킬은 discovery 목록에 없었다. Kernel의 hook 응답과 관측된 hook_response3개의 success/exit0을 확인했다. 다른 기존 플러그인도 로드됐으므로 전체 hook 이벤트 수를 FEF 중복 수로 해석하지 않는다.
- 이 새 세션의 부모 shell에서는 FEF 환경변수를 제거했다. 사용자 env 설정을 읽은 뒤 Trace2에서 FEF 형태의 repository/status/HEAD/index 호출8개가 명시 Git 절대 경로로 실행되는 것을 확인했다. 별도 host version 조회1개도 같은 경로였으며 FEF8개와 구분했다.
- 사용자 설정 외에 세션 전용 autoMemoryEnabled=false/claudeMdExcludes를 사용했고, 도구를 비활성화했다. 한 번의 합성 로딩·응답 검증이며 일반 제품 효능·모든 프로젝트·장기 안정성의 증거가 아니다. 누적 diff·제품 소스를 독립 리뷰용 외부 Claude에 전송하지 않았다.

## 권리 경계

- 권리 미확정 DelegationLoop, 외부 가이드의 프롬프트와 원본 이력·설치기는 이번 운영물에 포함하지 않았다. 알려진 원문 URL/프롬프트 식별자 검사 후보0건, 이력 디렉터리·제외 스킬 부재를 확인했다. 최초 텍스트 검사는 실행 중 생긴 .pyc까지 읽다 인코딩 오류가 났고, 원본87파일 명세로 범위를 고정해 재검사했다.
- 제3자 허가를 새로 확보하거나 MIT를 부여한 것은 아니다. 원본 저장소와 별도 위임 installer는 그대로 남아 있으며 이번 배포에 사용하지 않았다. 남은87파일의 모든 문장을 원문과 대조한 법적 권리 확인도 아니다. 기존 LICENSE의 자체 저작분 한정·제3자 제외·고지 경계를 유지하고 패키지 전체 MIT를 주장하지 않는다.
- 원본 DelegationLoop GitHub 조회는404여서 새 LICENSE 유무를 확인할 수 없었다. 원문 가이드 페이지의 라이선스·재배포 명시도 찾지 못했으며 이는 부재의 법적 증명은 아니다. 공개 코드라는 사실만으로 별도 재배포 허가가 생기는 것은 아니라는 [GitHub 라이선스 안내](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)를 적용해 미확정 자료는 배포에서 제외했다.
- 혼합 원본·독립 위임 ZIP의 더 넓은 배포에는 해당 권리자의 범위·조건이 확인되는 허가 또는 명시 라이선스가 여전히 필요하다. 권리자에게 외부 연락은 하지 않았다.

## 백업과 복구

- 설정·플러그인 등록부 사전 백업은 `%USERPROFILE%/.claude/taskforge-deployment-backups/20261023T214824Z/`에 있다. 인증정보를 응답·저장소·보고서로 내보내지 않았다. 다른 설정 변경이 있으면 백업 전체를 덮어쓰지 말고 해당 플러그인과 FEF env 키만 선택 복구한다.
- 신규 운영본을 되돌릴 때 공식 CLI로 `claude plugin disable fef-engineering@fef-marketplace --scope user`, 기존 복사본은 `claude plugin enable fef-engineering@synced --scope user`로 복원하고 새 세션에서 상태를 확인한다. 이전 FEF env 키가 있었는지는 비공개 설정 백업에서 확인해 선택 복원한다. 기존 plugin data를 삭제하는 uninstall은 쓰지 않는다. 이 복구 절차 자체는 실행 시험하지 않았다.
- 실제 [플러그인 설치·등록 방식](https://code.claude.com/docs/en/plugin-marketplaces)과 [사용자 설정 우선순위](https://code.claude.com/docs/en/settings)를 따랐다. 더 높은 우선순위의 프로젝트/관리 설정이 FEF env를 바꾸면 별도 확인이 필요하다. 기존 실행 세션은 다시 시작해야 새 설정을 적용할 수 있다.

## 검증 한계와 증거

- 공식 CLI strict plugin/marketplace 검증 success, manifest errors/warnings0. 배포 디렉터리 제출용 참고 진단에는 아이콘 없음과 README 설치 한 줄 권고가 남았으며 로컬 설치 차단 사항은 아니었다. 공개 디렉터리 제출은 하지 않았다.
- 기본 설정 전체 회귀의 기존265통과/4skip/2실패를 지우지 않았다. 이번 전체 Windows 회귀·다른 호스트·OS 프로세스 추적은 하지 않았다. 최신 원격CI는 소스77f447e에 대한 이전 성공이며 이 로컬 변형 배포본의 CI로 주장하지 않는다.
- checkout 옆 `validation-20261024-deployment/`에 release-manifest.json, deployment-state.json, git-trace-summary.json, installed-hook-report.json, actual-user-session-report.json, actual-user-session-verified.json, restricted-content-check.json 및 해당 원시 로그를 보존했다. 비공개 설정 백업은 이 디렉터리에 복사하지 않았다.
- 이번 제품 소스 수정·커밋·푸시 없음. 배포 후 이 문서와 PROGRESS 마감 기록만 추가했다.

## 후속 소스 변경과 WPR 검증 — 운영본 갱신 보류

앞선 설치 기록은 `1.3.2-local.20261024`에 대한 결과다. 이후 소스/생성본은
`2.0.0`과 코어 스킬 버전 `1.0.0`으로 준비했지만, 사용자 설치본을 갱신하지 않았다.
신규 배포 차단과 권리 확정 절차는 [권리 확인 절차](third-party-clearance.md),
버전 범위는 [스킬 버전](skill-versions.md)에 있다. 원본·기존 설치 데이터는 보존했다.

명시 Git 설정의 전체 Windows unittest는 main224개 중218통과/2FAIL/2ERROR/2skip,
delegation53개 중51통과/2skip였다. 신규 문서2개가 빠진 테스트 기대 목록을 수정한 뒤
설치기72개 중70통과/2skip, 시간 초과3건 재검증은3/3통과했다. repository/payload89/
위임 validator/evidence/history/diff 검사는 모두 exit0이다. 최초 전체 실패를 후속 통과로
대체하지 않으며, Windows의 안정적인 전체 통과는 여전히 확인되지 않았다.

위험을 설명한 뒤 명시 승인을 받아 관리자 WPR 전용 세션을 약1분 실행했다.
정상 종료/수집68초/유실 이벤트0, 원본 ETL과 로컬 tracerpt 요약은 checkout 옆
`validation-20261024-release-gate/wpr-local/`에 보존했고 외부 전송하지 않았다.
Git wrapper/직접 실행 각각4회가 모두 성공했다. 호출 전체 중앙값2.3297초/1.3317초,
Git 내부0.101038–0.177794초는 이 표본의 관측치이며 일반 성능 보장이 아니다.
15초 실패는 재현되지 않았고 OS 원인·CPU 스택 귀속은 미확정이다. WPA 스택 분석이나
보안 정책 변경은 하지 않았다.

전체 테스트 중 저장소454파일·HEAD·사용자 CLAUDE.md는 동일했으나 사용자 settings.json
해시는 달라졌다. 변경 주체를 확인할 수 없어 복원하지 않았고 FEF 관련 설정3개는 유지됐다.
후속 테스트 동안에는 settings 해시도 동일했다. 이 마감 문서와 테스트 기대 목록은 전체
실행 이후 보완했으며, 새 버전의 실제 모델 세션·운영 적용·원격CI·커밋·푸시는 하지 않았다.
