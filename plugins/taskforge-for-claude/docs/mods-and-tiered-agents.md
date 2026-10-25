<a id="claude-code-mods와-3계층-에이전트"></a>
# Claude Code Mods and Three-Tier Agents

Official documentation checked as of: 2026-10-18. Recheck support against the actual Claude Code version and execution environment. This document explains features and designs; it does not install Mods, change models, or enable automatic routing.

<a id="공식-기능-mods"></a>
## Official Feature: Mods

Mods are plugins containing JavaScript or TypeScript event handlers that run inside Claude Code. They can observe, modify, or handle events such as prompt submission, tool calls, and UI rendering. On supported interfaces, they can add panels, areas above the input box, and buttons. The terminal requires v2.1.287 or later; UI support varies by environment. Settings hooks use commands, HTTP requests, or prompts in configuration files; Skills provide instructions, and MCP connects tools. [Official overview](https://code.claude.com/docs/en/plugins/mods/overview)

<a id="최소-구성과-이벤트-처리"></a>
### Minimal Structure and Event Handling

The official introductory example uses the following structure. This is not a specification with a fixed number of files.

```text
my-mod/
├── .claude-plugin/plugin.json
└── hooks/
    ├── hooks.json
    └── register.js
```

`plugin.json` is the manifest, and `modules` in `hooks.json` specifies code module paths. Events are registered in the module's exported `register(on)` function. [Authoring guide](https://code.claude.com/docs/en/plugins/mods/create)

Handlers receive an API object `$`, an event `e`, and a continuation function `next`.

| Pattern | Behavior |
|---|---|
| Observe | Continue existing processing with `next(e)` while recording information |
| Modify | Pass a modified copy, such as `next({ ...e, text: newValue })` |
| Handle directly | Return an event-specific result without `next` to stop subsequent processing |

`e` is deeply frozen; modifying it directly causes an error. Stopping subsequent processing does not mean that all model calls are skipped. A reason for denying tool execution may also be returned to the model as a tool result. [Event handling](https://code.claude.com/docs/en/plugins/mods/events)

<a id="작성-재로딩-권한"></a>
### Authoring, Reloading, and Permissions

You can describe the required behavior in natural language and ask the built-in `plugin-authoring` skill to create it. Development directories specified with `--plugin-dir` reload when changed; changes Claude saves during its own turn take effect at the end of that turn. `claude plugin validate` reports static analysis results for the manifest and modules. Passing validation is not a security certification. [Authoring and validation guide](https://code.claude.com/docs/en/plugins/mods/create)

Mods run with the user's permissions and are not isolated in a separate sandbox. Review file, process, and network access. `--safe-mode` disables other user customizations as well as installed Mods, but does not stop all built-in Mods. [Permissions and scope of disabling](https://code.claude.com/docs/en/plugins/mods/overview)

<a id="사용자-정의-설계-mods-활용"></a>
## Custom Design: Using Mods

| Example design | What to implement and verify |
|---|---|
| Git and context status display | Information collected and update timing |
| Tool execution timeline and agent monitoring | Capture failures, cancellations, and missing states |
| Screen masking | What is displayed and how original content is handled; distinguish this from protecting logs, files, and network traffic |
| Risky command confirmation and file conflict warnings | Detection coverage, bypasses, omissions, and state sharing between sessions |
| Diagram and issue tracker integration | Rendering implementation, authentication, and approval for external writes |

This table is not a list of features installed in TaskForge for Claude. Distinguish the extension mechanisms provided by the API from individual implementations. The official `token-weather` and `blast-radius` samples are not enabled by default either; they are examples provided without a support guarantee. [Official sample guide](https://code.claude.com/docs/en/plugins/mods/overview)

<a id="공식-기능-서브에이전트와-캐싱"></a>
## Official Features: Subagents and Caching

Claude Code subagents work in independent contexts and can have role-specific instructions, tools, and models. An independent context does not imply filesystem isolation, and tool output does not automatically pass through Haiku. [Subagents](https://code.claude.com/docs/en/sub-agents)

Prompt caching is a separate feature that reuses repeated prefixes. Consider cache hit conditions, minimum length, lifetime, and write/read pricing. Placing fixed instructions does not by itself guarantee a cache hit, and caching does not remove context usage. [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

<a id="사용자-정의-설계-3계층-위임"></a>
## Custom Design: Three-Tier Delegation

The following is an example of role allocation, not Claude Code's default routing specification.

| Tier | Example tasks | Evidence to return |
|---|---|---|
| Explore and summarize | Investigate files and usages; analyze specified logs | Conclusions, files and lines, errors, and unverified items |
| Implement and execute | Modify code, run tests, and analyze failures | Changes, commands run, working directory, and exit status |
| Decide and review | Make design decisions, analyze complex failures, and conduct independent reviews | Reasoning, remaining risks, and recommended changes |

Choose models according to task difficulty, tool use capabilities, cost, verification results, and host support. There is no need to always start with the cheapest model or send every task through all three tiers. This example does not replace the dated L0–L3 preferences in [Adaptive Effort](adaptive-effort.md) or the reviewer definitions.

Summary length and escalation criteria are also custom choices. Fixed summary lengths, self-assessed confidence thresholds, and specified failure counts are not official automatic escalation rules. Preserve failure evidence and unverified items in summaries, and retain access to the originals. When tests fail, first distinguish environment, permission, and requirement issues. Actual model changes depend on host capabilities and user authorization.

<a id="효과-평가"></a>
### Evaluating Effectiveness

Delegation can reduce the amount of information in the main context, but adds costs for instructions, summaries, reviews, and retries. Measure success rate, regression results, total call cost, cache usage, retries, and completion time for the same tasks. Separate the effects of model changes from caching, and include execution environment costs when making claims about total computing costs. Specific savings or maintained quality cannot be guaranteed without measurements. [Official cost and performance optimization guide](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence)

TaskForge for Claude does not provide the three-tier automatic router or tool output compressor described in this document. For adoption evaluation, see the [measurement protocol](mod-evaluation-metrics.md) and [repository scorecard](mod-evaluation-scorecard.md). These scoring criteria are not an official benchmark.
