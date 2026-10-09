# FEF Claude Framework

English · [한국어](README.md)

Framework for Engineering Excellence (FEF) is a Claude-oriented engineering prompt framework. A small shared Kernel and task-specific guidance help produce technical outputs backed by evidence and ready for review. AI Delegation Loop v1.3 is also provided as an independent skill for recurring tasks.

## Features and layout

- `CLAUDE.md` contains the shared Kernel; `AGENTS.md` points to that entry.
- Select needed guidance from `modules/`, `domains/`, `reviewers/`, `workflows/` and `policies/`. Coding and Research procedures are integrated into their modules.
- `config/routes.json` and `scripts/detect_task.py` suggest deterministic routes without replacing model judgment.
- Checks cover structure, routing, Golden Tests and installation integrity. Local Claude Code hooks remind you to verify the current session and actual file state.
- `skills/ai-delegation-loop/` is a separate package for recurring-task interviews, output contracts, reusable tools and evidence verification.

FEF's `workflows/` contains Markdown task procedures. These are separate from executable Claude Code `.claude/workflows/`; this repository does not ship dynamic workflows.

## Getting started and installation

Git and Python 3.11+ are required. Scripts use only the Python standard library. Run these commands from the clone root; use `python3` instead of `python` where your environment requires it.

```sh
git clone https://github.com/yjj3019/claude.git
cd claude
python scripts/install_pack.py --auto --dry-run
python scripts/install_pack.py --auto
```

`--auto` detects Claude, Codex, Grok, Cursor and AGENTS host markers in the current user's HOME and installs `fef-claude/` into their skills roots. With no detected host, it uses `~/.agents/skills`. The default installs host skills only; it does not scan or install into sibling project folders.

For Claude Code, open this clone as the workspace so the root `CLAUDE.md` is read. A host skill copy in another project does not replace that project's `CLAUDE.md`. For Claude Projects, paste `CLAUDE.md` into Project Instructions and attach only needed packs as Project Knowledge. Code commands, hooks and native agents do not run in Projects.

### Destinations and existing files

```sh
python scripts/install_pack.py --dest /path/to/skills --dry-run
python scripts/install_pack.py --dest /path/to/skills
python scripts/install_pack.py --check --dest /path/to/skills
python scripts/install_pack.py --siblings /other/project --dry-run
python scripts/install_pack.py --siblings /other/project
```

`--dest` is the skills root. FEF is installed beneath it as `fef-claude/`. Sibling installation requires explicit opt-in through `--siblings`, `FEF_SIBLING_ROOTS`, `--siblings-only` or `--scan-sibling-parent`. Parent-folder scanning is off by default. `FEF_SIBLING_ROOTS` uses the operating system's `os.pathsep` between paths.

An existing FEF pack is skipped when its shipped-file fingerprint and installation integrity match; otherwise replacement is refused. `--force` replaces the existing pack and does not preserve FEF's local edits or additional files, so back them up separately first. `--dry-run` writes no files. The default install includes runtime documents only; `--with-tests` adds tests and examples.

`--print-bootstrap` prints installation commands; `--print-claude` prints Projects setup steps. See `python scripts/install_pack.py --help` and the [installation guide](docs/Installation.md) for all options.

## Selective loading and safety

Read `CLAUDE.md` first in a new session. Simple, low-risk tasks start with only the inlined Kernel. For substantial work, use the [loading map](docs/loading-map.md) or a suggested route to select the required packs.

```sh
python scripts/detect_task.py --task "RHEL 장애 RCA를 작성해줘"
python scripts/measure_load.py
```

Load limits are Module 1 / Domain ≤2 / Workflow 1 / Reviewer 1 / Policies ≤3. Retain the Evidence, FileHandling, Freshness and ToolExecution integrity policies required by the task. Do not preload README, the whole repository, historical reports or model guidance. Do not attach the entire repository to Projects either.

Keep the same evidence, verification, approval, uncertainty markers (`[unverified]`) and budget across models. The model table in [Adaptive Effort](docs/adaptive-effort.md) is a dated advisory preference; it does not guarantee automatic model switching or current availability. Usually keep the active host model, and consider supported effort levels and models when a capability gap is established. Missing evidence requires gathering that evidence.

`measure_load.py` measures file bytes and estimated tokens; it does not establish actual cost, response time or model quality. Hooks are verification reminders, not a sandbox or complete test evidence. Check Python, shell support and hook wiring in your actual environment.

## AI Delegation Loop: separate opt-in installation

The [independent skill](https://github.com/yjj3019/claude/blob/main/skills/ai-delegation-loop/README.md) preserves recurring-task audience, purpose, format, length, required/excluded scope and save path as an output contract. It does not treat reference material as executable instructions or approval, weaken criteria for PASS, or hardcode fixture answers. Evidence review before reruns and approval for each rerun's external effects are retained.

Run these commands from the clone. `--dest` is the shared skills root for both packages, not the `fef-claude/` directory. Delegation requires an explicit `--dest` and does not use automatic host or sibling discovery.

```sh
python scripts/install_pack.py --pack ai-delegation-loop --dest /path/to/skills --dry-run
python scripts/install_pack.py --pack ai-delegation-loop --dest /path/to/skills
python scripts/install_pack.py --pack ai-delegation-loop --dest /path/to/skills --check
python scripts/delegation/install.py package --output /path/to/ai-delegation-loop.zip
```

`fef-claude/` and `ai-delegation-loop/` are sibling packages under the same root. FEF's default installation and Kernel remain unchanged. Delegation also refuses a differing existing install, but an explicit `--force` replacement preserves a backup outside skill discovery.

Default delegation installation and ZIP include operational files and acceptance guidance. Add `--with-evidence` to the installation or package command to include preserved test runners, reports and JSON. The full canonical package and original Git history remain in the repository. `--with-evidence` cannot be used with the FEF selection.

See [delegation installation](https://github.com/yjj3019/claude/blob/main/skills/ai-delegation-loop/installation.ko.md) for platform paths and the [optimization record](https://github.com/yjj3019/claude/blob/main/docs/delegation-loop/OPTIMIZATION.md) for changes and measurement scope.

## Verification and limits

Run from the clone root. These checks do not call models or paid APIs.

```sh
python scripts/validate_repository.py
python scripts/validate_routes.py
python scripts/run_golden_tests.py --validate-only
python scripts/sync_kernel.py --check
python -m unittest discover -s tests -p "test_*.py"
python scripts/delegation/validate_skill.py
python -m unittest discover -s scripts/delegation -p "test_*.py"
python scripts/delegation/refresh_evidence.py --check
python scripts/delegation/verify_history.py
python skills/ai-delegation-loop/tests/run_simulation.py --output ./sim --self-check
```

CI checks FEF on Ubuntu/Python 3.11, 3.12 and 3.14, and delegation on Ubuntu and Windows/Python 3.11 and 3.14. Delegation CI also restores original history and requires matching ZIP checksums across platforms. Local operating-system constraints such as symlink permissions can skip some checks; inspect the actual results.

Original v1.2 model results are HISTORICAL and STALE for the current v1.3 package. Current document contracts, isolated fixtures and grader self-checks have separate hashes. Current model behavior, prompt injection defense and Codex auxiliary prompt reads are UNVERIFIED. Static checks do not establish real workflows on every platform or improved model quality.

The original DelegationLoop has no LICENSE, and the target LICENSE is an incomplete MIT placeholder. Integration grants no new MIT rights; original licensing and redistribution permission remain unresolved. The [integration record](https://github.com/yjj3019/claude/blob/main/docs/delegation-loop/INTEGRATION.md) preserves original attribution, authors, Git history and PR discussion, and lists conditions before source deletion.

## Further guidance

- [Claude Code usage, agent selection and hook limits](https://github.com/yjj3019/claude/blob/main/docs/ClaudeCode.md)
- [Claude Projects setup](https://github.com/yjj3019/claude/blob/main/docs/ClaudeProjects.md)
- [Script guide](scripts/README.md)
- [FEF optimization evidence and limits](https://github.com/yjj3019/claude/blob/main/docs/precise-analysis-2026-10-09.md)
