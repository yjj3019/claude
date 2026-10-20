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
- **Repository cleanup (2026-10-15)**: Historical simulation, review, ablation, and source-history files moved to `docs/archive/`. Stub docs removed. Full prior progress log preserved in `docs/archive/PROGRESS-full.md`.

## Current Status

The latest observed full regression passed. The earlier intermittent submodule failure remains unexplained; a passing rerun is not a root-cause fix. Prefer native Skills for ordinary coding/RCA tasks. Use `scripts/detect_task.py` or loading map for complex multi-pack routes. Verification hooks and golden tests remain active.

Open items from earlier rounds (S4-08 hook payload verification, valid pack-ablation re-run outside this repo) are recorded in the archived progress log.

Full historical entries (August–September 2026 rounds, ablation experiments, Fable deletion, routing priority changes, etc.) are in `docs/archive/PROGRESS-full.md`.

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
