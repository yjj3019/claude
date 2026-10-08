# Context and harness optimization decisions

2026-10-09. Baseline: `fc461fb90cde529421e49fba7ed0c88b4b309a59`.
This document records implementation and evidence limits, not a model-performance benchmark.

## Implemented

- Compact the generated core to 69 CLAUDE.md lines and keep AGENTS as a pointer. Preserve evidence, minimal changes, authorization, secret protection and truthful completion.
- Integrate Coding and Research workflows into their modules. Keep CodingWorkflow as a compatibility pointer and ResearchWorkflow as a standalone procedure for blog/deck tasks; neither duplicates the default Coding/Research route. Coding's reviewer is conditional on consequential risk or an explicit request.
- Use the existing route preview rather than also reading the full loading map for every mapped task. Manual/domain-specific selection retains the map and load limits.
- Retain the dated, user-defined model roster for compatibility; treat it as an advisory preference, verify host capabilities and compare supported effort before adding another model or Advisor.
- Replace the shared test marker with session baselines and content hashes. Include untracked nested files, deletions and all Git-visible languages; preserve state on resume/compact.
- Add a verification argv wrapper for native Bash payloads without exit metadata. Preserve raw child stdout/stderr and exit status; only credit a matching command and unchanged snapshot. Reject aggregate shell/pipeline exits.
- Installation fingerprints include all shipped files and an installed integrity manifest. Changes to policies, hooks or routes and local drift cannot be mistaken for an identical installation. Preserve explicit overwrite protection.
- Update Code/Projects guidance for cache versus occupancy, scoped references, selective skills, native session tools and workload-specific evaluation.

## Structural measurements

UTF-8 bytes, no BOM, logical LF. Domain files, system prompts, native skill descriptions and tool schemas are excluded. These are file-size models, not tokenizer counts, latency, dollar cost or quality measurements.

| Scenario | Baseline bytes | Optimized bytes |
|---|---:|---:|
| CLAUDE.md alone | 6,980 | 3,913 |
| Explicit CLAUDE.md + AGENTS.md scenario | 8,283 | 4,558 |
| Coding via route preview, both entries assumed | 15,173 | 9,265 |
| Coding with full manual loading map, both entries assumed | 24,217 | 15,696 |

Native Code does not necessarily load both entry files: do not describe the combined scenario as its measured default startup. Manual-map numbers include the map omitted by the old route estimate. A conditional reviewer or required domain increases actual load. Use `python scripts/measure_load.py` for the current structural accounting; bytes/4 is uncalibrated.

## Kept and excluded

Keep project-specific domains, Integrity Policies, useful examples, focused reviewers and regression fixtures. Their file count is not evidence of overhead when they are not read. Historical reports/tests are already excluded from the default install; deleting them would not demonstrate runtime savings.

Do not add deprecated advisor-opus, a whole harness framework, automatic team creation, repeated critic/voting, always-on LLM hooks or third-party output compressors as default dependencies. No universal compact percentage, 2KB skill threshold, 5x model-price ratio or token-savings target is enforced.

The native Advisor and API Advisor have different controls; compare single-model effort and accepted-task cost before adopting either. Code slash commands, local memory, hooks and native agents do not execute in Projects. Projects receives the compact instructions and selected Knowledge, with explicit retrieval/quality limits.

## Evidence and limitations

- [New context engineering rules](https://claude.dev/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models/): official claude.com redirect confirmed. The internal 80% system-prompt removal observation lacks public task/model/raw results; it does not justify 80% deletion or a user cost claim. Keep interfaces, needed references and progressive disclosure; remove repeated procedures.
- [Harnessing Claude's intelligence](https://claude.com/resources/articles/harnessing-claudes-intelligence) and [how Code works](https://code.claude.com/docs/ko/how-claude-code-works): model reasoning and harness execution/context/permissions are complementary. Avoid duplicating native mechanisms. The Korean article URL was unavailable; its English original was read.
- [PyTorch harness introduction](https://discuss.pytorch.kr/t/claude-code-harness-claude-code/10648) introduces [Chachamaru127/claude-code-harness](https://github.com/Chachamaru127/claude-code-harness), not [revfactory/harness](https://github.com/revfactory/harness/blob/main/README_KO.md). The Go plugin's hook count is static and its missing-binary path skips enforcement. Revfactory v2 is a prompt factory; v1 self-reported A/B scores are not v2 or FEF proof. No whole-framework installation is adopted.
- [Native Advisor](https://code.claude.com/docs/en/advisor), [API Advisor](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool), [deprecated advisor-opus](https://github.com/shalomeir/advisor-opus), [PyTorch advisor discussion](https://discuss.pytorch.kr/t/anthropic-claude-api-opus-sonnet-haiku-advisor/9684), [Hada summary](https://news.hada.io/topic?id=28370) and [AI Sparkup summary](https://aisparkup.com/posts/16375): distinguish official contracts from summaries; additional models are optional and add transcript/aggregation cost.
- [Native teams](https://code.claude.com/docs/en/agent-teams) and [subagents](https://code.claude.com/docs/en/sub-agents): independent context can reduce main-session noise but does not guarantee lower total usage. Native experimental-team settings and ordinary delegation are different.
- [Hancom context optimization](https://tech.hancom.com/claude-md-context-optimization/), [official cost/intelligence guidance](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence), [code performance](https://claude.com/ko/resources/articles/optimize-code-performance-quickly) and [session value](https://claude.com/ko/resources/articles/maximizing-the-value-of-your-claude-code-sessions): retain bounded investigation and observable acceptance criteria, not broad performance promises.
- [Caching](https://code.claude.com/docs/en/prompt-caching), [costs](https://code.claude.com/docs/en/costs), [memory](https://code.claude.com/docs/en/memory), [hooks](https://code.claude.com/docs/en/hooks) and [checkpointing](https://code.claude.com/docs/en/checkpointing): imported instructions still consume context; cache does not remove occupancy; usage estimates are not invoices; checkpoints do not undo all external actions.
- [Third-party tool comparison](https://computingforgeeks.com/reduce-claude-code-token-usage-tools/): a single read-only task's 43.5% raw-token decrease corresponded to 13.5% cost decrease. [The tool author's corrections](https://github.com/Mibayy/token-savior) prevent treating this as independently reproduced universal savings. UX Planet's submitted article was accessible only in its introduction; no full-content conclusion is claimed.

## Verification boundary

Unit/integration tests and repository validators establish implementation behavior, not better Claude answers. Native hooks still need the actual installation's interpreter/shell/capabilities. The reminder fails open visibly on unavailable state/Git, does not prove coverage, cannot attribute concurrent edits, and excludes ignored files. Direct explicit-exit metadata records post-run state; the wrapper additionally checks that state did not change during the run. No permission bypass, hook output replacement, deployment or credential changes are added.

Actual Code/Projects quality, retries, cache-aware total cost and latency require separate controlled model runs. No paid model evaluation is claimed. Preserve baseline/prompt/model/tool/cache evidence and measure accepted-task cost before promoting conditional mechanisms.

## Additional reading reviewed

[CLAUDE.md guidance](https://claude.com/blog/using-claude-md-files), [dsebastien](https://www.dsebastien.net/claude-code-tips-and-best-practices/), [Fast.io](https://fast.io/resources/claude-best-practices-guide/), [UX Planet (introduction only)](https://uxplanet.org/claude-code-context-window-optimization-best-practices-6f5f2e3d5931), [KDnuggets](https://www.kdnuggets.com/7-practical-ways-to-reduce-claude-code-token-usage), [Composio](https://composio.dev/content/ways-to-cut-token-consumption-in-claude-code) and [ClaudeCodeLab](https://claudecode-lab.com/en/blog/claude-code-token-optimization/). These contributed bounded-search/handoff ideas; current official contracts take precedence over their historical defaults or self-reported savings.
