# TaskForge for Claude

English · [한국어](README.md)

A framework that connects coding and root-cause analysis in Claude Code with task guidance, review and verification. Load only the guidance a task needs and record evidence, actual checks and remaining limits.

By yjj3019 · Formerly FEF (Framework for Engineering Excellence).

An independent project, not created, sponsored or endorsed by Anthropic.

<a id="getting-started-and-installation"></a>
## Quick start

Requires Claude Code, Python 3.11+ and Git. In Claude Code, run:

```text
/plugin marketplace add yjj3019/claude
/plugin install taskforge-for-claude@taskforge-marketplace
```

Restart the session to use the shared Kernel, skills, reviewer agents and verification reminder hooks. Hooks run with your user permissions; inspect [their configuration](https://github.com/yjj3019/claude/blob/main/hooks/hooks.json) before installation.

<a id="features-and-layout"></a>
<a id="selective-loading-and-safety"></a>
## Usage

| Task | Skill call |
|---|---|
| Implement or modify code | `/taskforge-for-claude:coding` |
| Investigate failures | `/taskforge-for-claude:rca` |

Select guidance and reviewers for the task, then inspect actual verification and remaining limits. See the [Claude Code guide](docs/ClaudeCode.md) and [loading contract (English)](docs/loading-map.md).

<a id="destinations-and-existing-files"></a>
### Updates and existing installations

```text
/plugin update taskforge-for-claude@taskforge-marketplace
```

Plugin 3.0.0 changes the native installation identity and skill names. Old
`fef-engineering` and native `fef-claude` calls must be updated. Preserve existing
settings/caches and follow the [migration guide](docs/ClaudeCode.md#plugin-validation-and-compatibility)
before cutover. Verification state, environment keys and the separate standalone
`fef-claude/` pack remain unchanged.

<a id="further-guidance"></a>
## Documentation

Shared instructions, operational guides and code explanations are maintained in English. The primary README uses natural Korean; this file is its English overview. Commands, configuration keys and Korean test inputs retain their original spelling. The approved native identity changes are documented separately. Historical evidence and third-party originals are preserved.

| Purpose | Guide |
|---|---|
| Installation options and standalone packs | [Installation](docs/Installation.md) |
| Skills, hooks, reviewers and compatibility | [Claude Code](docs/ClaudeCode.md) |
| Task selection and routing | [Loading contract (English)](docs/loading-map.md) |
| Skill versions and change history | [Versions](docs/skill-versions.md) |
| Official capabilities and custom delegation | [Mods and three-tier agents](docs/mods-and-tiered-agents.md) |
| Scripts and generated distributions | [Script guide](scripts/README.md) |

<a id="verification-and-limits"></a>
### Repository checks

Run from the clone root after source changes. These checks do not call model APIs.

```sh
python scripts/validate_repository.py
python -m unittest discover -s tests -p "test_*.py"
```

<a id="distribution-clearance-and-skill-versions"></a>
## License and distribution scope

Original FEF contributions are covered by the scoped [MIT license](LICENSE). DelegationLoop materials, external guides, quotations, archived records and their generated copies are excluded; the repository as a whole is not MIT-licensed.

The delegation skill with unresolved redistribution rights is excluded from the plugin; new installation and ZIP generation are blocked. Source and existing installed data are preserved, along with coding/RCA calls. See the [third-party notices](https://github.com/yjj3019/claude/blob/main/skills/ai-delegation-loop/THIRD_PARTY_NOTICES.md) and [clearance procedure](docs/third-party-clearance.md).
