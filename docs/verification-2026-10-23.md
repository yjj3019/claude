# 격리된 실제 Claude 세션·효능 검증 — 2026-10-23

기준 커밋 `45de11e2dbe8548f2542fb677b023286592bda85`, Claude Code 2.1.308, 요청·실제 응답 모델 `claude-sonnet-5-5`, effort `medium`이다. 실제 first-party 로그인으로 새 세션을 호출했다. [구조화 증거](verification-2026-10-23.json)에 실행별 점수·사용량·패치·최종 응답·실패를 기록했다. 과거 기록은 보존한다.

## 격리 설치·실행

배포본101파일을 임시 폴더에 복사해 `--plugin-dir`로 세션에만 로드했다. `--restricted`, `dontAsk`, `--permission-prompts none`, `--no-session-persistence`, `--strict-mcp-config`를 사용했다. 명시 설정은 `autoMemoryEnabled:false`, `claudeMdExcludes:["**"]`, `blockReadsOutsideWorkingDirectories:true`이며 모델에는 합성 자료만 제공했다. 인증값은 읽거나 복사하지 않았다. 제품453파일과 사용자 `settings.json`·`CLAUDE.md`는 실험 전후 동일했다. 모든 사용자 런타임 파일의 불변성 보장은 아니다.

| 실제 네이티브 확인 | 소요(초) | 관찰 |
|---|---:|---|
| 컨텍스트·스킬 발견 | 61.887 | SessionStart Kernel 전달, 플러그인·스킬 목록 확인. 이 실행만으로 Skill 호출은 주장하지 않음 |
| 검증 없는 상태 변경 | 60.156 | 하네스가 SessionStart 뒤 비실행 텍스트 변경; 실제 Stop block 응답 |
| 검증 래퍼 성공 | 75.836 | 실제 fef-coding 호출·본문 전달, 신뢰된 산술 unittest2개 성공, returncode0·현재 snapshot 일치·Stop 허용 |

Stop은 반복 차단하지 않는 알림이며 보안 격리·정확성 보증이 아니다. 양성 검증 코드는 하네스가 작성했고 모델에 편집 도구를 주지 않았다. 전역·marketplace·운영 서비스 배포는 하지 않았다.

## 실제 모델 비교

각 과제 baseline/FEF 각5회, fresh workspace, AB/BA 교대, 같은 모델·effort·도구 설정이다. FEF는 플러그인·명시적 스킬·워크플로우 지시의 묶음 비교다. 내장 CLI 플러그인은 공통이며 캐시·부하·순서 효과는 남는다. SD는 표본 표준편차, 비용은 CLI list-price 추정 USD이며 구독 청구액과 다르다.

| 과제 | Variant | N | 평균/100 | SD | 평균 초 | 평균 추정 USD |
|---|---|---:|---:|---:|---:|---:|
| GT012 | baseline | 5 | 100.0 | 0.000 | 40.262 | 0.044809 |
| GT012 | FEF | 5 | 98.6 | 3.130 | 90.673 | 0.072117 |
| 합성 RCA | baseline | 5 | 97.6 | 1.517 | 19.951 | 0.032369 |
| 합성 RCA | FEF | 5 | 97.6 | 3.130 | 41.355 | 0.045303 |

GT012 공유 `money.py` 수정과 독립 unittest6개는 양쪽5/5회 통과했다. 테스트 파일·FEF 복사본은 불변이다. 기계 cap100을 총점으로 취급하지 않고 [rubric](../tests/GoldenTest-012.md)으로 별도 채점했다. 한 FEF 최종 답변에 sibling 설명이 없어7점 감점했지만 두 호출부 Read·테스트 통과는 관찰됐다. 중간 assistant 서술은 수집하지 않아 이전 설명은 복구할 수 없다. 부분 점수는 평가자 판단이다. 감점을 없애도 양쪽 SD0으로 엄격한 lower-SD 기준을 만족하지 못한다. **FEF 우위·Golden PASS는 입증하지 못했다.** [실행별 결과](../tests/results/GT012-20261023.md).

FEF5회 모두 직접 unittest 성공이 상태 기록에는 `returncode:null`로 남아 Stop 알림 후 재검증했다. 실험의 유일한 허용 명령은 `python -m unittest discover -s tests/fixtures/GT012-code -v`여서 권장 래퍼는 허용되지 않았다. 최종 Stop 허용을 성공 기록으로 해석하지 않았다. 별도 네이티브 래퍼 검증은 성공했다. 추가 시간·비용에는 명령 제한·알림의 영향이 포함된다. baseline2회·FEF2회에서 추가 명령의 권한 거절도 기록됐다. 일부 패치는 fixture 밖 숫자형·공백 입력 호환성이 다를 수 있으며 제품 코드에는 반영하지 않았다.

RCA는 새 보조 과제이며 GT011·공식 Golden이 아니다. HTTP8081/healthcheck8080 설정,8081 정상응답 뒤8080 연결 거절2회·healthcheck 실패 재시작, 증거 없는 OOM 추측을 제공했다. 요구사항은 API listener와 healthcheck 일치다. 사전 rubric은 원인20/근거20/요구 일치 수정10/미실행을 구분한 검증계획20/불확실성·OOM20/읽기전용10이다. 양쪽 모두 포트 불일치를 찾고 미실행 조치를 완료했다고 주장하지 않았다. 과거200 응답으로 나중에도 정상이었다고 단정한 표현 등을 감점했다. 입력 바이트는 모두 유지됐고 Read·Skill만 허용해 코드·외부 채점기를 실행하지 않았다.

독립 luna_explorer에 라벨 숨김 출력·패치·검증 증거를 전달하고 메인이 원본을 대조했다. 응답의 hook·스킬 언급으로 완전한 블라인드는 아니다. 두 합성 과제·한 모델·수동 평가·표본5회로 실제 업무 전체, Mods 채택, 절감률·품질 보장을 주장하지 않는다. 이번 표본은 품질 우위를 보이지 않았고 FEF 시간이 길며 추정 비용도 더 들었다.

## 실패·승인·남은 한계

GT012 파일럿2개 뒤 수집기가 문자열 message 처리에서 실패했다. 타입 검사·self-check 후 본 실험10회를 새로 실행했고 파일럿은 별도 보존·제외했다. RCA 최초1회는 Windows 줄바꿈 변환을 입력 변경으로 오판했다. 정규화 해시 동일을 확인한 뒤 정확한 UTF-8 바이트 작성으로10회를 재실행했다. 제품·모델 실패로 집계하지 않는다. 기록 생성 스크립트 최초 구문 오류와 문서 patch 문맥 오류는 대상 쓰기 전 실패했고 수정했다.

Python 채점기는 OS sandbox가 아니다. 자동 승인 검토가 암묵적 승인을 거절한 뒤 사용자가 합성 GT012 각5회 임시 폴더 호스트 실행 위험을 명시 승인했다. 그 범위에서 본 실험을 실행했다. Podman info는60초에 응답하지 않아 컨테이너 격리를 확인하지 못했으며 보안 설정을 완화하지 않았다.

제3자 재배포 권한은 여전히 미확정이다. DelegationLoop 조회는 다시404였고 원본 가이드에서 별도 공개 재배포 허락을 확인하지 못했다. 비공개·삭제 여부나 모든 권리자 관계는 확정할 수 없다. FEF 자체 MIT는 [감사 문서](license-audit-2026-10-22.md)·현행 LICENSE 범위만 따른다. 실행 성공은 재배포 허락이 아니다.

제품·설정·생성 배포본 변경 없이 기록만 추가했다. 기록 추가 후 repository validator·배포본101파일 동기화·diff 공백 검사는 exit0이었다. JSON 파싱·20회 모델/점수/보호 파일/통계 assert·신규 로컬 링크·제한적 비밀정보/개인 경로 검사도 통과했다. 이중 이스케이프 경로1건은 제거 후 재검증했다. 기존453파일 중 이력 PROGRESS.md 외에는 동일하다. PowerShell 초기 드라이브 메시지와 Git의 LF→CRLF 안내는 명령 실패로 이어지지 않았다.

이번 전체 소프트웨어 회귀·새 원격CI는 재실행하지 않았다. Windows symlink 권한, 간헐 Git 지연 근본 원인, 전체 저장 불가·동시 writer, 다른 모델·장기 안정성·실제 운영 부하는 미검증이다. 커밋·푸시 없음.

근거: [공식 CLI](https://code.claude.com/docs/en/cli-reference), [공식 메모리 설정](https://code.claude.com/docs/en/memory), [원본 가이드](https://sdk-kim-builds.com/guides/ai-delegation-loop-playbook/), [원본 저장소 조회 대상](https://github.com/yjj3019/DelegationLoop). CLI 제한은 외부 grader의 OS 격리를 의미하지 않는다.
