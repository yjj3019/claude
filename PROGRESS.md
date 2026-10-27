# Project Progress

## Recent (2026-10)

- **Live-model and redistribution verification (2026-10-21)**: Actual Claude Code 2.1.304 / first-party claude-sonnet-5 sessions observed Kernel delivery, native coding/RCA Skills and delegation interview startup against an unchanged 101-file session-only payload. Initial coding attempt was not verified due to scoped command/path denials; corrected invocation retained the same permissions. Coding later passed 3 fixture tests and independent replay, with one PostToolUse TimeoutExpired followed by actual Stop block feedback, model retry and matching verification/current snapshot. RCA/interview were read-only scoped fixtures, not business-workflow acceptance. No complete redistribution grant was located in current LICENSE/source notices/public guide; asked for ownership/permission evidence. See docs/verification-2026-10-21.md. User settings and product code unchanged; no commit or push.

- **Remote CI follow-up: canonical Windows test paths (2026-10-20)**: Delivered initial commit f8440d51efd703fa02839c7ff21a91557a8c5ee9 to main and verified clean local/remote equality. Its Linux CI matrix (Python 3.11/3.12/3.14) and delegation workflow passed; Windows 3.11/3.14 failed only the isolated-payload test expecting a raw 8.3 TEMP alias while the hook correctly returns a resolved long path. Reproduced that assertion locally under an actual short TEMP alias (1 failure in 8.148s), then resolved the expected installed/source paths in two assertions. Runtime and payload unchanged. Short-alias Windows builder 8/8 passed in 24.024s; Python 3.11 short-alias case 1/1 passed in 8.839s. Independent review found no P0-P2 issues. Prepared a normal follow-up commit/push; final CI outcome belongs to that exact commit/run. Existing licensing/live-session limitations and nonblocking action-runtime deprecation advisories remain.

- **Authorized main delivery validated (2026-10-20)**: User authorized commit/merge/push; local and fetched origin main share base 58ae7d8b5954195bea5238ff237acd99c2f1ad20, with no separate branch to merge. Final delivery covers 134 files after fixing native-payload LF checkout rules and byte-exact test restoration. New autocrlf regression reproduced 15-file drift before the fix. Final Linux full regression: 196 main (194 passed/2 Windows-only skips) plus 49 delegation (48 passed/1 Windows-only skip), 242 passed/3 skipped; repository validation passed and 447 files remained byte-identical before/after. Windows builder 8/8 and framework 3/3, Python 3.11 new checkout 1/1 and framework 3/3 passed. Staged EOF advisories in 8 generated copies are identical to canonical source blobs and preserved; no other whitespace errors. Existing licensing/live-session and historical unconfirmed-failure limitations remain. Actual commit/push outcome is recorded in Git/remote and the delivery response.

- **Resumed: Python floor and documentation-link coverage (2026-10-20)**: Python 3.11.15 compiled all 37 Python files under source/generated scripts in memory without errors. The selected generator/plugin-runtime/Golden-runner/hook regressions ran 27 tests in 285.475s with no failures/errors/skips, including the strengthened ignored-submodule case. Python 3.11 repository validation passed (101 payload files, 10 routes, Kernel and 31 Golden metadata). Read-only review of 98 scoped Markdown files found no broken targets among 65 inline local links, including 9 fragments; main rechecked fragment targets/headings. No product changes were needed. This is targeted floor coverage, not a full Python 3.11 suite or complete CI matrix; existing live-session, licensing, advisory and unexplained-failure limitations remain. No staging, commit or push.

- **Working-tree closeout (2026-10-20)**: Completed the authorized code, documentation, archive recovery, compatible plugin migration and generated-distribution work. Latest full verification: Windows 240 passed/4 skipped before the final test-only tightening; Linux hash-verified native snapshot 241 passed/3 Windows-only skips afterward, including the strengthened submodule regression. Repository/payload/diff checks passed. Preserve the intentional root CLAUDE.md advisory, unexplained earlier intermittent failure and first Linux validator failure, unresolved redistribution rights and untested live-model/full-matrix behavior as explicit limitations. All cumulative changes remain unstaged at HEAD 58ae7d8b5954195bea5238ff237acd99c2f1ad20; no commit or push. Further changes require a new user request.

- **Linux full regression on a verified native snapshot (2026-10-20)**: Ubuntu WSL 2 / Python 3.12.3: main 195 run in 9.186s (193 passed, 2 Windows-only skips), delegation 49 run in 3.806s (48 passed, 1 Windows-only skip); aggregate 244 run, 241 passed, 3 skipped, no failures/errors. The strengthened submodule ignore-all test passed in the full suite. The original /mnt/c attempt blocked in p9_client_rpc and produced no suite verdict; excluded it. Reran from a native /tmp copy after matching all 481 archived entries and HEAD. Repository validation initially exited 1 with an unavailable log; a fresh same-snapshot rerun passed all checks, so its first failure cause is unconfirmed. Runtime sources unchanged. Original intermittent failure, live-session coverage and redistribution rights remain unresolved. No staging, commit or push.

- **Fault rejection and Linux symlink coverage (2026-10-20)**: Injected a TimeoutExpired exception into the actual verification-record hook at the ignore-all transition; the strengthened test rejected its sanitized stderr with the expected assertion failure (one injected fault, no unexpected errors). This proves the test guard, not the cause of the earlier intermittent failure. Independent review found no new P0-P2 issues in the assertion/log delta. WSL access is now available: Ubuntu 24.04.3 LTS / Python 3.12.3 ran all four previously skipped real-symlink cases successfully in 5.364s, with zero skips. This supplements the Windows full run; it is not a Linux full-suite result. Redistribution rights, live paid-session behavior and the original intermittent cause remain unresolved. No staging, commit or push.

- **Observed full rerun passed; original cause unconfirmed (2026-10-20)**: Main 195 tests in 2301.363s: 193 passed, 2 Windows symlink skips, no failures/errors. Delegation 49 tests in 124.960s: 47 passed, 2 symlink skips. Aggregate: 240 passed, 4 skipped. The previously failing submodule test passed both in full-discovery isolation (145.681s) and the full rerun. Added stderr assertions to that test's successful record/stop transitions so fail-open hook errors cannot look like successful verification; the strengthened test passed separately in 218.144s. The full run preceded this test-only tightening; it was not repeated afterward. Runtime sources/timeouts unchanged. Payload/history/Golden/CLI checks passed; root compatibility advisory, original intermittent cause, live/cross-platform validation and licensing limits remain. No staging, commit or push.

- **Full regression failure (2026-10-19; recorded on resume 2026-10-20)**: Main suite: 195 run, 192 passed, 1 failed, 2 skipped in 2644.818s. Delegation: 49 run, 47 passed, 2 skipped in 147.914s. Aggregate: 239 passed, 1 failed, 4 Windows symlink-privilege skips. The submodule ignore-all test failed at tests/test_hooks.py:177 after recording verification; isolated rerun passed in 287.030s. Cause remains unconfirmed. Next: capture recording diagnostics and snapshot differences before changing behavior. Payload/history/Golden checks passed; no staging, commit or push.

- **License metadata consistency (2026-10-18)**: Removed unconfirmed MIT identifiers from native plugin/marketplace metadata; preserved LICENSE bytes and documented unresolved permissions in the usage guide and generated README. Regenerated 3 of 101 payload files. Targeted runtime/generator regression: 13 passed; repository and payload drift checks passed. Actual symlink tests remain limited by Windows privileges; WSL enumeration was denied. No commit or push.

- **Self-contained native distribution (2026-10-18)**: Added `scripts/build_plugin.py` and the generated 101-file `plugins/fef-engineering/` payload; marketplace now installs that directory at plugin version `1.3.1`. Root clone/standalone instructions and `--plugin-dir .` remain intact. Marketplace/payload validation is clean; root `validate .` intentionally retains its compatibility advisory. Fetched the existing origin `v1.2.0` tag, resolving repository tag validation without inventing a release. Full regression: 194 main + 49 delegation tests; 239 passed, 4 Windows symlink-privilege skips, no failures/errors. No commit or push.
- **Approved native plugin rename (2026-10-18)**: Renamed the plugin to `fef-engineering` and retained `fef-claude` in the marketplace `renames` map. Updated installation/migration guidance while preserving the standalone `fef-claude/` pack. Isolated Claude Code 2.1.302 CLI checks confirmed settings-key migration and preservation of an old-data marker; custom data migration and old skill aliases are not guaranteed. Full regression: 187 main + 49 delegation tests, 232 passed and 4 Windows symlink-privilege skips, no failures/errors. No commit or push.
- **Archive recovery and plugin diagnostics (2026-10-18)**: Restored the exact original `DelegationLoop.bundle` from integration commit `17dd9fc`, matching the existing manifest size/SHA-256. Offline history restoration and integrity checks passed. Removed the redundant marketplace version; retained plugin identity and root `CLAUDE.md` pending any separately approved compatibility migration. See `docs/delegation-loop/INTEGRATION.md` and `docs/ClaudeCode.md`.
- **Context and harness optimization (2026-10-09)**: Compacted CLAUDE.md core to ~69 lines / 3.9kB. Integrated Coding/Research procedures into modules. Session-scoped verification hooks. Full details: `docs/precise-analysis-2026-10-09.md`.
- **Native Skills + Plugin packaging (2026-10-15)**: Added `.claude-plugin/` manifest and marketplace, plus `skills/fef-coding/` and `skills/fef-rca/` for on-demand native Skills. Plugin install path documented in README.
- **Repository cleanup (2026-10-15)**: Historical simulation, review, ablation, and source-history files were archived or removed. See `docs/archive/README.md`; full prior content is available in Git history.

## Current Status

Product delivery complete as of 2026-10-22 06:33 KST: commit d0467e6f8af20d17f40d0246bc2d2c4e84010725 is on origin/main; both exact-commit CI workflows completed successfully (10/10 jobs). The closeout records are included in a separate documentation-only follow-up; the product verification and CI evidence above refer to d0467e6.

Validated changes: failed state saves persist a per-session marker that Stop checks before accepting an earlier pass or baseline. JSON v1 and one-shot behavior remain compatible. Windows full regression (Python 3.14.4): 256 run, 252 passed, 4 symlink-privilege skips, no failures/errors; native Linux full regression: 256 run, 252 passed, 4 Windows-only skips. Repository/101-file payload checks passed. Final cumulative independent review found no Critical/Major issues; no further product-code fix was needed. Root CLAUDE.md context and catalog ICON_MISSING advisories remain nonblocking. Git proxy startup overhead was measured, but the earlier 15-second timeout remains unexplained. Total storage failure, failed repository lookup and concurrent-writer atomicity remain unguaranteed. Prefer native Skills for ordinary coding/RCA tasks; use `scripts/detect_task.py` or loading map for complex multi-pack routes.

Earlier S4-08 hook-payload concerns now have actual Kernel delivery, wrapper/Stop feedback and regression evidence; the original acceptance criteria are unavailable in this checkout, so this does not close every historical criterion. Marketplace-cache model sessions and a valid isolated pack-ablation re-run remain unverified. Existing ablation results record instruction contamination and cannot support effectiveness or savings claims. See `docs/verification-2026-10-21.md` and `tests/results/pack-ablation/`.

For removed historical progress entries, consult Git history as described in `docs/archive/README.md`; `docs/archive/PROGRESS-full.md` is absent from this checkout.

## 2026-10-21 추가 검증 마감

- 보관 번들 모든 advertised refs/고유 5커밋과 FEF LICENSE 가시 이력·공개 원문을 확인했으나 재배포 허가는 미확정이다. 권리 자료는 사용자 답변 대기. 원격 전체 이력 조회는 DNS thread 오류로 미완료.
- Git snapshot 20회 중 19회 완료, repository lookup의 git rev-parse --show-toplevel에서 15.460초 TimeoutExpired 1회 재현. 시스템 지연 원인은 미확정.
- 추가 실제 모델 4세션: 자동 스킬 선택 확인; restricted 접근 거부와 최초 초안 frontmatter 누락 발견; 임시 plugin --add-dir 재시도에서 원문 읽기·교정 초안 형식 확인. 두 새 세션의 매뉴얼 읽기는 확인했지만 미승인 초안으로 업무 실행은 미완료.
- 구조 검증/생성 배포본 101파일 동기화 통과. 샌드박스 hook suite 40 tests/75 errors, 격리 해제 후 10개 통과 뒤 지연 중단: 전체 회귀 통과로 기록하지 않음.
- docs/verification-2026-10-21.md와 verification-followup-2026-10-21.json에 상세 증거·실패·제한 기록. 코드/라이선스 변경, 커밋·푸시 없음.
- 임시 감사용 복제본 삭제는 자동 승인 검토가 명시적 삭제 승인 부재로 거절해 보존. 우회 삭제 없음.

## 2026-10-21 후속 검증 완료 — Linux 회귀와 합성 업무 재사용

- 최신 Linux native snapshot: HEAD 9cd2f8b, Python 3.12.3. main196실행/194통과/2skip + scripts/delegation49실행/48통과/1skip = 총245실행/242통과/3 Windows전용skip, 실패·오류0. 구조검사와payload101동기화도exit0.
- 마지막 단일-process 검사에서 전송559파일manifest검증, 프로젝트451파일의 전후집합·바이트동일 확인(.git mutablemetadata/bytecode제외). 최초완주복사본은 사후조회에서없어 무변경판정을보류했고, 최종별도검사로해소함. 잘못된경로0test와중단Windows실행은통과집계제외.
- 실제모델 새2세션에서 검토기록을갖춘 합성매뉴얼로 W3/W4 결과생성; 각각done/pending2/1과1/3, 항목·상태·줄수·주차독립대조통과. 원본초안/입력/완료기준 보존. 실제사람인터뷰·업무승인으로확대하지않음.
- GitHub GET으로 remote main/기준HEAD일치와 LICENSE변경2건확인. 두버전모두불완전한허가본문, 원본DelegationLoop GET404. 재배포권리는여전히미확정이며권리자료대기.
- docs/verification-2026-10-21.md 및 approved-fixture/linux-final JSON에증거저장. 이마감이후변경은검증문서·이력뿐. Windows전체재실행·간헐지연원인·실제운영·marketplace/타모델세션은미검증. 임시파일보존, 제품코드/라이선스변경및커밋·푸시없음.

## 2026-10-21 검증 기록 전달 승인

- 사용자가 커밋·병합·푸시를 명시적으로 요청했다. 이전 단계의 미커밋·미푸시 표시는 각 검증 시점의 기록으로 보존한다.
- 전달 범위는 검증 보고서·비식별 JSON 증거 5개와 기존 이력 파일 2개다. 제품 코드·생성 배포본·라이선스 변경은 포함하지 않는다.
- main과 origin/main이 같은 상태이며 이 작업의 별도 병합 대상 브랜치·PR은 없다. 검증 기록을 main에 커밋하고 정상 푸시하는 범위다. force push나 새 라이선스 부여는 승인 범위에 넣지 않는다.
- 검증 근거: Linux 245개 실행/242개 통과/Windows 전용 3개 건너뜀, 실패·오류0; 실제 모델의 합성 업무 두 차례 실행·독립 대조; 프로젝트 451파일 전후 동일. 재배포 권리는 여전히 미확정이며 실제 업무 전체·간헐 지연 원인도 보장하지 않는다.

## 2026-10-21 전달 결과 및 기존 라이선스 정책 확인

- 검증 기록 7개를 f1ba322로 main에 커밋·정상 푸시했다. 기존 코드 수정은 이미 main에 있어 별도 병합 대상이 없었다. FEF CI 39506459166과 Delegation CI 39506459335는 모두 통과했다.
- 사용자는 추가 허락 자료 없이 기존 라이선스 정책을 따르도록 지시했다. 답변 대기를 종료하고 기존 LICENSE·권리 고지를 유지한다. 이를 권리 보유나 새 재배포 허가로 해석하지 않으며, 제3자 부분의 MIT 재선언도 하지 않는다.
- 이 확인은 문서·이력에만 반영한다. 제품 코드·생성 배포본·라이선스 본문 변경은 없다. 실제 업무 전체와 로컬 Windows 지연 원인은 여전히 미검증이다.

## 2026-10-21 미해결 훅 오류 후속 수정

- 이전 성공 뒤 snapshot/result/final-write 오류가 나면 성공이 남는 결함을 회귀 테스트로 재현(관련 4개 중 새 3개 실패)하고, 상태를 읽은 직후 이전 성공을 먼저 무효화하도록 수정했다. 새 회귀 5개와 Git timeout 고정 작업명 진단을 추가하고 생성본 4파일을 동기화했다.
- Ubuntu native/Python 3.12.3: 훅45개 통과; 전체 main201실행/199통과/2skip + delegation49실행/48통과/1skip =250실행/247통과/3 Windows전용skip. 프로젝트452파일 전후 동일, 저장소·payload101 검사 통과. Windows 진단 회귀2개도 통과했고 최종 구조·동기화 검사를 재실행했다.
- 로컬 diff 검토 완료. 필수 외부 code-change-reviewer는 코드·문서 diff의 Claude 전송에 대한 명시적 승인 부재로 자동 승인 검토가 차단해 미실행이다. 우회 전송 없음. 상세 근거는 docs/verification-2026-10-21.md에 기록했다.
- 사라진 과거 이력 파일의 링크를 Git history 보관 안내로 교정했다. Git 조회/최초 상태 쓰기의 fail-open, Windows 지연 원인, marketplace 세션·유효 ablation 및 추가 재배포 허가는 미해결이다. 기존 권리 고지 보존, 커밋·푸시 없음.

## 2026-10-21 승인 후 독립 리뷰 완료

- 사용자가 이번 diff의 외부 Claude 전송을 명시적으로 승인했다. 기존 역할이 자동 로드되지 않아 결과 없이 종료된 초기 시도 후, 같은 프로젝트 code-change-reviewer 정의를 CLI에 명시해 claude-sonnet-5/Read·Grep·Glob으로 성공한 리뷰 1회를 수행했다. 설정·권한 변경과 임의 모델 대체는 없다.
- 판정 Approve, Critical/Major 없음. 추가 상태 저장의 I/O는 오류 시 이전 성공을 남기지 않기 위한 비용으로 유지했다. 경계 테스트와 공유 상수 제안은 차단 결함이 아니므로 이번 범위에서 추가하지 않았다.
- 제품 코드 추가 수정 없이 훅45개를 재실행해 모두 통과했고 프로젝트452파일 전후 동일을 확인했다. 직전 전체250실행/247통과/3 Windows전용skip 결과는 별도 기존 검증으로 구분한다. 리뷰 완료 기록만 갱신했으며 커밋·푸시 없음.

## 2026-10-21 Windows 지연·최초 상태 저장 실패 후속

- 최초 baseline 저장 실패와 기존 성공의 최초 무효화 저장 실패 뒤 Stop 허용을 재현했다. Linux 새2개는 block 출력 부재로2error, 실제 Windows 공유삭제 불허 잠금도1error였다. PermissionError와 이전 JSON 보존을 먼저 확인했다.
- 기존 JSONv1 옆 세션별 `.failed` 표식을 shared save_state에서 저장 실패 시 남기고 Stop이 우선 확인하도록 수정했다. 성공 저장 이후만 해제하며 최초 오류 보존·민감 정보 비출력·세션 분리·one-shot을 유지했다. 새 회귀6개 추가, 사용 안내와 생성본 반영.
- Linux 전체256실행/252통과/Windows전용4skip/실패·오류0; Windows 저장6개·진단2개 통과. 구조검사/payload101 동기화 통과, native 프로젝트452파일 전후 동일. 독립 방향 검토와 claude-sonnet-5 code-change-reviewer 1회 수행, Critical/Major 없음. 리뷰 뒤 주석 표현만 명확히 했다.
- Windows 일반16표본과 프록시 비교16표본에서 timeout0. 실제 Git 조회는 평균0.656초, 기본프록시 경유1.267초로 실행 전후 비용의 일부를 확인했다. 동일버전2.54.0.windows.1이며 PATH/설정/보안/timeout은 유지했다. 과거15.460초 원인은 입증하지 못했다.
- 전체 저장 불가·루트 조회 실패·동시 writer 원자성은 보장하지 않는다. baseline 복구/clear는 현재 시점의 새 baseline이다. 상세 근거는 docs/verification-2026-10-21.md에 기록했다. 커밋·푸시 없음.

## 2026-10-21 Windows 전체 회귀·누적 최종 리뷰

- 기본 Windows PATH/Git과 Python3.14.4에서 main207실행/205통과/2skip(1584.776초), delegation49실행/47통과/2skip(47.649초). 합계256실행/252통과/4symlink권한skip/실패·오류0. 실제 파일 잠금·서브모듈 ignore-all·junction·짧은경로 회귀도 전체 실행에서 통과했다.
- 구조검사/payload101 동기화/git diff --check 모두exit0. 프로젝트452파일의 전후 집합·바이트 동일, 변경경로0. 테스트 실행 중 소스·문서를 수정하지 않았다.
- 사용자가 누적14파일 전체 diff의 외부 Claude 전송을 명시 승인했다. code-change-reviewer 1회와 독립 문서 검토 완료, Critical/Major 없음. 생성 wrapper diff누락 후보는 같은SHA원본에서2개hunk를 확인해 오탐으로 판단했다. 누적 생성 변경은5파일, 회귀 추가는11개다. 추가 제품 코드 수정 없이 검증 기록·이력만 갱신했다.
- Claude CLI 루트/생성본 검증도 통과. 루트 CLAUDE.md context 호환 경고와 catalog ICON_MISSING 권고는 별도이며 유지했다. Windows symlink4개·다른 Python 버전/현작업트리 원격CI·과거15초 timeout 원인·전체 저장 불가/루트조회/동시writer·marketplace/업무 전체·추가 재배포 허가는 여전히 한계다. 커밋·푸시 없음.

## 2026-10-22 검증된 누적 변경 전달 승인

- 사용자가 검증 완료된 누적 코드·문서·생성본의 커밋·정상 푸시와 해당 커밋의 원격 CI 확인을 명시적으로 요청했다. 앞의 미커밋·미푸시 표시는 각 시점의 이력이다.
- fetch 후 main과 origin/main은 edd862cd09821a6c636197a15ca1db9d6f64ce6b로 동일했고 별도 미전달 커밋은 없었다. 범위는 검토한14파일과 회귀11개이며 추가 제품 코드 변경은 없다. 구조/payload101/공백 검사를 다시 통과했다.
- Linux·Windows 각256실행/252통과/4플랫폼·권한skip과 누적 독립 리뷰를 근거로 전달한다. 기존 LICENSE·고지와 제한을 유지하며 새 릴리스·태그·권한·보안 설정은 변경하지 않는다. 실제 전달 해시와 CI 결과는 Git 이력·해당 원격 실행을 기준으로 확인한다.

## 2026-10-22 06:33 KST — 최종 전달 결과 및 작업 마감

- 최종 전달 커밋: [d0467e6f8af20d17f40d0246bc2d2c4e84010725](https://github.com/yjj3019/claude/commit/d0467e6f8af20d17f40d0246bc2d2c4e84010725). origin/main에 정상 푸시됐고 마감 시 원격 main의 동일 해시를 재확인했다.
- [FEF CI 39630976186](https://github.com/yjj3019/claude/actions/runs/39630976186): success, 5/5작업. [Delegation CI 39630976006](https://github.com/yjj3019/claude/actions/runs/39630976006): success, 5/5작업. 두 실행의 headSha가 최종 전달 커밋과 일치한다.
- 검증 요약: Windows256실행/252통과/4symlink권한skip, Linux256실행/252통과/4Windows전용skip, 실패·오류0. 구조·배포본101파일·공백 검사 통과, 프로젝트452파일 전후 동일. 누적 최종 독립 리뷰 Critical/Major 없음.
- 남은 제한: 로컬 Windows symlink4개 미실행, root CLAUDE.md context·catalog ICON_MISSING 권고, 과거15초 timeout 원인 미확정. 전체 쓰기 불가·루트 조회 실패·동시 writer 원자성은 미보장이다. marketplace 캐시 모델 세션·실제 업무 전체·유효 ablation·추가 재배포 허가는 여전히 미확정이며 기존 LICENSE·고지를 유지한다.
- 오늘 작업 종료. 제품 코드·생성본 추가 변경이나 새 릴리스·운영 배포는 없다. 이번 마감 이력만 로컬에 남기고 추가 커밋·푸시는 하지 않았다.

## 📎 Notion 기록 URL

[FEF Claude Framework - 2026-07-09](https://app.notion.com/p/398b44a2dd2e81729cb9dab78c31a5e7) 기존 개발 이력에 동일한 마감 결과를 추가했다.

후속 사용자 요청으로 로컬 마감 기록2파일의 커밋·정상 푸시와 그 커밋의 CI 확인을 진행한다. 위의 미커밋 표시는 06:33 당시 상태이며 제품 코드·생성본의 추가 변경은 없다.

## 2026-10-22 Fable 의존 제거·후속 전체 회귀

- 현행 소스에는 Fable 모사 실행기가 없음을 확인했다. 남은 전용 모델 권고·실행 지침·설치 문구·문서 검증 조건과 전이율 비교 형식을 제거했다. 일반 근거·안전·상태 검증과 과거 릴리스/실측 결과는 보존했다.
- 사용자 승인으로 L3 권고 `model` 값을 기존 L2와 같은 `Opus 5 (1M)`으로 변경했다. L0–L3 ID, JSON 키, 라우트, 상태 형식, Load Limits는 유지한다. 모델명 문자열을 사용하는 외부 소비자는 매핑 갱신이 필요하며, CLI는 호스트 모델을 자동 전환하지 않는다.
- 중복 tier 표를 canonical adaptive 가이드 참조로 정리했다. 모델 가이드는 UTF-8 17,320→15,582바이트(약10% 감소)이며 토큰·비용·품질·지연 개선 측정으로 해석하지 않는다. 회귀4개를 추가하고 생성 배포본3파일을 동기화했다.
- 승인된14파일 diff로 외부 Claude code-change-reviewer 1회를 완료했다. 모델별 결과 구분이 모호하다는 지적을 반영해 GT012 및 빈 결과 템플릿3개의 점수·실패 표에 Model 열과 모델 간 합산 금지 규칙을 추가했다. 답안 키와 기존 채점 가중치·실패 상한의 정합성을 확인했다.
- 최종 Linux/Python3.12.3: main211/208통과/3skip + delegation49/48통과/1skip. 최종 Windows/Python3.14.4: main211/209통과/2skip + delegation49/47통과/2skip. 각260실행/256통과/4skip/실패·오류0이며 Linux는 Windows전용, Windows는 symlink권한 제한이다. 저장소·배포본101파일·diff검사 모두 통과, 각 검증 중 프로젝트452파일 전후 동일을 확인했다.
- Windows main은2862.891초, delegation은66.765초였다. 느린 훅 테스트2개의 정적 Git 호출은 setup 포함13회·17회이며 상태 관측을 생략하지 않았다. 현 실행의 개별 Git 지연이나 과거 timeout 근본 원인을 새로 입증한 것은 아니다.
- 증거는 Temp의 `fef-fable-full.json`, `fef-fable-review.json`, `fef-windows-full-ssa25lvn/report.json`과 로그에 있다. 기준 HEAD는06b8c510abfe30fff4772eec9d8d6a73c58f3166이며 미커밋 변경을 포함한 작업트리를 검증했다. 검증 완료 뒤 이력2파일만 추가 갱신했다. 이번 변경의 커밋·푸시·원격CI·실제 모델 효능 평가는 진행하지 않았다. 기존 저장소/쓰기 실패·동시 writer 및 marketplace/권리 관련 한계를 이번 결과의 보증 범위로 확대하지 않는다.


## 2026-10-22 라이선스·출처 전면 감사 — 권한 확인 전 단계

- 기준 HEAD `11201b6859a06906237cf2b86b682cfca6d0a7d2`의 추적452파일을 열거·해시·Python 구문/import 검사하고 자체 저작 후보, DelegationLoop 파생물, 가이드, 역사 기록, 생성 배포본의 권리 범위를 분리했다. 상세 근거·한계·출처는 `docs/license-audit-2026-10-22.md`에 기록했다.
- 루트/생성본 LICENSE는 불완전한 MIT 자리표시자이며 제3자 자료의 명시적 공개 재배포 허락도 확인되지 않았다. 자체 FEF 저작분의 MIT 부여 권한 확인을 요청한 상태로, 답변 전 새 라이선스를 부여하지 않는다. 이전의 추가 허락 자료 부재 답변을 소유권 확인이나 새 허락으로 확대하지 않았다.
- 복구 번들은 실제 추적 중이며 68,724바이트/SHA256 `bba18c87965baa407d1fcf9f51d3f0b0f8a60fcbc010dd4cb449d5d50a1437d4`로 기존 기록과 일치한다. PyYAML은 선택적 런타임·테스트 의존성으로 구분했다. 전체 역사·문장별 원저자·별도 계약 확인은 미완료다.
- validator·payload101 동기화·build-plugin8개 테스트·diff 공백 검사 통과. 코드·라이선스·과거 기록·생성 배포본·설치 계약은 변경하지 않았다. 전체 회귀/원격CI 재실행, 커밋·푸시 없음.


## 2026-10-22 권한 확인 후 FEF 자체 저작분 MIT 적용

- 사용자가 `yjj3019` 명의 FEF 자체 저작분의 MIT 부여 권한을 명시 확인했다. 앞 절은 확인 전 단계이며, 현재는 LICENSE에 적용 범위·제3자 예외와 MIT 전문을 반영했다. DelegationLoop 관련 세 경로·외부 인용/원문·과거 기록 및 대응 생성 복제본은 제외한다. 혼합 패키지 전체 MIT 표시는 하지 않는다.
- README 한영본·현행 고지·Claude Code 안내·생성 README 문자열을 갱신하고 생성기를 통해 배포본5파일을 동기화했다. 원본 보관 bundle/PR JSON/manifest 바이트는 HEAD와 동일하다.
- 스킬 팩 설치가 LICENSE를 누락하던 복사 목록을 수정했다. 새 설치 및 명시적 --force 갱신에만 포함되며 기존 manifest v1·검증 필수 목록·설치 경로·스킬 호출·저장 데이터는 유지한다. 새 고지 복사/무결성과 이전 v1 설치 호환성 회귀2개를 추가했다.
- 독립 방향 검토와 최종 로컬 리뷰에서 차단할 권리 경계/호환성 문제는 없었다. 신규 README 로컬 고지 링크가 standalone에서 깨져 설치기71개 중2개가 실패했고, 원격 출처 링크로 수정 후 해당2개를 다시 통과했다. 기본 샌드박스의 별도 전체 재실행은 임시 .codex 디렉터리 쓰기 제한으로 판정에서 제외하고 허용된 실행 모드로 재검증한다.
- 최종 Windows 설치기71실행/69통과/2skip(100.263초), 부모 build-plugin8개 통과(59.483초), 라이선스 metadata1개 통과. 세 검증군 합계80실행/78통과/2skip. 최종 validator·payload101·diff검사 exit0, 제3자 validator·deterministic evidence 검사와 보관 파일 HEAD 바이트 동일 확인도 통과했다. 별도 runner의 기본 샌드박스 build8개는 임시경로 생성/정리 권한 오류로 실패해 부모의 허용된 실행 성공과 분리했다. 전체 Windows회귀·새 외부 모델 전송·커밋·푸시·원격CI·실제 모델 세션 검증은 하지 않았다. 제외 자료의 재배포 권한은 여전히 미확정이다.

- Skip 사유 추가 확인: 설치기 symlink 회귀2개를 별도 실행해 파일·디렉터리 링크 생성이 모두 WinError1314(필요 권한 없음)로 skip됨을 확인했다. 권한 설정은 변경하지 않았다.


## 2026-10-22 라이선스 변경 최종 리뷰·전체 회귀 — 커밋 전 기준

- 사용자 요청으로 누적17파일의 최종 로컬 리뷰, 전체 회귀, 문제 없을 때 커밋·정상 푸시와 해당 커밋 원격CI 확인이 승인됐다. 기존 절의 미커밋/전체 미실행 표시는 각 이전 단계의 기록이다.
- 최종 독립 로컬 리뷰와 메인 diff 검토에서 차단할 결함·권리 범위 모순·설치 호환성 문제를 찾지 못했다. MIT 권한은 사용자 확인을 근거로 FEF 자체 저작분에 한정하며 제3자 권리의 법적 완전성을 보증하지 않는다. 추가된 diff와 신규 감사 문서의 제한적 비밀정보 패턴 검사도 탐지0건이었다.
- Linux/Python3.12.3: main213실행/210통과/Windows전용3skip(12.273초), delegation49실행/48통과/Windows전용1skip(4.427초). 합계262실행/258통과/4skip/실패·오류0. 원본과 격리 복사본의 프로젝트453파일 전후 바이트 동일. 근거: Temp/fef-license-final-full.json.
- Windows/Python3.14.4: main213실행/211통과/2skip(1984.600초), delegation49실행/47통과/2skip(58.771초). 합계262실행/258통과/4skip/실패·오류0. Skip은 파일/디렉터리 symlink 생성 권한 제한이며 main2건은 실제 WinError1314를 기록했다. 파일 잠금·PowerShell wrapper·서브모듈 ignore 상태·최초 저장 실패 회귀도 통과했다.
- Windows validator·배포본101 동기화·diff 공백 검사 모두exit0. 프로젝트453파일의 목록·바이트 동일, changed_paths=[]이었다. 근거: Temp/fef-windows-full-4sblxs3a/report.json 및0.log~4.log. 최초 자동 승인 거절은 임시 하네스 전체와 쓰기 범위 안전성 확인 후 동일 명령 재요청이 승인돼 해소됐으며, 권한·보안·Git 설정 변경은 없었다.
- 테스트 중 제품·문서를 동결했고 완료 뒤 이 문서와 PROGRESS 기록만 갱신했다. 전체 실행은 실제 모델 품질·운영 설치·새 제3자 재배포 허락의 증명이 아니다. 제외 자료 권리 미확정, Windows symlink4개, 기존 간헐 Git 지연 원인·전체 저장 불가/동시 writer 한계는 유지한다. 새 릴리스·버전 변경·외부 모델 diff 전송은 하지 않는다.
- 위 결과는 커밋 전 작업트리 기준이다. 전달 커밋 해시와 그 커밋의 원격CI 결과는 최종 응답에서 보고한다.

## 2026-10-23 실제 모델·격리 설치 검증

- 기준45de11e2dbe8548f2542fb677b023286592bda85, Claude Code2.1.308/claude-sonnet-5-5/medium. 배포본101파일 임시 복사·세션 전용 로드로 실제 Kernel·Skill·Stop 차단 및 래퍼 성공/현재 snapshot 일치·Stop 허용을 확인했다. 전역·marketplace·production 설치는 하지 않았다.
- GT012 및 새 읽기전용 RCA 각각 baseline/FEF5회, 합계20회. 코드 독립테스트 양쪽5/5통과. 수동rubric 평균GT012 baseline100/FEF98.6, RCA97.6/97.6. 시간·CLI추정비용은 두 과제 모두 FEF가 더 들었다. 우위·절감·일반효능·Golden PASS로 해석하지 않는다.
- 명령 제한으로 FEF5회 직접unittest 기록returncode:null/Stop알림 후 재검증을 관찰했다. 별도 신뢰된 wrapper 세션은returncode0·현재상태일치·Stop허용. 최종Stop허용만으로 검증 성공을 주장하지 않는다.
- 수집기 타입오류 파일럿2개·줄바꿈 오판 RCA1개를 별도 보존·제외했다. OS격리 없는 호스트채점은 자동승인거절 뒤 사용자가 합성GT012각5회 위험을 인지하고 명시 승인했다. Podman info timeout으로 컨테이너 격리는 확인 못 했다.
- 제품453파일 및 사용자settings.json/CLAUDE.md 전후동일. 제3자 재배포 권리는 미확정. docs/verification-2026-10-23.{md,json}, tests/results/GT012-20261023.md에 상세 기록. 기록만 변경하며 커밋·푸시 없음.
- 기록 최종검증: repository validator·payload101 동기화·diff공백 exit0, JSON/20회점수·모델·보호파일·통계 assert/로컬링크/제한적 비밀정보·개인경로검사 통과. 이중이스케이프 개인경로1건 제거 후 재검증했다. 기존453파일 중 PROGRESS.md만 변경됐다. 이번 전체 회귀·새CI는 재실행하지 않았다.

## 2026-10-23 래퍼 허용 GT012 재비교·지연 원인 분석

- 기존 직접검사 실험의 정수종료코드 부재→null→Stop5/5→추가검사 경로를 확인했다. 코딩 스킬에 첫 검사부터 허용된 래퍼 사용과 기록한계 공개·알림만 위한 반복 금지·최종 자체완결 보고를 추가하고 대응 배포본1파일을 동기화했다. 훅·snapshot/footer·상태v1·호출명·라우트는 변경하지 않았다.
- 같은 래퍼/도구/명령을 양쪽에 제공해 GT012각5회 재비교했다. 실제claude-sonnet-5-5/medium/CLI2.1.308. 양쪽 독립테스트5/5·rubric평균100/SD0. FEF returncode0기록5/5, Stop알림0/5. 평균 baseline48.552초/$0.053725, FEF83.805초/$0.064336(CLI추정). 이전과 공통지시·래퍼·캐시·부하가 달라 일반 절감률이나 품질 우위를 주장하지 않는다.
- 신뢰된 단일 합성진단의 Git호출은1.664~3.333초. start4회/8.654초, wrapper7회/15.616초, recorder4회/7.597초, Stop4회/7.540초. 이 별도 진단은 실제모델 지연 전체의 분해나 OS근본원인 증명이 아니다. snapshot 안전성을 줄이는 변경은 하지 않았다.
- 관련 고유25회귀 통과(runtime7/context3/build8/wrapper7); 공백 경로·무관한 프로젝트에서 실제 recorder0기록까지 강화한 새 테스트1회도 재통과했다. 최초 샌드박스·cwd 오류는 정상재실행과 구분했다. 전체 회귀·새CI는 미실행이다.
- 실험중456파일·확인대상 사용자설정 전후동일. 생성코드 제품반영 없음. 증거 docs/verification-wrapper-2026-10-23.{md,json}, tests/results/GT012-20261023-wrapper.md. 외부 code-change-reviewer용3파일 diff 전송은 사용자 승인 대기. 커밋·푸시 없음.
- 최종 repository validator/payload101/diff공백 exit0, JSON·모델/점수/상태/해시 assert·로컬링크·제한적 비밀정보/개인경로·Python구문 검사 통과. 외부diff리뷰는 승인 대기이며 수행했다고 표시하지 않았다.

## 2026-10-23 TaskForge for Claude 표시 이름 적용

- 사용자가 이름 검토와 반영을 요청했다. 제품 표시명을 TaskForge for Claude, 게시자 by yjj3019, 이전 명칭 FEF로 정리했다. 한영 README·한국어 호환 링크·plugin displayName/설명·marketplace 설명·설치 안내/생성 텍스트·런타임 제목을 갱신했다. 독립 프로젝트이며 Anthropic의 공식 제품·후원·보증이 아님을 명시했다.
- 공개 검색에 별도 taskforge 목록이 확인돼 명칭 고유성을 단정하지 않았다. Anthropic 상표 지침의 허가·제휴 표시 제한도 확인했다. 명칭 등록·상표 사용 허가·공개 배포 승인은 확인되지 않았고 로고·외부 계정·전역 설치·저장소 URL을 바꾸지 않았다. 근거와 한계는 docs/ClaudeCode.md의 Product name and retained identifiers에 기록했다.
- 기술 ID fef-engineering/fef-marketplace/fef-claude, 기존 renames 맵, 스킬 frontmatter·호출, 환경변수·설치 manifest, state v1·footer·실패 표식은 유지했다. native Skill 본문·Kernel·검증 훅·라우트·라이선스·제3자 보관물은 그대로다. 과거 FEF 평가군·실측 기록은 새 브랜드로 소급 치환하지 않았다. standalone 설명에는 기존 FEF와 새 제품명의 명시 요청을 함께 반영했다. 이전 native ID 이관과 이번 표시명 변경을 분리하고 기존 문서 앵커를 보존했다.
- 생성기를 통해 payload101개 중8파일을 동기화했다. 원본 installer/builder AST는 문자열 변경을 제외하면 동일하다. 사전459파일 해시 스냅샷과 독립 로컬 리뷰로 기존 미커밋 변경 보존을 확인했다. FAQ의 측정 근거 없는 일괄 품질 개선 표현도 작업별 평가가 필요하다는 설명으로 수정했다.
- 최초 설치 전체회귀71개 중1실패/2skip: 기존 미커밋 GT012 결과2문서가 선별 설치에서 제외되는 실험 보고서로 상대 링크를 걸었다. 첫 수정의 인라인 docs/*.md도 PATH_RE 검증 대상이라 targeted1개가 실패했다. 원본 checkout docs 폴더의 파일명 안내로 바로잡은 뒤 targeted1개 통과(6.919초). validator·복사 정책은 약화/변경하지 않았고 보고서 JSON·점수·표·결론은 보존했다.
- 최종 Windows 설치기71실행/69통과/2skip(81.416초), plugin runtime7통과(45.730초), build-plugin8통과(50.246초), sync-kernel6통과(0.117초). 합계92실행/90통과/2skip/실패·오류0. Skip은 파일/디렉터리 symlink 생성 권한 WinError1314이며 권한 설정은 변경하지 않았다.
- repository validator·10라우트·Kernel 동기화·payload101·diff공백 exit0. 루트 및 생성본 claude plugin validate도exit0이다. 루트 CLAUDE.md context 경고와 catalog ICON_MISSING 권고는 유지한다. 기존 평가 JSON·제3자 원본·라이선스는 해시 동일, 결과문서2개는 참조 표기만 변경했다.
- 새 모델 세션의 표시/호출·전체 회귀·새 원격CI·전역/marketplace 배포는 실행하지 않았다. 버전1.3.1 유지, 캐시 설치본 자동 변경 없음. 이전 코딩 안내 diff의 외부 리뷰 승인은 별도 대기 상태이며 이번에 외부 모델로 diff를 보내지 않았다. 커밋·푸시 없음.

## 2026-10-23 누적 변경 최종 로컬 리뷰·Windows 전체 회귀

- 표시명 변경과 이전 검증 래퍼 안내·통합 회귀·실험 문서를 포함한 누적 작업트리를 HEAD 45de11e2dbe8548f2542fb677b023286592bda85 기준으로 다시 검토했다. 독립 로컬 리뷰에서 수정할 결함은 발견하지 못했다. 설치기/생성기의 문자열 외 AST, 스킬 frontmatter·기술 ID·상태 계약·원본/생성본 일치를 확인했고 JSON 통계 재계산도 문서와 일치했다. 제한적 시크릿·개인 경로 패턴 검사에 탐지 후보는 없었다. 원시 모델 로그·외부 문헌을 새로 검증한 것은 아니다.
- Windows/Python3.14.4 메인214실행/212통과/2skip(2007.799초), delegation49실행/47통과/2skip(53.003초). 합계263실행/259통과/4skip/실패·오류0이다. 파일·디렉터리 symlink 생성 권한 제한이며 메인2개에서 WinError1314를 확인했다. 권한 설정을 변경하지 않았다. 최초 상태 저장 실패·최종 저장 실패·PowerShell 래퍼·서브모듈 ignore 상태·공백 설치 경로의 recorder 통합 회귀도 통과했다.
- repository validator(31 Golden Tests 메타데이터, 모델 실행 아님)·Kernel/10라우트·payload101 동기화·delegation validator·deterministic evidence --check·보관 이력 checksum/복구/refs/commits/file bytes/fsck·git diff --check 모두 exit0이다. 공백 검사에는 기존3파일의 LF→CRLF 안내만 있었다. 현재 패키지 모델 효능 증거의 UNVERIFIED/HISTORICAL 표시를 유지했다.
- 검증 중 프로젝트459파일 aggregate SHA256은 전후 6c42aa5991d5fe7374c6f2a32d043ebfd7da7086aba64dce373e1f1160b3a420으로 동일했다. 제품을 수정하지 않았으며 검증 완료 후 이 이력만 추가했다. 원시 로그는 임시 폴더 final-windows-regression-97fb15c52d39402189837245bd610698의 01-main-tests.log~07-git-diff-check.log에 있다.
- 이번 Linux/Python 버전 행렬·실제 모델/UI·원격CI·전역/marketplace 배포는 실행하지 않았다. 외부 Claude diff 리뷰의 별도 전송 승인은 여전히 대기 상태다. 제3자 재배포·명칭/상표 권한, Windows Git 지연 근본 원인, symlink 미실행4개와 기존 CLAUDE.md/아이콘 경고는 남아 있다. 버전 변경·커밋·푸시 없음.

## 2026-10-23 Windows Git 지연 분리 진단

- 새 임시 저장소에서 기본 Git 실행기와 같은 설치의 내부 실행 파일을 AB/BA/BA/AB 네 쌍씩 비교했다. version/status/서브모듈 없는 submodule status 모두 exit0·stdout/stderr 해시 동일. status 중앙값은1.870055/0.802335초였다. 별도 status 외부2.190938초에 Trace2 내부 exit t_abs0.154657초, 빈 Python 실행 중앙값0.788304초도 확인했다. 범위는 Git 내부보다 실행 전후 구간으로 좁혀졌으나 보안 검사·실행기·시작/종료 처리 등 특정 근본 원인은 미확정이다.
- CREATE_NO_WINDOW 비교 네 쌍의 중앙값은 기본1.575134/옵션1.655511초로 개선을 관측하지 못했다. 기본 샌드박스의 임시 fixture 권한 오류 및 worktree 안에 trace를 둔1차 측정은 유효한 동일 조건 비교와 구분했다. 후속 trace는 worktree 밖에 두고 출력 동일을 확인했다.
- 실제 서브모듈·다른 Git 설치·helper/필터 호환성을 검증한 것은 아니므로 내부 실행 파일을 제품에 하드코딩하지 않았다. Git 호출·snapshot·timeout·보안 설정·사용자 저장소/전역 설정을 변경하지 않았다. 근거·전체 시간 표본·출력 해시·한계는 docs/windows-git-latency-2026-10-23.md에 기록했다. 중앙값 재계산·출력/종료코드 일치 assert, repository validator/payload101/Kernel/10라우트 및 diff 공백 검사 통과.
- 이번 변경은 진단 기록뿐으로 전체 회귀를 반복하지 않았다. 직전263실행/259통과/4skip 결과와 구분한다. 외부 diff 전송·실제 모델·원격CI·배포·커밋·푸시 없음.

## 2026-10-23 Windows Git 직접 실행 호환성 후속 검토

- Git for Windows 공식 wrapper 문서에서 내부 Git 절대 경로 직접 호출 지원을 확인했다. 전역 PATH 추가와는 구분한다. 임시 fixture에서 제품 snapshot 함수를 수정 없이 사용해 실행 파일만 비교했고 unborn HEAD·실제 로컬 서브모듈·공백/유니코드 staged rename 및 ignore=all인 dirty child의 snapshot이 모두 동일했다. child 수정/미추적2파일과 부모 rename도 감지됐다. 고정 셸 alias 출력/exit0/stderr0바이트 동일 확인도 통과했다. 각 상태1쌍·고정 실행 순서의 시간은 일반 성능 증거로 확대하지 않는다.
- 독립 방향 검토에서 경로 이름/버전만으로 custom wrapper를 식별할 수 없고 절대 실행 경로를 쓰면 기존 timeout operation 진단이 사라질 수 있음을 확인했다. 자동 우회를 적용하지 않았다. 기본 PATH·wrapper 동작을 유지하고 명시 지정에만 적용하는 FEF_GIT_EXECUTABLE 방안을 제시했다. 새 공개 설정 계약이므로 사용자 승인을 요청했으며 아직 구현하지 않았다. 공용/HEAD/재귀 호출 일치, 실패·timeout·비밀정보 비노출, observer 전체 및 HOME 미설정/공백 설치 경로 검증을 수용 기준으로 정리했다.
- 진단 결과와 공식 출처·제한은 docs/windows-git-latency-2026-10-23.md에 추가했다. 사용자 저장소·전역 설정·런타임·생성 배포본은 변경하지 않았다. 전체 회귀·외부 모델 전송·원격CI·커밋·푸시 없음. 설정 추가 승인은 대기 상태이며 과거 외부 diff 전송 승인 대기와 구분한다.

## 2026-10-23 명시적 Git 선택 구현·관련 회귀

- 명시적 선택 방안을 제안한 뒤 사용자의 후속 진행 지시에 따라 FEF_GIT_EXECUTABLE을 구현했다. 미설정/빈 값은 기존 git 검색을 유지하고 절대 파일 경로(Windows .exe)만 명시 선택한다. 잘못된 경로·실제 실패를 기본 Git으로 재시도하지 않는다. 공용/HEAD/재귀 호출을 맞췄고 자체 Git timeout만 기존 진단 whitelist용으로 정규화했다. snapshot/state v1·footer·timeout·검증 child 명령은 유지했다. 신규 회귀8개, 설치/해제 안내, 생성 배포본2파일을 반영했다. 자동 우회/probe·전역/사용자 설정·버전 변경은 없다.
- 로컬 독립 리뷰에서 구체적 결함을 발견하지 못했다. 설정/진단13 + 기본 실제 훅3 + 명시 핵심 훅5 + runtime7 + build8 + installer71 =107실행/105통과/2symlink skip/실패0이다. Skip은 WinError1314 권한 제한이다. 최초 기본 샌드박스의 임시 쓰기/정리 오류 및 runner cwd 오류는 정상 재실행과 구분했다. 별도 원시 로그 파일은 없고 도구/세션 출력에 결과가 있다.
- 실제 별도 프로세스 observer8회(AB/BA/BA/AB; 공백 작업·Git 경로; 후반2쌍 HOME 제거)에서 test exit0·recorder0·Stop 허용을 확인했다. 전체 중앙값은 기본50.957952초/명시27.278230초였다. 합성 단일 호스트·동시 회귀 부하의 관측이며 실제 모델 지연·비용·일반적인 속도 개선 주장이 아니다. 상세 표본/한계는 docs/windows-git-latency-2026-10-23.md에 기록했다.
- repository validator·payload101·10라우트·Kernel·diff 공백 검사 통과. 이번 전체 main/delegation·Linux 실기·실제 Claude/UI·원격CI·전역 배포는 실행하지 않았다. 이전263개 전체 회귀는 이번 코드 구현 전 결과다. 외부 Claude diff 전송은 별도 승인 대기이며 전송하지 않았다. 커밋·푸시 없음.

## 2026-10-23 기본/명시 Git 양쪽 Windows 전체 회귀·누적 최종 리뷰

- 같은 HEAD45de11e2dbe8548f2542fb677b023286592bda85/제품460파일에서 Windows Python3.14.4 main/delegation 전체를 양쪽 설정으로 실행했다. 기본: main222/218통과/2skip/2실패(2825.735초), delegation49/47통과/2skip(76.991초). 명시: main222/220통과/2skip(1901.936초), delegation49/47통과/2skip(162.866초). 합계542실행/532통과/8skip/2실패/오류0이다. Skip은 symlink 권한 제한이며 메인에서 WinError1314 확인. 시간 비교를 일반 성능 개선률로 해석하지 않는다.
- 기본 실패2개는 malformed wrapper의 Stop 차단 기대 및 native JSON 진입점 setup에서 Git status15초 timeout 진단이 발생한 경우다. 두 개 기본 설정 단독1회 재현은2/2통과(136.054초), 명시 전체에서도 각각 통과했다. 지속 재현되는 새 코드 결함은 확인하지 못했고 판정/timeout/PATH를 완화하지 않았다. 기본 설정의 안정적인 전체 통과는 미확인으로 남긴다. 과거 성공 결과나 단독 재현으로 이번 실패를 지우지 않았다.
- 두 설정의 repository/payload101/10라우트/Kernel/위임 validator/deterministic evidence/보관 이력/diff 검사 exit0. 첫 기본 실행 완료 뒤 사용자 settings.json 해시 변경으로 하네스가 명시 시작 전 중단됐다. 제품 변경경로=[]/사용자 CLAUDE.md 동일. 테스트 홈 격리와 설정 사용처를 확인했으나 작성 주체는 미확정이다. 사용자 파일을 복원/덮어쓰지 않았다. 같은 제품 해시를 강제한 별도 명시 하네스에서 현재 설정 기준으로 완료했고 해당 실행 동안 제품·확인대상 사용자 파일 모두 동일했다. 전체 세션 사용자 설정 불변성은 주장하지 않는다.
- 원시 로그와 report는 Temp/fef-dual-windows-full-9xe_gozo 및 fef-explicit-windows-full-04ocn41k에 보존했다. 첫 실패 요약의 skip 집계 누락은 원본을 보존한 normalized-default-report.json에서 실제 FAILED summary로 수정했다. 단독 재현 로그는 default-env-failures-5658f4990cf549bfb60401391a5b75a7.log다. 메인에서 원시 요약·설정별 기준 해시 동일·최종 HEAD를 대조했다.
- 누적29개 변경+미추적7개 독립 로컬 리뷰에서 구체적 수정 결함은 발견하지 못했다. 원본/생성본8쌍·문자열 외 installer/builder AST·통계/문서·기술 ID·권리 경계 일치, 제한적 시크릿/개인 경로 탐지 후보0건을 확인했다. 제품은 동결 유지하고 검증 뒤 이 이력과 진단 문서만 갱신했다. 다른 OS/Python·실제 Claude/UI·외부 diff 전송·새CI·배포·제3자/상표 권한은 별도 미검증이다. 커밋·푸시 없음.

## 2026-10-23~24 기본 설정 안정성 확인: 연속 통과 미달

- 기본 설정에서 이전 간헐 실패2개를 각각3회 순차 실행해6/6통과했다(unittest411.575초). 이어 같은 HEAD45de11e2dbe8548f2542fb677b023286592bda85/제품460파일로 전체 회귀를 두 차례 실행했다. FEF_GIT_EXECUTABLE만 자식 환경에서 제거했고 PATH·사용자 설정·Git15초 제한·판정은 유지했다. 별도 검증/로그 감시 프로세스 병렬 실행 없음.
- 1차: main222/220통과/2skip(3073.708초), delegation49/47통과/2skip(68.252초), 합계271/267통과/4skip/실패·오류0. 2차: main222/216통과/2skip/3실패/1오류(3102.181초), delegation49/47통과/2skip(168.286초), 합계271/263통과/4skip/3실패/1오류. 전체542실행/530통과/8skip/3실패/1오류이며 사전6개는 별도다. Skip은 기존 symlink 권한 제한이다.
- 2차 실패는 읽기전용 dirty 세션 setup의 head, 실제 래퍼 실패 setup의 repository, 실제 래퍼 성공 setup의 status 조회에서 Git15초 초과가 발생한3건이다. 서브모듈 snapshot의 child rev-parse도15초 초과 오류였다. 메인이 원시 traceback과 최종 report를 확인했다. 특정 입력 결함보다 간헐적 프로세스 지연 가설이 남고 OS 근본 원인은 미확정이다. 순차 실행으로도 재발했으므로 세 번째 전체 반복·timeout 증가·자동 재시도·wrapper 자동 우회·검증 완화를 하지 않았다. 안정적인 연속 전체 통과는 미달이며 다음 진단은 OS 추적 또는 별도 Windows 호스트 비교다.
- 두 라운드 모두 repository/payload101/위임 validator/evidence/보관 이력/diff exit0. 제품·확인대상 사용자 파일·HEAD 전후 동일(source_unchanged=true, user_unchanged=true); two_rounds_passed=false. 원시 근거는 Temp/fef-default-stability-1ta8gikm의 report.json과 라운드별 로그, 상세는 docs/windows-git-latency-2026-10-23.md다. 종료 후 이력2파일만 추가 갱신했다. 제품 수정·외부 diff 전송·실제 모델·새CI·배포·커밋·푸시 없음.

## 2026-10-24 AI-Harness 비교 분석·선별 반영

- 사용자 요청 저장소 yjj3019/AI-Harness의 HEAD ac4c59adcced5484c9e9c7952b5794c880838a97을 별도 참조 clone으로 읽었다. .git 제외14파일(문서·에이전트5개·JS 스켈레톤)을 분석했다. 원본 명령·설치 스크립트를 실행하거나 원본 파일을 제품에 복제하지 않았다. 공식 Anthropic 장기 하네스 연구와 Claude Code subagent 형식도 확인했다. 상세 근거·소스 고정 링크·채택표는 docs/ai-harness-assessment-2026-10-24.md에 있다.
- 루프 JS에는 실제 에이전트 호출·판정·재시도·상태 갱신이 없고5개 에이전트 정의의 YAML frontmatter 구분자가 없다. LICENSE/명시 재배포 허가도 확인되지 않았다. 자동 런타임·권리 확정으로 취급하지 않았다. 강제 커밋/세션 재시작·70% 임계·매 작업 전체 교훈 로딩·5에이전트 상시 구동·효능 보장은 미채택이다.
- 일반 운영 원칙을 독자적으로 서술해 기존 소유 문서5개에 반영했다: Coding의 단계별 완료 근거/현재 작업 상태/제한적 복구, Context Protocol의 핸드오프/재개 시 실제 상태 대조/승인 보존, Review의 원본 근거/미실행 구분, Knowledge Governance의 선택적 교훈 축적, Presentation의 대표 샘플/전체 렌더링·편집성 검증. 기존 생성기로 payload101파일 중5개를 동기화했다. 새 런타임·의존성·명령·상태 원장·설정은 추가하지 않았다.
- Kernel·CLAUDE.md·AGENTS.md·라우트·기술 ID·에이전트 정의·훅·상태v1·Git15초 timeout·선택 정책은 유지했다. 선택 문서는 길어졌으나 기본 cold-start 경로는 그대로다. 실제 토큰·지연·비용·품질 변화는 측정하지 않았다. 별도 읽기 전용 문서 검토에서 구체적 사실오류·과도도입·권리 범위 혼동은 발견하지 못했고, 메인이 원본 및5쌍의 생성본 바이트 일치와 사전460파일 해시 기준을 대조했다.
- 관련 회귀: context3/latency5/build8/installer71/runtime7/framework5, 유효 테스트99개 중97통과/2skip/실패·오류0. Skip은 symlink 권한 WinError1314다. 최초 tests cwd 묶음은95실행/92통과/2skip/1 import 오류(750.117초)였다. test_validate_framework의 scripts import에 필요한 저장소 루트가 빠진 부모의 명령 경로 오류였으며, 소스 수정 없이 해당 모듈만 루트에서 재실행해5/5통과(0.366초)했다. 최초 실패 로그를 보존했고 전체 묶음을 다시 돌려 지우지 않았다. 새 코드 로직이 없어 지침 문자열을 반복하는 테스트는 추가하지 않았다.
- repository validator/10라우트/Kernel/payload101·build_plugin --check·git diff --check 모두exit0. Golden31개는 메타데이터 검사이며 모델 실행이 아니다. 원시 로그와 summary.json은 Temp/taskforge-harness-adoption-zzmtkuyl에 있다. 기존 LF→CRLF 안내는 유지한다.
- 기본 Windows Git의 간헐 timeout·직전 연속 전체 회귀2차 실패는 미해결이다. 이번 전체 main/delegation·실제 모델·원본 AI-Harness 호스트 인식/실행·PPT 출력·외부 Claude diff 리뷰·원격CI·전역/운영 배포는 수행하지 않았다. 원본 권리와 기존 제3자 재배포 권한도 미확정이다. 커밋·푸시 없음.

## 2026-10-24 전체 회귀·실제 모델·PPT 후속 실행 검증

- 사용자 요청으로 같은 HEAD45de11e2dbe8548f2542fb677b023286592bda85/미커밋 제품461파일을 동결해 세 검증을 수행했다. 제품 목록·바이트·HEAD와 관측 대상 사용자 settings.json/CLAUDE.md 해시가 전후 동일했다. 완료 뒤 이력·평가서 후속 링크·새 검증 MD/JSON만 기록했다. 상세는 docs/verification-2026-10-24.md 및 대응JSON이다. 커밋·푸시 없음.
- 기본 PATH Git/15초 제한 유지: main222/218통과/2skip/2실패/오류0(3684.720초), delegation49/47통과/2skip(79.236초). 합계271/265통과/4skip/2실패/오류0. 실패는 payload-alone baseline의 head 조회와 bool-exit setup의 repository 조회 timeout이다. 원문 traceback을 부모도 대조했다. symlink4skip은 기존 Windows 권한 제한이다. 저장소·payload101·10라우트·Kernel·위임 validator·evidence·보관 이력·diff 검사 exit0. timeout 증가·자동 우회·재시도·판정 완화는 하지 않았고 기본 설정 전체 통과는 미달이다.
- 초기 관측기가 stdout만 읽어 stderr의 unittest 진행/집계를 놓쳤다. 원시 로그/commands.json을 유지하고 normalized_report.json을 작성했으며, 부모가 최종 Ran/FAILED/OK 원문을 별도로 파싱해 집계를 확인했다. 사용자 파일 비교의 Windows 경로 구분자·16진 해시 대소문자도 정규화했다. 이 계측 오류는 제품 실패2건과 구분한다.
- 실제 Claude Code2.1.309/claude-sonnet-5-5/medium의 두 새 CLI 컨텍스트에서 GT012 수정→핸드오프 재개를 실행했다. Skill·Kernel·현재 가이드4개 Read·보호 파일 불변·현재 snapshot과 returncode0을 확인했고 독립 채점도6/6통과했다. 생성 parser는 제품에 적용하지 않았다. 첫 세션은 비허용 python -c1회 시도가 CLI allowlist에 차단됐고 음수 미지원이라는 보고 오류가 있었다(-1 probe는-1). 원본 응답/핸드오프와 오류를 보존했다. 단일 fixture·ignored 진행 기록·내장 cc 플러그인 잔존 조건이며 일반 효능·A/B·Golden PASS 증거가 아니다. CLI추정비용합계0.2366266USD는 구독 청구액이 아니다.
- PPT 대표2장 먼저 검사 후 전체4장 생성. PowerPoint16.0.20430.20182 실제 읽기전용 open·PNG4개1600x900·PDF export·native chart/table/workbook·한국어제목·원본 OOXML 검사 모두 통과했다. 작성자와 부모가4페이지를 각각 직접 확인했다. 최초 의존성 부재·COM0x80080005·guard2회 중단을 보존하고 문서0개인 작업 소유 orphan만 확인·정리한 뒤 STA 재검증에 성공했다. 문서 Close/Quit·작업 프로세스 종료 완료. defusedxml0.7.1은 검증 전용 target/자식 PYTHONPATH에만 준비했으며 제품·전역 의존성을 바꾸지 않았다. 재시도 성공이 COM 근본 해결이나 Claude PPT 효능의 증명은 아니다.
- 증거는 checkout과 나란한 validation-20261024-full-model-ppt의 regression/model/ppt에 보존했다. 모델·Office 작업이 일부 같은 호스트에서 겹쳐 통제된 성능 실험이 아니다. Windows Git 지연 원인·PPT 수동 편집/스크린리더·Linux/다른 버전 행렬·원격CI·실운영/marketplace 배포·제3자 재배포 권리는 미확인/미해결이다. Claude API와 격리 검증기용 PyPI 다운로드 외에 누적diff 외부리뷰·외부 메시지는 수행하지 않았다.

## 2026-10-24 커밋·푸시 및 원격 CI 확인 / 작업 마감

- 사용자 승인으로 누적 코드·문서·생성 배포본·검증 기록 47파일을 `7fce4b5efd415d8ae80b5db8484212735f3712ff` (`feat: adopt TaskForge branding and evidence-led workflows`)에 커밋하고 `origin/main`에 일반 푸시했다. 사전 fetch에서 로컬/원격 분기 차이가 없어 별도 merge는 필요하지 않았다. 원격 main 해시 일치와 커밋 직후 깨끗한 작업 트리를 확인했다. 제품 표시명은 TaskForge for Claude이며 기존 기술 ID·호출·상태 형식을 유지했다.
- 커밋 전 repository validator·10라우트·Kernel·payload101 동기화·스테이징 diff 공백 검사와 JSON 파싱을 통과했다. 제한적 인증정보 패턴 검사 후보는 0파일이었다. 이는 포괄적인 시크릿 감사나 전체 회귀 재실행을 뜻하지 않는다.
- 정확히 위 커밋의 원격 CI 두 실행이 `completed/success`임을 마감 시 다시 조회했다. [Validate FEF Harness #40002063791](https://github.com/yjj3019/claude/actions/runs/40002063791): Linux Python3.11/3.12/3.14 및 Windows 설치·훅·빌드 Python3.11/3.14의 5작업 성공. [Validate Delegation Loop #40002063747](https://github.com/yjj3019/claude/actions/runs/40002063747): Ubuntu/Windows × Python3.11/3.14와 deterministic ZIP 비교의 5작업 성공. 합계10/10작업 성공이다. 원격 CI 범위는 로컬 Windows 전체 회귀와 동일하지 않다.
- 남은 제한: 로컬 기본 Windows 전체 회귀는271개 중265통과/4skip/2실패이며 Git15초 timeout 2건의 OS 근본 원인은 미해결이다. 원격 성공으로 이 실패를 해소했다고 간주하지 않는다. symlink 권한 skip, 실제 모델의 단일 GT012·두 컨텍스트 범위와 보고 오류, PPT COM 최초 실패 원인·수동 편집/스크린리더 미검증도 앞선 원시 증거와 함께 유지한다. 일반 효능·비용 절감·운영 안정성은 보장하지 않는다.
- CI에는 actions/checkout@v4·actions/setup-python@v5의 Node20 지원 종료/Node24 강제 실행 및 ubuntu-latest 이미지 전환 안내가 남았다. 이번 마감에서 워크플로·의존성 업그레이드는 하지 않았다. 플러그인 버전은1.3.1로 유지되어 기존 캐시 설치의 자동 갱신은 보장되지 않는다. 실운영/marketplace 배포·누적 diff 외부 Claude 리뷰·제3자 재배포 권한·이름/상표 권한은 별도 미검증/미확정이다.
- 이 마감 기록은 위 제품 변경 커밋 이후 작성했으며, 작성 당시 로컬 미커밋 상태였다. 사용자 후속 요청에 따라 별도 문서 커밋으로 푸시하고 해당 커밋의 원격 CI를 확인한다. 위 CI 링크는 제품 변경 커밋에 대한 결과이며 이 후속 문서 커밋의 결과와 구분한다. 오늘 제품 변경과 실행 검증을 종료한다.


## 2026-10-24 Windows 사용자 운영 배포·제외 자료 및 Git 완화

- 사용자 승인으로 권리 미확정 위임 자료14파일을 제외한87파일을 별도 로컬 버전1.3.2-local.20261024로 사용자 범위에 설치했다. 원본101파일·소스77f447e·기술ID·기본스킬·state v1은 보존했고 ai-delegation-loop 호출 제외는 승인받았다. 기존 synced1.3.1은 삭제 없이 비활성화했다. 설치 해시·공식strict검증 통과, 설정·등록부 비공개 백업 완료.
- Windows Git은 user env의 기존 FEF_GIT_EXECUTABLE을 신뢰한 기존 내부 실행 파일로 명시했다. 관련10/10회귀(123.992초), 설치 훅5개·실제검증1개·통과후Stop허용/재수정차단을 확인했다. 기본 PATH의 OS원인 해결·전체회귀 재통과로 표현하지 않는다.
- 새 실제Claude/sonnet5.5/medium 세션 exit0/응답확인/85.842초. 운영 플러그인1개·기본2스킬·Kernel로딩·제외스킬부재와 사용자env설정에 의한 FEF형태Git호출8개 명시경로를 Trace2로 확인했다. 관측 hook응답3개 success/exit0. 단일합성 검사이며 일반효능 보장은 아니다.
- 제3자허가 자체는 미확정이며 이번 운영배포는 제외로 처리했다. 원본/독립installer의 공개재배포 권리까지 해결했다고 주장하지 않는다. 최초 절대Python자식명령 인식차단·.pyc 텍스트검사 인코딩오류는 원문보존 후 검사범위만 바로잡았다. 제품코드·검증정책·보안설정·15초timeout은 바꾸지 않았다.
- 상세범위·증거·롤백·한계는 docs/deployment-2026-10-24.md에 기록했다. 운영설정은 새세션에서 확인했고 기존실행세션은 강제종료하지 않았다. 이번 소스 커밋·푸시는 하지 않았다.


## 2026-10-24 신규 배포 차단·권리 확인 절차·스킬 버전 준비

- 사용자 승인으로 미확정 위임 자료의 native 생성·독립 설치·ZIP 신규배포를 차단했다. 원본은 보존했고 바이트 동일을 확인한 생성 사본14파일만 제외했다. CI는 ZIP 배포 거부를 검사하며 기존 집계 job ID를 유지하고 선행 실패도 전파한다. export-ignore는 향후 git archive에 적용하며 raw clone/기존 공개 이력/수동 복사를 통제하는 보안 경계가 아니다.
- 권리자·대상revision/hash·허용행위·조건·증빙·검토결론과 코드 변경에 의한 해제 기준을 docs/third-party-clearance.md에 정리했다. 허가 자체를 새로 확보하지 않았고 외부 연락도 하지 않았다. 새 CLI 우회 플래그나 JSON 허가 토글은 없다.
- 자체 native스킬2개 metadata.version1.0.0 및 standalone본문1.0.0을 최초 명시 버전으로 제공하고 제거기능이 있는 native패키지는2.0.0으로 구분했다. docs/skill-versions.md에 범위/호환/캐시/변경 기준을 기록했다. 기술 ID·Kernel·기본 coding/RCA·설치manifest/state v1은 유지했다.
- 생성89파일sync·스킬quick_validate2개·공식nativeCLIstrict검사 통과. 배포/아카이브/embedded/표시계약 targeted4개 및 기본정책4개 통과. 정책 worker 초기35개 중5개는 CI evidence drift로 실패했고 원문을 보존했다. 관련 문서계약/oracle self-check를 실행해 증거를 갱신·재검증했으며 현재 모델효능은 UNVERIFIED로 유지했다.
- 아키텍처 방향·최종 독립 로컬 코드리뷰에서 확정P0-P3 지적 없음. 외부Claude에 새diff를 전송하지 않았다. 스크립트 삽입위치/작업cwd 실수는 제품실패와 구분해 수정했다.
- WPR CPU 추적은 시스템 전역 활동·민감정보 수집에 대한 명시승인 부족으로 자동 승인 검토가 거절했다. 현재 관리자토큰도 없으며 우회하지 않았다. 별도 승인 질문을 유지한 채 나머지 작업을 진행한다. OS원인 해결이나 기본PATH timeout 부재는 주장하지 않는다. 제품 동결 후 운영 명시Git 환경의 Windows 전체 회귀를 진행한다. 커밋·푸시 없음.

## 2026-10-24 배포 차단·권리 확정 절차·스킬 버전 검증 결과

- 사용자 승인 범위에서 미확정 위임 자료의 신규 native 생성·별도/embedded 설치·ZIP 배포를 차단했다. 원본과 기존 설치 데이터는 보존한다. Git archive의 알려진 자료 경로도 export-ignore로 제외하지만 raw clone·수동 복사·기존 공개본을 회수하는 장치는 아니다. CI는 ZIP 업로드 대신 배포 거부를 검사한다.
- docs/third-party-clearance.md에 구성요소별 미확정 근거, 권리자/권한·정확한 revision/파일 해시·허용 행위/채널·조건·보호된 증빙·검토 결론을 확인하는 절차를 추가했다. 허가를 새로 취득하거나 제3자 자료에 MIT를 부여하지 않았다. 증빙 JSON이나 사용자 옵션만으로 배포를 해제하지 않는다.
- 코어 native fef-coding/fef-rca는 metadata.version 문자열 1.0.0, standalone fef-claude는 기존 name/description frontmatter를 유지한 본문 1.0.0을 제공한다. 플러그인 소스/생성본은 제거된 기능을 반영한 2.0.0이며 docs/skill-versions.md에 범위·변경 기준·호환성을 기록했다. 스킬 호출 ID·설치 manifest v1·검증 상태 v1은 유지하고 제3자 원본은 재버전하지 않았다. per-skill 자동 업데이트/설치 잠금 기능을 추가하지 않았다.
- 배포 정책4개 및 부모 targeted4개 통과, owned skill quick_validate 2개 통과, 공식 CLI strict manifest 검증 통과. 로컬 독립 리뷰에서 확정 P0–P3 지적 없음. 외부 Claude로 현재 누적 diff를 전송하지 않았다.
- Windows 전체는 명시 FEF_GIT_EXECUTABLE 설정으로 main224개(218통과/2FAIL/2ERROR/2skip,3938.464초), delegation53개(51통과/2skip,81.833초)를 실행했다. 합계277개/269통과/4실패·오류/4skip. Skip은 symlink 권한 WinError1314다. repository·payload89·위임 validator·deterministic evidence·보관 이력·diff 검사 모두 exit0. 최초 로그가 종료 때만 기록되던 하네스의 11분 중단은 미완료로 별도 보존했고 실시간 로그/즉시 baseline 저장으로 재실행했다.
- 새 문서2개를 test_default_install_keeps_runtime_docs_only 기대 목록에 빠뜨린 결함을 수정했다. 설치기 전체72개 재검증은70통과/2skip(150.422초). 나머지3건은 Git repository 15초 timeout1개와 native Python 실행 부모30초 timeout2개였다. 동일 제한·동일 명시 Git 경로로 해당3개 재검증은3/3통과(216.264초). 최초 실패를 지우거나 전체 재실행이 완전 통과했다고 표현하지 않는다. 제품 timeout/PATH/검증 판정은 완화하지 않았다.
- 전체 실행 중 저장소454파일·HEAD77f447e9bb673fc4bd68f6bea1b3559964004ddf·사용자 CLAUDE.md는 동일했다. 사용자 settings.json은15495바이트/59f9e86b…에서15104바이트/a3a88ebe…로 변했으며 작성 주체는 미확정이다. 부모·runner는 이 파일을 쓰거나 복원하지 않았다. 후속 재검증 동안 settings 해시는 동일했고 FEF Git 경로·코어 활성·synced 비활성 설정은 유지됐다. 최종 fixture와 이 마감 문서는 전체 실행 이후 변경이다.
- 초기 자동 승인 검토에서 거절된 시스템 전역 WPR CPU 추적은 사용자의 명시적 위험 인지·관리자 세션 승인 뒤 실행했다. 전용 TaskForgeApproved20261024 세션을 시작·종료했고 stop_exit0. 수집 구간68초/8,811,192이벤트/유실0, 원본441,450,496바이트는 checkout 밖 로컬 증거에만 보관한다. 외부 전송 없음. tracerpt 로컬 변환 exit0이며 설치기 follow-up 일부와 겹쳤음을 별도 기록했다.
- WPR 중 ABBA 순서 Git wrapper4회/직접4회 모두성공·timeout0. 호출 전체 중앙값은2.3297초/1.3317초, Git Trace2 내부 시간은0.101038–0.177794초였다. 이8개 표본은15초 실패를 재현하지 않았으며 OS 원인·CPU 스택 귀속은 확정하지 않았다. WPA 미설치 상태에서 스택 분석·보안 예외·추가 시스템 튜닝을 하지 않았다.
- 증거는 checkout 옆 validation-20261024-release-gate의 summary.json, followup_summary.json, 명령별 로그 및 wpr-local에 있다. 로컬 candidate는89파일/2.0.0으로 준비했으나 사용자 운영본은 기존1.3.2-local.20261024 그대로다. 새 실제 모델 세션·운영 갱신·새 원격CI·커밋·푸시는 하지 않았다. 제3자 허가와 Windows 안정적인 전체 통과는 미확정이다.

## 2026-10-24 기존 코딩 지침의 최소 구현·변경 소유 범위 보완

- 별도 스킬이나 플러그인을 추가하지 않고 modules/Coding.md 및 skills/fef-coding/SKILL.md에 두 원칙을 같은 문구로 반영했다. 현재 완료 기준에 필요한 기능·옵션·추상화만 추가하고 기존 코드를 재사용하며 신뢰 경계의 입력 검증·실패 처리를 유지한다. 이번 변경으로 미사용이 된 코드만 정리하고 기존의 무관한 미사용 코드는 유지·별도 보고한다.
- 호환되는 지침 명확화로 coding 스킬1.0.1, native plugin2.0.1로 갱신했다. RCA와 standalone 진입점은1.0.0 유지하되 standalone에 복사되는 Coding 모듈에는 보완 지침이 포함된다. docs/skill-versions.md에 고정 참조 revision2c60614와 변경 범위·호환성을 기록했다. 외부 플러그인·원문 파일을 설치/복사하거나 새 권리를 부여하지 않았다.
- 기존 생성기로89파일 중4파일을 갱신했다. 원본·생성본4쌍 바이트 일치, 시작 시454파일 기준 제품 변경8파일 외446파일 동일을 확인했다. 플러그인 manifest 변경 키는version뿐이며 호출 ID·시장 이름·라우트·Kernel·훅·설치 manifest/검증 state v1은 유지했다. 이 마감 기록은 제품 검증 후 별도로 추가했다.
- 원본/생성 코딩 스킬 quick_validate2개 통과. Windows 명시 FEF_GIT_EXECUTABLE 자식 설정에서 build/runtime16개 통과(81.528초), installer/framework/latency/context85개 중83통과·2skip(139.802초): 합계101개 중99통과·2skip·실패/오류0. Skip은 Windows symlink 권한 제한이다. 문구를 그대로 비교하는 테스트를 새로 만들지 않고 기존 생성·설치 무결성·호출 호환성 회귀를 실행했다.
- repository validator·생성89파일 --check·diff 검사 모두exit0. 독립 로컬 리뷰에서 P0–P3 확정 지적 없음. 이번 전용8파일 diff만 검토했고 누적 이전 변경의 재검증으로 주장하지 않는다. 원시 로그·전후 기준·전용 diff·scope-report는 checkout 옆 validation-20261024-coding-guidance에 있다.
- 테스트 전후 HEAD77f447e9bb673fc4bd68f6bea1b3559964004ddf 및 사용자 settings.json·저장소 CLAUDE.md 해시 동일. 전역 설정·운영 설치·새 실제 모델·전체277회귀·원격CI·커밋·푸시는 수행하지 않았다. 지침의 실제 모델 준수 효과와 기존 Windows 간헐 지연 원인, 제3자 재배포 권한은 이번 검증으로 확정하지 않는다.


## 2026-10-24 Ponytail 고정 소스 분석과 선택적 지침 보강

- DietrichGebert/ponytail revision09c434ab73ca43761c5d8b0c5d341926c2fba710(package/plugin5.3.2)의 tracked 일반 텍스트161파일/971,898바이트를 정적 검토했다. 설치기·훅·upstream 테스트·모델 벤치마크는 실행하지 않았다. MIT 저작권/고지 조건을 확인했으며 원문 런타임·전체 프롬프트를 가져오지 않았다. 기존 별도 제3자 자료 권한을 확정하거나 배포 차단을 해제하지 않았다.
- upstream CSV의 물리적 개행 분할로 인한 동일 키 다중행 갱신 손상, 프로젝트 원장의 비동기 read/modify/write 및 read 오류 빈 원장 대체, benchmark compare/run의 실패 분모 차이를 정적 경로와 구체 조건으로 기록했다. 실제 운영 재현이나 공개 성능 수치 오류로 단정하지 않았다. 상세 근거·고정 링크·비도입 범위는 docs/ponytail-assessment-2026-10-24.md에 있다.
- 기존 Coding 모듈/스킬에 프로젝트 추상화→표준 기능→설치된 의존성 검토 순서를 추가하되 호환성·보안·접근성을 유지하도록 했다. 기존 CodeChangeReviewer에 연결 실행/실패 경로 및 사례·영향·최소 수정 근거를 보강했다. 기존 Mod 평가 절차에는 동일 도구/권한/검증 래퍼·캐시 조건, 실패·결측 표본의 명시적 분모와 원시 결과 보존을 추가했다. 새 스킬·의존성·대시보드·webhook·상태 원장은 추가하지 않았다.
- coding1.0.2/plugin2.0.2로 호환 패치 갱신했다. 기존 생성기로 리뷰어 inline과89파일 payload를 동기화했으며 변경7쌍 바이트 일치다. RCA/standalone 진입점1.0.0, 호출ID·라우트·권한·훅·state v1·Kernel은 유지한다. 검증 후 기준454파일 중14파일 변경·440파일 동일·누락0, source-only 분석 문서1개 추가를 확인했다. 이 마감 기록은 검증 후 별도로 추가했다.
- 원본/생성 coding skill quick_validate2개 통과. Windows 자식 프로세스에만 FEF_GIT_EXECUTABLE 명시 경로를 설정하여 build/runtime16개 통과(143.276초), install/framework/latency/context85개 중83통과·2skip(181.702초): 합계101개 중99통과·2skip·실패/오류0. Skip은 WinError1314 심볼릭 링크 권한 제한이다. repository validator·생성89파일 --check·diff 검사 exit0; diff 검사에는 기존 PROGRESS.md LF→CRLF 경고가 있다. Golden Tests31개는 인덱스 검사이며 실제 모델 실행이 아니다.
- 독립 로컬 code-change-reviewer에서 수정 필요 지적 없음. upstream 세 가지 근거와 생성본을 교차 확인했다. HEAD77f447e9bb673fc4bd68f6bea1b3559964004ddf, 사용자 settings.json 및 저장소 CLAUDE.md 해시 전후 동일. 원시 로그·전용 diff·scope-report·요약은 checkout 옆 validation-20261024-ponytail-adoption에 보관한다. 전체277회귀·새 실제 모델·upstream 실행 재현·전역 설치/운영 배포·외부 diff 전송·원격CI·커밋·푸시는 수행하지 않았다. 실제 효능/절감, 기존 Windows 간헐 지연 원인과 제3자 재배포 권한은 미확정으로 남긴다.


## 2026-10-24 upstream 개선 검토의 지속 유지보수 절차 등록

- 사용자 요청에 따라 TaskForge 소스를 추가/변경/업데이트하는 작업 묶음마다 Ponytail과 andrej-karpathy-skills의 기본 브랜치 HEAD를 읽기 전용으로 확인하고 마지막 검토 revision 이후를 선별 검토하도록 docs/upstream-review-policy.md에 등록했다. 초기 검토 기준은 각각09c434ab73ca43761c5d8b0c5d341926c2fba710/2c606141936f1eeef17fa3043a72095b4765b9c2이며 최신 원격 HEAD라는 주장은 아니다. 새 가치가 없으면 불필요한 제품 변경을 만들지 않고 결과를 기록한다.
- 유효한 호환 개선은 기존 코딩/리뷰 지침에 우선 반영하고, 채택/거부/보류 이유·고정 출처·실제 검증과 제한을 기록하도록 했다. 네트워크/검증 불가 시 기존 검토 기준을 유지한다. 아키텍처/API/스키마/운영/보안/데이터 삭제 등 기존 승인 요건, 제3자 권리 확인, 비공개 diff 외부 전송 제한, 커밋/푸시/설치/배포 권한은 완화하지 않았다. 별도 스킬·상시 프로세스·예약 자동화는 추가하지 않았다.
- AGENTS.md와 CLAUDE.md에 TaskForge 소스 유지보수일 때만 적용하는 짧은 포인터를 추가했다. 기존 역할/검증/설치 동작은 유지하며 AGENTS 중복 문구를 축약했다. 초기 초안 byte 검사5673/5529는5500 제한을 초과했으나 최종5491바이트(정규화 측정5392바이트/~1348토큰)로 제한을 충족했다. Kernel 본문은 유지했다.
- 최초 설치 회귀85개 중81통과/2실패/2skip으로 source-only 문서 누락 참조를 재현했다. 문구 검사나 테스트를 약화하지 않고 문서를 설치 allowlist와 검증기 필수 문서 집합에 포함하고 기존 정확한 파일 목록 fixture를 갱신했다. 설치본에서도 TaskForge 소스 유지보수에만 적용되는 조건은 유지한다. plugin2.0.3과 생성90파일을 동기화했으며 스킬 버전·호출ID·라우트·훅·state v1은 유지했다.
- 수정 후 실패 targeted2개 통과(14.923초). install/framework/latency/context85개 중83통과·2skip(102.446초), build/runtime16개 통과(77.602초): 관련 회귀101개 중99통과·2skip·실패/오류0. Skip은 WinError1314 심볼릭 링크 권한 제한이다. repository validator·90파일 --check·diff 검사exit0; Golden Tests31개는 인덱스 검사이며 실제 모델 실행은 아니다. 기존 PROGRESS.md LF→CRLF 경고는 남는다.
- 초기3파일 작업 지침의 독립 로컬 리뷰는 수정 필요 지적 없었고, 이후 설치 참조 수정은 메인 diff 검토와 위 회귀로 확인했다. HEAD와 사용자 settings.json/저장소 CLAUDE.md 해시는 테스트 전후 동일하다. 초기 실패와 재검증 원시 로그·전용 diff는 checkout 옆 validation-20261024-upstream-policy에 보존한다. 운영 설치·외부 모델 전송·실제 모델 효능·전체277회귀·원격CI·커밋·푸시는 수행하지 않았다. 자동 검토는 향후 소스 변경 작업에 적용되는 에이전트 지침이며 무인 동기화/자동 merge나 권리 부여를 보장하지 않는다.


## 2026-10-24 누적 최종 리뷰 및 Windows 전체 회귀

- 누적 코드·문서·설치/배포 차단·생성 배포본을 로컬에서 교차 검토했다. 초기457파일은 네 번의 전체 실행 동안 바이트 변경이 없었고, 코드 리뷰에서 추가 P0–P2 런타임 결함은 확인하지 못했다. 생성90파일은 원본과 정합하며, 기술ID·호출·라우트·state/설치 manifest v1·Kernel은 유지했다. plugin2.0.3/coding1.0.2/RCA·standalone1.0.0은 그대로다.
- 확인된 문서 불일치를 scripts/README.md와 README.en.md에서 수정했다. 신규 위임 설치/ZIP 차단과 기존 설치의 읽기 전용 --check 예외, ZIP 비교 대신 차단을 검사하는 CI, 고정 시점의 권리 확인 실패와 미확정 재배포 상태를 구분했다. 보존된 v1.3 소스를 현재 운영 배포본으로 오인하지 않도록 표현을 정리했다. 원본·이력·기존 누적 변경은 보존했다.
- Windows 기본 설정(FEF_GIT_EXECUTABLE 자식 환경에서 해제) 전체277개는273통과/4skip/실패·오류0이다. main224개222통과/2skip(2489.549초), delegation53개51통과/2skip(59.048초)다. 명시 Git 경로(C:/Program Files/Git/mingw64/bin/git.exe) 전체277개는272통과/1실패/4skip/오류0이다. main224개221통과/1실패/2skip(1594.437초), delegation53개51통과/2skip(84.321초)다. Skip은 Windows symlink 생성 권한 제한이다.
- 명시 경로 실패는 tests/test_hooks.py:183의 ignored-submodule 테스트에서 Stop snapshot의 Git 인덱스 조회가 기존15초 제한을 넘겨 stderr 진단을 출력한 것이다. 루트/하위 저장소 중 어느 호출인지와 OS 근본 원인은 미확정이며, submodule digest 결함이라고 단정하지 않는다. 판정·15/30초 제한을 완화하거나 오류를 숨기지 않았다.
- 동일 테스트를 기본→명시→명시→기본 순서로 독립 실행한4회는 모두 통과했다(146.906/89.187/86.847/151.796초). 자식 Git에만 적용한 로컬 Trace2에서 각89개 Git 시작/정상 종료와 짧은 내부 index region을 확인했으나 전체 실행의 실패는 재현하지 못했다. temp fixture의 root 표시는 하위 모듈 재귀 여부를 증명하지 않으며 Trace2 시작 전/프로세스 바깥 지연도 제외할 수 없다. 이 단독 통과로 전체 실패를 해소 또는 안정화했다고 주장하지 않는다. 시스템 전역 추적·외부 전송은 하지 않았다.
- 문서 수정 후 repository validator, 생성90파일 --check, diff 검사, delegation 형식·evidence --check·Git 이력/복원/fsck 검사를 모두 exit0으로 확인했다. 새 격리 --dest 설치 및 --check도 exit0이며 scripts/README.md·README.md·README.en.md 설치본이 원본과 바이트 일치한다. diff에는 기존 PROGRESS.md LF→CRLF 경고만 남았다. Golden 인덱스/fixture는 실제 모델 실행이 아니다.
- upstream 두 원격 HEAD는 기존 검토 기준 Ponytail09c434ab73ca43761c5d8b0c5d341926c2fba710 및 andrej-karpathy-skills2c606141936f1eeef17fa3043a72095b4765b9c2와 동일하여 새 채택 변경은 없었다. 원시 로그·초기 실패·ABBA 집계·전후 해시·설치 증거는 checkout 옆 validation-20261024-cumulative-final에 보존했다.
- HEAD77f447e9bb673fc4bd68f6bea1b3559964004ddf와 사용자 settings.json·저장소 CLAUDE.md 해시는 전후 동일하다. 이번 묶음은 README2파일과 이 이력만 수정하며 기존 누적 변경을 유지한다. 운영본1.3.2-local.20261024 갱신·실제 모델/PPT·새 원격CI·외부 diff 전송·커밋·푸시는 하지 않았다. 제3자 재배포 권한, 명시 경로 전체 회귀의 간헐 timeout 원인 및 Windows symlink 권한으로 생략한 동작은 미확정/미검증으로 남긴다.


## 2026-10-24 AI-Harness 업데이트 재검토·검증 증거 명확화

- 사용자 요청으로 AI-Harness ac4c59adcced5484c9e9c7952b5794c880838a97→45664d315faa13aab71f3b01bf270d50a42f4906의18커밋·변경32경로 및 최신33파일 snapshot을 비교했다. 별도 참조 저장소와 고정 소스 사본을 사용하고 upstream 코드·설치기·테스트·MCP를 실행하지 않았다. 에이전트 frontmatter·실제 command/gate·훅·테스트/CI·Apache-2.0 LICENSE 추가를 확인하여 최초 검토의 미구현/라이선스 부재 지적을 과거 revision 한정으로 명확히 했다. 상세 고정 출처·채택/보류표는 docs/ai-harness-assessment-2026-10-24.md에 추가했다.
- 최신 gate의 exit0→PASS는 테스트 의미·0건/전부skip을 구별하지 않고, attestation 명령 고정은 선택이며 CI는 attestation0개도 허용한다. read receipt/해시는 이해·검증 적합성·권한을 증명하지 않고 패턴 가드는 OS 보안 경계가 아니다. 코드 분기/fixture/CI의 정적 확인이며 실제 호스트·공격 재현 주장은 아니다. 원본 LICENSE 추가로 별도 보존 자료의 재배포 권한이 확정되지는 않는다.
- 유용한 부분만 독자 문구로 기존 Coding 모듈/native coding 스킬과 Review 정책/CodeChangeReviewer에 반영했다. 의도한 동작을 실행한 명령·최종 요약·가능한 실행/실패/skip 수·원시 로그를 확인하고, 로컬 attestation 대신 실제 CI 필수 작업/명령을 점검하도록 했다. 기존 handoff/lesson/PPT와 중복되는 항목은 다시 추가하지 않았다. 새 스킬·Node/Bash/jq runtime·상태 원장·해시 체인·권한/보안 정책·CI 변경은 없다.
- coding1.0.3/plugin2.0.4 호환 패치 및 생성90파일 중7파일을 동기화했다. 원본/생성7쌍과 reviewer inline을 독립 리뷰에서 확인했으며 수정 필요 지적은 없었다. RCA/standalone entry1.0.0, 기술ID·라우트·Kernel·검증 래퍼/훅·state/설치 manifest v1은 유지한다. 지침을 그대로 따라 읽는 문자열 테스트나 새 런타임 테스트는 추가하지 않고 기존 배포/설치/프레임워크/예산 회귀를 실행했다.
- Windows 자식 FEF_GIT_EXECUTABLE 명시 경로에서 build9개 OK(37.524초), runtime7개 OK(22.943초), install72개 중70통과/2skip(104.099초), framework5·latency5·context3개 OK다. 합계101개 중99통과/2skip/실패0이며 skip은 symlink 권한 제한이다. build9개 직후 실행 도구의 skip 요약 파싱 오류로 해당 child exit/전체 walltime을 보존하지 못했고 재실행하지 않았다. 나머지5개 suite와 repository validator·생성 --check·diff 검사 exit0은 기록됐다. 원본/생성 coding quick_validate2개 통과다. 최초 wrapper 오류와 원시 로그를 보존하고 Python으로 원문 요약을 재확인한 verification.json을 최종 집계로 사용한다.
- 이전 누적 작업트리457파일을 기준으로 이번 소유 변경은15파일과 검증 후 추가한 이 이력뿐이다. 기존 누적 변경·미확정 자료 배포 차단을 유지했다. HEAD77f447e9bb673fc4bd68f6bea1b3559964004ddf 및 저장소 CLAUDE.md·settings는 유지한다. 사용자 settings의 최종 해시는 이전 누적 검증값과 같지만 이번 runner의 초기 출력은 축약되어 독립적인 전후 해시 증거로 주장하지 않는다. 원시 증거·scope·소스 사본은 checkout 옆 validation-20261024-ai-harness-update에 있다.
- 유지보수 정책에 따른 Ponytail/andrej-karpathy-skills 원격 HEAD는 기존09c434ab73ca43761c5d8b0c5d341926c2fba710/2c606141936f1eeef17fa3043a72095b4765b9c2와 동일하여 추가 채택은 없었다. 이번 전체277회귀·upstream 실행·실제 모델/PPT·운영 설치·외부 diff 전송·새 원격CI·커밋·푸시는 하지 않았다. 기존 Windows 간헐 index timeout, symlink 미검증, 제3자 권리·실제 모델 효능은 이 지침 변경으로 해소됐다고 보지 않는다.


## 2026-10-24 첫9건 종료 코드 보완·AI-Harness 포함 누적 Windows 전체 검증

- 사용자 요청에 따라 이전 AI-Harness 반영 검증에서 exit가 누락된 build9건을 별도 재실행했다. test_build_plugin.py9개 모두 OK(73.850초), 실제 child returncode0/wall76.004초를 원시 로그와 runs.json에 저장했다. 이전 누락 기록을 소급해서0으로 바꾸지 않고 이번 후속 증거로 보완했다. 새 로컬 검증 helper는 subprocess 종료 직후 returncode/시간을 먼저 원자 저장하고 이후 선택 요약을 파싱하므로 요약 오류가 종료 코드 기록을 지우지 않는다. 제품 런타임 변경은 없다.
- 최신 plugin2.0.4/coding1.0.3 및 기존 누적 코드·문서·생성90파일을 포함한 작업트리를 동결했다. 기본 Windows 자식 환경에서 FEF_GIT_EXECUTABLE을 해제한 main224개는222통과/2skip/실패·오류0(2370.468초, exit0), delegation53개는51통과/2skip/실패·오류0(54.417초, exit0)이다. 합계277개273통과/4skip/실패·오류0이다.
- 명시 FEF_GIT_EXECUTABLE=C:/Program Files/Git/mingw64/bin/git.exe의 main224개는222통과/2skip/실패·오류0(1394.155초, exit0), delegation53개는51통과/2skip/실패·오류0(53.365초, exit0)이다. 합계277개273통과/4skip/실패·오류0이다. 명시 main에만 자식 Git Trace2를 로컬 적용했으며 env/config 값 캡처 옵션은 제거했다. 전역 환경·시스템 전역 추적·외부 전송은 변경/실행하지 않았다. 두 환경의4skip은 Windows symlink 생성 권한 제한이다. 첫9건은 별도 반복 검증이며 전체277건에 새로운 고유 테스트로 더하지 않는다.
- 이전 명시 경로에서 실패했던 ignored-submodule 테스트는 두 main 원시 로그에서 모두 ok임을 메인이 확인했다. 이번 전체 실행에서는15초 index timeout이 재현되지 않았다. 다만 이전 실패와 ABBA 증거는 그대로 보존하며, 이번 각1회의 전체 통과/계측으로 OS 근본 원인 해소·장기 안정성을 보장하지 않는다. 기존15/30초 제한·오류 처리·판정·테스트는 변경하지 않았다. Trace2의 revision 조회/비저장소 오류 및 줄바꿈 경고 이벤트는 unittest 실패와 구분하며 로그를 로컬 보존한다.
- 전체 후 repository validator, 생성90파일 --check, delegation format·deterministic evidence --check·Git history 복원/해시/fsck, diff 검사6개 모두 실제 exit0이다. Golden31개는 인덱스 검사이고 모델 실행이 아니다. 이번 모든11명령의 실제returncode가0으로 기록됐다. 기존 PROGRESS.md LF→CRLF 안내는 whitespace 실패가 아니다.
- 누적 코드/설치/배포 차단/테스트/CI의 독립 읽기 전용 리뷰에서 추가 actionable P0–P3 결함은 확인하지 못했다. 문서/스킬/생성본 리뷰도 중대한 불일치 없이 source/generated11쌍 해시와 manifest2.0.4를 확인했다. README의2.0.0은 정책 도입 시점의 정확한 역사적 설명이므로 선택적 스타일 변경을 만들지 않았다. 추가 제품 코드 수정이나 버전 변경은 하지 않았다.
- 모든 검증이 끝날 때까지 시작 기준457파일이 바이트 단위로 동일했고, HEAD77f447e9bb673fc4bd68f6bea1b3559964004ddf 및 사용자 settings.json·저장소 settings.json·CLAUDE.md 해시도 전후 동일하다. 검증 후 이 PROGRESS 기록만 추가했다. 기존 누적 변경과 source/배포 제외 정책은 보존했다. 원시 로그·각 실제exit·전후/범위 해시·리뷰 요약·Trace2·마감 요약은 checkout 옆 validation-20261024-post-harness-full에 있다.
- 유지보수 참조 원격 HEAD는 Ponytail09c434ab73ca43761c5d8b0c5d341926c2fba710, andrej-karpathy-skills2c606141936f1eeef17fa3043a72095b4765b9c2로 이전 검토와 같았다. 실모델/PPT·upstream 실행·운영 설치 갱신·외부 diff 리뷰·새 원격CI·커밋·푸시는 하지 않았다. 운영본은 기존1.3.2-local.20261024이며 제3자 재배포 권한은 여전히 미확정이다. symlink 생략 범위와 이전 간헐 Windows timeout 원인을 이번 통과로 해소했다고 보지 않는다.


## 2026-10-25 AI-Harness6bc8e25 업데이트 선별 반영

- 사용자 재요청으로 마지막 검토45664d315faa13aab71f3b01bf270d50a42f4906부터6bc8e252d9295fcb2b7c3420706ff5e4349307f8까지3커밋·변경18경로 및 최신38파일 snapshot을 비교했다. 실제 Git delta·고정 소스와 분석 증거는 checkout 옆 validation-20261025-ai-harness-update에 보존했다. upstream 코드·설치기·테스트·모델은 실행하지 않았다.
- required-test-command.json 추가로 기본 저장소의 핀 부재 지적이 해소됐고, Windows 경로 구분/변환·실제 셸에서의 doctor·연결/오류 테스트·LF 속성이 보강됐다. CLI expected override는pin보다우선하는설계이므로현재CI우회취약점으로단정하지않고 인터페이스/조합검증경계로구분했다. rm가드의여러조건을명령전체에서찾는방식은다른명령의토큰오인·따옴표누락이가능함을 inert ASCII 문자열의Python 정규식 대응 검사로확인했다. 실제 shell/삭제 명령을 실행한 재현은 아니다. 상세고정링크·기존발견갱신·채택/보류는 기존 docs/ai-harness-assessment-2026-10-24.md의6bc8e25절에 추가했다.
- 기존 Coding 모듈/native coding 스킬과 CodeChangeReviewer에 guard/persistence/tool orchestration 변경 시 연결 경로의 관련 정상·거부/실패 사례 및 영향받는 path/shell/default/override 변형 확인을 명확히 했다. ToolExecution은 도구 의존 실패를 진단할 때 실제 선택 interpreter/shell·cwd·환경의 prerequisite을 확인하도록 보완했다. 정상 호출마다 probe를 강제하지 않으며 시뮬레이션/목업과 실제 호스트·모델 검증을 구분한다. 문구는 독자적으로 작성했고 새 skill/runtime/hook/dependency/CI/mutation framework를 추가하지 않았다.
- coding1.0.4/plugin2.0.5로 호환 패치 갱신하고 reviewer inline 및 생성90파일 중7개를 동기화했다. RCA/standalone entry1.0.0, 기술ID·라우트·Kernel·승인/권한·wrapper/훅·state/설치 manifest v1은 유지한다. 새 런타임 로직이 없어 문장을 반복하는 테스트는 추가하지 않고 관련 기존 회귀를 실행했다.
- 최초 위임 실행이 지시한 방식과 달리 restricted sandbox에서 수행되어 build/runtime/install/framework4묶음이 sandbox 임시 경로 WinError3/5 및 cleanup 오류 등으로 실패했다. 도구 출력 세션은 회수되지 않았지만 helper가 실제 returncode를 파싱 전에 파일에 저장해 실패 원시 증거를 회수했다. 제품을 수정하거나 기준/제한을 완화하지 않고 원시 runs.json과 로그를 보존한 채, 실패4묶음만 정상 로컬 도구 실행 방식으로 재검증했다. 무관한 latency/context8개 및 정적 검사 성공은 반복하지 않았다. 검증 도구의 실행 맥락 문제를 제품 결함으로 오인하거나 실패를 삭제하지 않았다.
- 재검증 build9개 OK(151.382초), native runtime7개 OK(54.892초), install72개 중70통과/2skip(288.138초), framework5개 OK(0.346초), 모두 실제exit0이다. 최초 성공한 latency5/context3개와 합쳐 관련101개 중99통과/2skip/실패·오류0이다. Skip은 Windows symlink 권한 제한이다. repository validator·90파일 --check·원본/생성 coding quick_validate2개·diff 검사도 exit0이며 최종 집계 verification.json은 초기 실패와 후속 결과를 구분한다. Golden31개는 인덱스 검사이며 모델 실행이 아니다.
- 독립 로컬 리뷰에서 수정 필요 지적이 없고 source/generated7쌍·inline·상대참조·추가 줄 시크릿 패턴을 확인했다. 테스트 동안 현재 제품457파일은 바이트 동일했고, 사용자 settings·저장소 settings/CLAUDE/AGENTS 해시가 시작값과 같으며 HEAD는 faba43a316f9bc3b117faf820dfb0f9f3495b83b 그대로다. 이번 변경은15파일과 검증 후 추가한 이 PROGRESS만이며 초기 누적 커밋 상태와 범위 밖 파일을 유지했다.
- 유지보수 참조 Ponytail09c434ab73ca43761c5d8b0c5d341926c2fba710 및 andrej-karpathy-skills2c606141936f1eeef17fa3043a72095b4765b9c2의 원격 HEAD는 기존 검토와 같았다. 전체277회귀·새 실모델/PPT·upstream 실행·운영 설치·외부 diff 전송·새 원격CI·커밋·푸시는 수행하지 않았다. 직전faba43a의 전체 Windows/원격CI 성공은 과거 검증으로 보존하며 이번2.0.5변경의 전체 실행 증거로 확대하지 않는다. 기존 간헐 index timeout 원인·symlink 미검증·별도 제3자 권리·실제 모델 효능은 이번 지침 보강으로 확정하지 않는다.


## 2026-10-25 candidate2.0.5 기본·명시 Windows 전체 회귀 및 누적 최종 리뷰

- 사용자 요청으로 현재16파일 미커밋 변경과 기커밋faba43a를 포함한 누적 코드·문서·생성본을 검토하고 Windows/Python3.14.4에서 기본/명시 설정 전체를 각각1회 실행했다. 시작 전 실제 임시 .claude/agents 파일 생성·읽기를 확인해 직전 restricted sandbox의 임시경로 오류와 구분했다. 메인이 정상 로컬 도구 실행으로 시작했고 각 child 실제exit를 요약 파싱 전에 저장했다. 전역 환경·설정은 바꾸지 않았으며 두 mode 모두 Trace2 없이 실행했다.
- 기본 자식 환경에서 FEF_GIT_EXECUTABLE을 해제했다. main224개216통과/6실패/2skip/오류0(4155.475초, exit1), delegation53개51통과/2skip/실패·오류0(64.070초, exit0): 합계277개267통과/6실패/4skip이다. 전체 통과로 판정하지 않는다.
- 명시 자식 환경 FEF_GIT_EXECUTABLE=C:/Program Files/Git/mingw64/bin/git.exe에서는 main224개222통과/2skip/실패·오류0(1430.732초, exit0), delegation53개51통과/2skip/실패·오류0(59.465초, exit0): 합계277개273통과/4skip/실패·오류0이다. 각4skip은 Windows symlink 생성 권한 제한이다. 순서·호스트 부하를 통제한 성능 실험이 아니므로 시간 차이를 일반 절감률이나 원인 확정으로 사용하지 않는다.
- 기본 실패6건 원문을 보존했다. compound pipeline Stop/status, initial baseline error setup/status, initial state error session-B start/head, cross-session Stop/status, wrapper-change Stop/head의5건은 기존15초 Git timeout으로 확인됐다. parser 거부 로직이 우회됐거나 상태 공유/실패 marker 코드가 고장났다고 단정하지 않는다. missing-plugin-kernel의1건은 load_state가None이지만 assertion에 이미 수집한stderr가 연결되지 않아 원시 원인을 확인할 수 없었다. 초기 실패는 후속 통과로 대체하지 않았다. 기본 PATH는 Git/cmd/git.EXE, 명시는 mingw64/bin/git.exe로 확인했으나 OS/실행 전후 지연의 근본 원인은 미확정이다. 자동 wrapper 우회·재시도·15/30초 제한 증가·판정 완화는 하지 않았다.
- 확인된 진단 누락만 tests/test_hooks.py의 해당 assertIsNotNone에 result.stderr를 전달하는 한 줄로 보완했다. 조건은 그대로다. 기준 전체 실행 동안457파일은 바이트 동일했고 이 수정은 전체/정적 검사 종료 뒤 적용했다. 실제 stderr 가시성을 확인하는 격리 self-check는 원래 lazy module 초기화 누락과 허용 argv와 다른 합성 입력 때문에 실패했으며 그 오류도 보존했다. 두 차례 확인 실패 뒤 Astra 독립 검토로 제품 수정 실패가 아닌 확인 입력 불일치를 확인했다. 정확한status argv에 CANARY를 output/stderr로 넣고, 원본SHA와 일치하는 baseline bytes를 메모리에서만 로드해 같은 마지막 assertion에 도달했는지 비교했다. 원본은 기대exit1/진단 미표시, 수정본은exit0/TimeoutExpired·operation 표시/CANARY 비노출이었다. 실제 Git을 실행한 지연 재현이나 전체 안정성 증거는 아니다.
- 수정 후 실제 missing-plugin-kernel 검사1개를 기본/명시로 각1회 재실행해 모두 통과했다(20.425/14.269초, 실제exit0). 이는 진단 한 줄 수정의 관련 재검증이며 원래 기본 전체6실패 해소를 뜻하지 않는다. 전체는 진단 메시지 수정 후 반복하지 않았고 이전 전체 결과를 최종 파일의 새 전체 통과로 주장하지 않는다. Runtime·스킬·패키지 입력은 바뀌지 않아 plugin2.0.5/coding1.0.4 및 generated90을 유지한다.
- repository validator·generated --check·delegation format/evidence --check/history 복원·diff검사6개는 모두exit0이다. Golden31개는 인덱스 검사다. 77f447e→현재 작업트리의 독립 로컬 코드/계약 리뷰는 확정P0–P2 지적이 없었고 문서 리뷰도 차단 불일치 없이 source/generated·inline·버전·권리/실행 경계를 확인했다. 이 정적 결론과 실행 실패는 별도로 취급한다.
- HEADfaba43a316f9bc3b117faf820dfb0f9f3495b83b, 사용자 settings·저장소 settings·CLAUDE/AGENTS 해시가 기준 전체 실행 전후 같았다. 이번 묶음에서 테스트 진단 한 줄과 이 PROGRESS만 추가로 수정했고 기존16파일 변경 및 범위 밖 파일을 유지한다. 원시10명령·실패상세·보호 해시·before/after self-check·실제2mode targeted·리뷰·최종 범위는 checkout 옆 validation-20261025-cumulative-full-205에 보관한다.
- Ponytail09c434ab73ca43761c5d8b0c5d341926c2fba710 및 andrej-karpathy-skills2c606141936f1eeef17fa3043a72095b4765b9c2 원격HEAD는 이전과 같았다. 새 OS 전역 추적·실제 모델/PPT·운영 설치·외부 diff 전송·원격CI·커밋·푸시는 하지 않았다. 기본 설정의 안정적인 전체 통과, 간헐 Windows timeout의 OS 원인, 원시 진단이 없는1건의 원인, skip 범위와 별도 제3자 재배포 권한은 미해결/미확정이다.


## 2026-10-25 Git 시간초과5건·원인 미확정1건 후속 및 최종 회귀

- 기존6실패를 기본 설정에서 집중 재현해6/6통과(421.406초, exit0/162Git호출)했으나 이전 실패를 해소로 바꾸지 않았다. 이어진 진단 부분 실행에서 실제15초 timeout1건을 확보했다. 상태 복구 테스트 마지막 Stop의 repository 조회가 Git exit/atexit0(t_abs0.244초) 뒤 약14.073초 더 대기하다 timeout했고, wrapper 종료 후 출력 회수는0.075초였다. OS 종료/핸들/실행기 중 원인 귀속은 미확정이다. 정상 후속 표본의 소유 PID 읽기 조회로 Trace2 종료와 OS 종료 완료가 다를 수 있음을 확인했지만 과거 실패 원인으로 소급하지 않았다.
- 확인된 진단 누락만 tests/test_hooks.py 마지막 Stop 결과1회 보관·정제 stderr 기록·기존 stdout assertion 메시지로 보완했다. 경고 유무×stdout 유무4조합의 원래 판정과1회 호출이 같음을 실제 소스 추출 확인(exit0)했다. 관련 실제 테스트1개는 기본/명시 모두exit0(53.705/34.103초). 독립 로컬 코드 리뷰 추가 지적 없음. 기존 missing-kernel assertion 진단도 유지한다. Runtime·기본 PATH·custom wrapper·명시 선택·state v1·15/30초·판정 기준은 변경하지 않았다. plugin2.0.5/coding1.0.4/generated90 유지.
- 최종 기본: 메인224/222통과/2skip(2984.686초), 위임53/51통과/2skip(56.511초), 각각 실제exit0. 명시: 메인224/222통과/2skip(1446.518초), 위임53/51통과/2skip(53.265초), 각각 실제exit0. 설정별277/273통과/4skip, 합계554/546통과/8skip/실패·오류0. 메인 두 설정은 같은 Popen/Trace2 계측이며 직접 Git1133회씩의 timeout은0이다. 모든 네이티브 자손 Popen을 관찰한 수가 아니고, 단일 호스트 관측을 성능·안정성 보장으로 확대하지 않는다. skip은 기존 Windows symlink 권한 제한이다.
- 저장소·generated --check90·위임 형식·evidence·이력·diff6검사 실제exit0. Golden31은 인덱스 검사다. 테스트 중457파일, HEADfaba43a316f9bc3b117faf820dfb0f9f3495b83b, 사용자/저장소 settings·CLAUDE/AGENTS 해시 모두 동일했다. 완료 뒤 기존 지연 문서와 이 이력만 기록한다. 이번 추가 범위는 테스트 진단·기존 지연 문서·PROGRESS이며 이전 누적 변경을 보존한다.
- 진단 도구 오류도 보존: 최초 Popen 함수 교체로 Windows asyncio import8오류가 난45개 불완전 실행과, 진단 수정 전 중단한 timeout 부분 실행은 최종 전체에서 제외했다. 클래스 상속/224개 로딩 사전 확인 뒤 최종 전체를 수행했다. 최종 기록기의 runs.json 교체 WinError5는 명시 메인exit0 저장 후 발생(helper exit1)했다. 원본 actualexit0/224개 OK 로그를 보존·대조했다. 읽기 핸들로 replace를 막는 합성 재현은 같은WinError5, 닫은 뒤 교체exit0이었으나 정확한 차단 행위자는 미확정이다. 조회기를 중단하고 결과 JSON 조회를 종료 flag로 대체했다. 완료한 메인은 반복하지 않고 남은 위임+정적7명령만 별도 기록기로 완료(helper exit0)했다. 단위 판정을 바꾸거나 정상 결과를 고르기 위한 반복은 하지 않았다.
- 근거: checkout 옆 validation-20261025-git-timeout-followup, validation-20261025-git-timeout-full-v2, validation-20261025-git-timeout-final. 마지막 디렉터리의 verification-summary.json, runs-before-recorder-recovery.json, runs-normalized.json, remaining-runs.json, tested-source-check.json, protected-check.json에 원시/복구 집계를 구분했다. 상세 방법·공식 API 출처·원인 한계는 docs/windows-git-latency-2026-10-23.md 후속 절을 참조한다.
- 기본 단일 전체는 통과했으나 간헐 지연의 안전한 runtime 수정이나 안정적인 연속 통과는 입증하지 못했다. 과거 stderr가 없는1건도 원인 미확정이다. 자동 Git 우회·재시도·부분출력 성공 인정·제한 증가·판정 완화·전역/보안 설정 변경은 하지 않았다. 참조HEAD Ponytail09c434a/Karpathy2c60614는 기존과 같았다. 새 시스템 전역 추적·다른 OS/모델·PPT·운영 설치·외부 diff 전송·원격CI·커밋·푸시 없음.


## 2026-10-25 실패 시점의 프로세스·출력 핸들 추적 후속

- 실제15초 Git 실패는 이번에 재현되지 않아 원인 확정/해결로 처리하지 않는다. 기준 HEADfaba43a316f9bc3b117faf820dfb0f9f3495b83b와 기존18파일 미커밋 변경을 보존했다. 제품 runtime·기본/명시 Git·15/30초·assertion·state v1은 변경하지 않았다.
- 자식 환경에만 적용하는 로컬 진단기로 TimeoutExpired의 원본 발생 줄(stdout/stderr reader, stdin writer, process wait), 종료 요청 전 자신의 프로세스 신호·출력 reader/캐시 핸들 속성·버퍼 길이·스택(로컬 변수 제외), read/close 시각을 수집한다. 출력 본문·원문 명령/환경은 저장하지 않으며 writer 핸들을 복제하지 않는다. Python3.14.4 private 구현과 비원자적 관측에 한정한다. PeekNamedPipe의 동기 멀티스레드 블로킹 위험 때문에 사용하지 않았다.
- 로컬 독립 리뷰에서 확인된 진단기2결함을 보완했다: 진단 저장/조회 오류가 원래 결과·예외·kill을 덮지 않도록 격리하고 불완전 표식으로 분리; 닫힌 핸들 번호의 재사용/객체 동일성 오인을 방지. 합성15초 대기3종 검사exit0, 오류 주입5검사exit0. 첫 오류 주입 검사의 Windows CRLF 가정 실패는 보존하고 동일 자식 환경의 원본 부모 Popen 결과와 정확 비교해 정정했다. PID만 대응한 초기 분석도 보존하고 생성/완료 시각·인스턴스로 보완했다. 진단 수정 전 중단한 부분 전체는 최종 결과에 넣지 않았다. 제품 결함을 확인해 runtime 수정한 것은 아니다.
- 실제 기본 Git200회는 첫 timeout에서 중단/재시도 없는 고정 예산으로 실행해 timeout0/exit0. 최종 메인 관측 Git은 설정별1175회(15초 대상939회), 관측 timeout/reader오류0. 가장 느린 정상 communicate3.450초 중 read반환3.449초/닫힘 이후반환0.000927초였으나 과거15초 실패의 증거가 아니다. pipe/임시파일 AB/BA/BA/AB16회는 exit0/출력·오류 해시 동일; status중앙값1.787/1.771초, HEAD1.696/1.781초로 파일 캡처의 일관된 개선을 관측하지 못해 제품 캡처 방식은 유지했다.
- 최종 기본: 메인224/222통과/2skip/2198.565초, 위임53/51통과/2skip/51.279초. 명시: 메인224/222통과/2skip/1456.194초, 위임53/51통과/2skip/56.491초. 모두 실제exit0/실패·오류0. 합계554/546통과/8symlink권한skip. 정적6검사도 실제exit0이며 generated90 동기화/Golden31인덱스(실제 모델 아님)를 확인했다.
- 설정별 관측 Python 메인54개·위임25개 완료 표식 모두 존재/진단오류0. 각 설정의 자식 호출 중 메인18개·위임24개 내부는 PYTHONPATH 제거/-I/-S 격리로 미관측이며 부모 경계만 관측했다. PID+시각으로 대응한 authoritative자료를 사용해 PID재사용 오인을 피했다. source457/HEAD/사용자·저장소설정/CLAUDE/AGENTS는 전 단계 동일. 완료 뒤 이력과 기존 windows지연 문서2파일만 기록한다. plugin2.0.5/coding1.0.4/payload90 유지.
- 근거는 checkout 옆 validation-20261025-exit-pipe-state(v1실험·200회·중단기록), validation-20261025-exit-pipe-state-v2(최종도구·합성검사·554회귀·비교·완료표식·invocation별coverage·verification-summary)에 보존한다. 상세 방법/공식 출처/한계는 docs/windows-git-latency-2026-10-23.md 최신 절을 참조한다. 실제 실패 시점의 새 핸들 상태와 과거 진단 누락1건은 미확정이다. 새 전역추적·운영설치/설정변경·실제모델/PPT·외부diff·원격CI·커밋·푸시 없음. 유지보수 참조 HEAD09c434a/2c60614는 이번에도 기존과 같았다.

## 2026-10-25 사용자 안내 언어 통일

- 사용자·유지관리 문서는 한국어, 영문 소개는 README.en.md, 에이전트 실행 지침과 자동 검사기가 읽는 loading-map은 영어로 구분했다. 기여 안내에도 같은 기준을 명시했다. 과거 검증 기록·제3자 원문·법적 원문과 명령·설정 키·경로·식별자는 보존했다.
- 설치·Claude Code/Projects·FAQ·모델/컨텍스트·평가·권리 확인·참조 저장소 유지관리·버전·기여/릴리스 안내를 정리하고, 기존 제목 앵커를 보존했다. 영문 README는 한국어 기본 README와 구성을 맞추고 상세 안내의 언어를 표시했다.
- 플러그인 사용자 설명과 생성 README를 한국어로 통일하고 로컬 플러그인 버전을 2.0.6으로 갱신했다. coding 1.0.4, RCA/독립 설치 진입점 1.0.0, fef-engineering@fef-marketplace 및 기존 호출·저장 상태는 유지했다. 공개 식별자 이름 변경이나 운영 재설치는 수행하지 않았다.
- 참조 저장소 HEAD는 Ponytail 09c434ab73ca43761c5d8b0c5d341926c2fba710, Karpathy 기반 스킬 2c606141936f1eeef17fa3043a72095b4765b9c2로 기존 검토 기준점과 같았다. 신규 외부 코드나 스킬은 가져오지 않았다.
- 최초 검사에서는 문서 편집 중 생성본 차이, 영문 제목/고정 입력을 전제로 한 latency 1건·framework 2건 실패가 있었다. 해당 검사 문구를 한국어로 갱신하고, 독립 문서 검토와 전체 사용처 확인에서 발견한 리팩터링 용어 치환 오타를 바로잡았다. 검증 기준의 의미나 제한 시간은 낮추지 않았다.
- 최종 관련 회귀: adaptive effort 21/21, latency lightness 5/5, framework validation 5/5 통과. 생성기 9/9, 플러그인 런타임 7/7도 통과하여 관련 테스트 총 47건 통과. 저장소 통합 검증 exit 0(라우트 10개, Golden Test 31개 메타데이터 검사; 모델 실행 아님), 생성본 90파일 동기화 검사 exit 0, git diff --check exit 0. 사용자 문서 22개에서 로컬 제목 링크 6개를 검사해 오류가 없었다.
- 독립 검토 범위는 주요 사용자 안내·호환성·검증 문구이며 저장소 전체 보안 리뷰를 뜻하지 않는다. Windows 전체 회귀, 실제 모델, 외부 링크의 최신 사실, 운영 설치는 이번 언어 변경에서 재실행하지 않았다. Git의 LF→CRLF 예정 안내는 공백 검사 실패와 구분한다. 누적 코드·진단 변경을 보존했으며 커밋·푸시는 하지 않았다.

## 2026-10-25 approved TaskForge native identity and English operational docs

- User approved the native plugin/marketplace/call rename: taskforge-for-claude@taskforge-marketplace, /taskforge-for-claude:coding and /taskforge-for-claude:rca. Plugin candidate is 3.0.0; both native skill interface versions are 2.0.0. Canonical skill directories and generated payload moved to skills/coding, skills/rca and plugins/taskforge-for-claude. The append-only rename chain remains fef-claude -> fef-engineering -> taskforge-for-claude. No old qualified-call aliases or automatic cross-marketplace migration are promised.
- Latest language direction supersedes the preceding Korean operational-doc candidate: shared instructions, operational docs and code explanations are English; the primary README remains natural Korean, with an English overview. Commands, configuration keys and Korean test inputs are retained except for the explicitly approved native ID changes. Historical records and third-party originals were not rewritten.
- Automatic approval rejected an unguarded 21-file HEAD restoration. A read-only comparison then proved all 21 original blobs equal their pre-language hashes in the existing 457-file verification baseline. The guarded, separately approved operation backed up all current text under ../validation-20261025-taskforge-rename/language-backup before restoring only those language changes. Release/roadmap clarifications and the new language policy were retained in English. Version-history additions and accumulated code changes were preserved separately. This was not a repository reset.
- Existing standalone fef-claude, .fef-manifest.json schema v1, verification state v1, FEF_GIT_EXECUTABLE and other configuration keys/result markers are unchanged. Ten settings/entry/routing/installer/state/hook files retained their pre-language SHA-256 values. Five accumulated coding/reviewer/AI-Harness files and the final Windows investigation record also retained their verified bytes. Native skill instruction bodies retain the prior clarifications; the public name/version/header changed.
- Migration docs require an independently usable old payload/settings backup, an isolated check, stopping on same-source registration conflicts, disabling all applicable old copies before the new active install, and reviewing scoped settings/prompts/reviewer references. No real-user cutover, uninstall, cache deletion or credential change was performed.
- Upstream HEAD checks matched the reviewed Ponytail 09c434ab73ca43761c5d8b0c5d341926c2fba710 and Karpathy-inspired 2c606141936f1eeef17fa3043a72095b4765b9c2; no new upstream runtime/skill was imported. Local independent review found two active old-path references, now fixed and regenerated. Scoped re-review confirmed the fixes and matching source/generated docs.
- Initial installer regression: 72 tests, 2 failures and 2 skips, exit 1; both failures were the primary README's relative hooks/hooks.json link missing from standalone installs. Both README links now use the existing public source URL. The two targeted regressions passed, followed by the full installer suite: 72 run, 70 passed, 2 skipped, exit 0. Other suites: plugin runtime 7, builder 9, adaptive effort 21, latency 5, framework 5, rename/resume state 1, all passed. Unique total: 120 run, 118 passed, 2 skipped; repeated cases are not double-counted. Verbose recheck confirmed both skips are Windows file/directory symlink privilege failures (WinError 1314); the 8.3 short-path case passed.
- Final repository validation, generated-byte check and git diff --check all exited 0. Routes 10 and Golden Test metadata 31 validated; model runs were not executed. Generated payload has 90 files. Git LF-to-CRLF notices are distinct from whitespace failures.
- Actual Claude Code 2.1.310 marketplace and payload validation each exited 0 with advisories: the requested taskforge-for-claude name may appear Anthropic-owned, and the plugin-directory listing icon is missing. These advisories remain documented; no name policy bypass, icon addition, security-scan result or trademark clearance is claimed. An initial output collector failed on CP949 special-character rendering; its UTF-8 rerun completed.
- Isolated CLI fresh add/install/list each exited 0 and listed taskforge-for-claude@taskforge-marketplace 3.0.0. A first collector incorrectly counted an empty legacy directory as a skill. Read-only follow-up confirmed exactly coding/SKILL.md and rca/SKILL.md entrypoints, no files in the uncleared directory, and all 90 source/cache file bytes identical. Three real user settings/registry files retained their before/after hashes. Evidence: ../validation-20261025-taskforge-rename/cli-install/content-verification.json. No actual model session, hook firing, existing-user marketplace transition or production rollout was exercised.
- A read-only git show evidence probe reached its existing 30-second limit; a batched git archive read completed within the unchanged limit. This does not resolve the previously investigated intermittent Windows exit delay. Full Windows default/override and cross-Python/remote CI matrices were not rerun for this batch. No commit, push or publication was performed.

## 2026-10-25 authorized delivery preparation

- User authorized merge, commit and push of the accumulated reviewed changes. After fetching origin, local main and origin/main both point to faba43a316f9bc3b117faf820dfb0f9f3495b83b; there is no separate local branch to merge. Deliver as a normal commit on main, without force push or history rewriting.
- Pre-commit repository validation passed again: 90-file payload synchronized, routes 10, inline Kernel, structural budget and 31 Golden Test metadata checks; no model execution. Reuse the unchanged-tree 120-case related regression and isolated CLI fresh-install evidence recorded above. Preserve the naming/icon advisories and operational/Windows limitations.
- Publication is authorized; the exact delivery commit and its remote Actions runs are the authoritative completion evidence. This preparation record does not claim a tag, GitHub Release, production cutover or actual model acceptance.

## 2026-10-27 delivery closeout

- Delivery commit: 1a27ae063abf3f2aa36d9a862d140981ccc1dcf4 (feat!: migrate TaskForge native plugin identity), published on main. No separate branch merge, force push, tag or GitHub Release was needed.
- Rechecked the exact delivery commit's remote Actions results: [Harness](https://github.com/yjj3019/claude/actions/runs/40191025954) and [Delegation](https://github.com/yjj3019/claude/actions/runs/40191025995) both completed successfully. Each workflow passed all five jobs. These results supplement the related local regressions and isolated CLI installation recorded above; they do not establish production or actual-model acceptance.
- The worktree was clean before this documentation-only closeout. Upstream reference HEADs remain Ponytail 09c434ab73ca43761c5d8b0c5d341926c2fba710 and Karpathy-inspired skills 2c606141936f1eeef17fa3043a72095b4765b9c2; reuse the recorded reviews. No product or generated payload changes are required for this record.
- Remaining limits: real-user plugin/marketplace migration and actual model/hook execution were not performed. CLI naming and missing-icon advisories remain. Third-party redistribution rights remain unresolved, with the existing deployment exclusions and blocks retained. Earlier intermittent Windows Git/exit delays are not established as resolved by passing CI.
- This entry records the delivered product commit. The documentation-only follow-up commit and its CI results are reported through Git/Actions and the completion message to avoid a self-referential chain of closeout commits.

## 2026-10-28 document guidance and verification

- Added bounded preview routes for research PDF translation, Korean proofreading and HWPX editing, preserving existing matched routes and high-risk unmapped behavior. New task_type values can affect consumers that previously received unknown. Updated related guidance and generated the 90-file native plugin payload; candidate plugin version 3.1.0, existing skill IDs and versions unchanged.
- Independent reviews found and verified fixes for source-code misrouting, missing file policy, empty code-path patterns and Korean table/standard ambiguity. Windows full regression: 229 tests, 227 passed, 2 skipped, exit 0, 1800.061 seconds. Both skips require Windows symbolic-link creation privilege (WinError 1314); an elevated user run was requested but its result was not supplied. Repository and payload checks passed.
- Isolated Claude Code 2.1.310 / claude-sonnet-5-5 session: SessionStart kernel delivery, explicitly invoked coding skill body, and Read of Writing policy observed; exit 0. This does not prove automatic selection of the new document routes or general model quality.
- Kordoc 4.24.13 installed with scripts disabled in a separate folder. Its MCP read and separate HWPX patch were checked with synthetic input; re-read, retained table text, unchanged source hash and KORDOC_ROOT rejection passed. A hidden .codex ancestor blocked output, so a fresh OS temporary directory was used. KORDOC_OFFLINE was set but not independently network-audited; rendering, visual preservation and production integration remain unverified. No Kordoc runtime or third-party asset was added to the repository.
- Existing unresolved third-party redistribution restrictions, Windows Git/process exit delays, native plugin naming/icon advisories and production deployment limits remain. No release or production activation is implied.

## 2026-10-28 document policy delivery and rendering follow-up

- With user approval, added a native UserPromptSubmit hook for exactly the three existing unambiguous low-risk document routes. It injects the fixed allowlisted guidance without storing the prompt; previously matched routes, ambiguous asks and high-risk unknown asks receive no added context. Missing or unsafe guidance produces a warning without partial delivery. Version 3.2.0 is a local candidate; matching follow-up prompts repeat context and may add latency.
- A clean generated-plugin copy was used with Claude Code 2.1.310 and claude-sonnet-5-5. Official debug logs recorded successful UserPromptSubmit additionalContext for Korean proofreading (Writing and FileHandling), PDF paper translation (Research, Evidence and FileHandling), and HWPX table editing (FileHandling). A different HWPX prompt containing a generic file cue was captured by the pre-existing coding fallback and did not receive document context; this existing precedence is unchanged. These are isolated synthetic prompts, not general efficacy or all-host proof.
- Local Windows related regression: 82 tests, 81 passed, one symlink privilege skip, exit 0. WSL document hook regressions: seven passed with actual symlink escape case. Both previously skipped installer symlink cases also passed in WSL. Administrator Windows rerun was approved but result collection failed on the first attempt and the second waited for approval until canceled; Windows actual-link coverage remains unverified.
- Kordoc 4.24.13 generated a synthetic HWPX with one rendered table; after MCP text patch the original hash remained unchanged and title, edited text and table were visually checked in rendered output. A separate incomplete synthetic HWPX lacking header.xml showed zero rendered tables before and after editing; its cause was not established. This does not establish visual preservation for arbitrary documents or production.
- No production deployment, commit or push was performed.

- Follow-up generated-payload hook regression: source and generated hook entry points were invoked from an unrelated directory. Windows: seven tests, six passed and one symlink-privilege skip, exit 0; WSL: seven passed, including real symlink escape rejection, exit 0. An additional elevated Windows runner produced no evidence before its waiting launcher was interrupted; no Windows actual-link pass is claimed.

- Final Windows full regression after document-hook changes: 236 tests, 233 passed, three skipped, no failures, exit 0, 1933.029 seconds. All three skips were actual symbolic-link creation privilege limits: two installer cases and the document hook escape case; their corresponding WSL tests passed with real symlinks. The verification wrapper reported identical pre/post snapshot hashes. This history-only entry was added after the run; no product files changed afterward. Administrator Windows actual-link results remain unverified.
