# Delegation Loop integration

The independent canonical package is `skills/ai-delegation-loop/`. It was imported from v1.2 optimized commit `01351414e10df3c177939e4fef8393609ece6c55`, one commit beyond main `1e35bf0a6d16bac0c6e1dccda1014a1e78b7bb96`, and is now v1.3 with semantic prompt fixes. The feature branch has the same tree as main but a different commit. FEF root AGENTS/CLAUDE, Kernel and selective loading rules remain intact. Default FEF installation is unchanged; delegation is explicitly installed beside it.

Tooling lives in `scripts/delegation/`. Validation scans that tooling, the full canonical package, this documentation and the delegation workflow, rather than imposing source-wide rules on FEF. It preserves root FEF entry points and already uses minimal fixtures. Default installation and ZIP project operational files plus acceptance guidance; optional `--with-evidence` includes test runners and historical artifacts. Canonical files/history remain intact. Runtime links are validated without the experimental files. Operational clone URLs use claude; archived source URLs are historical provenance.

## History and discussion recovery

`source-history/DelegationLoop.bundle` preserves complete reachable Git objects, parents, trees, file bytes, authors and original commit messages for all advertised source branch heads, including main and optimize/three-platforms. The PR #1 head object is also retained; `manifest.json` maps the original advertised branch/PR/HEAD names to their commit IDs and separately records the bundled local refs. No source remote settings are changed. The manifest records SHA-256, file identities, object counts, scan results and restoration verification. A blob manifest alone is not Git history preservation.

Restore without the original repository:

```sh
git clone --mirror docs/delegation-loop/source-history/DelegationLoop.bundle restored-source.git
git -C restored-source.git fsck --full
git clone restored-source.git restored-work
git -C restored-work checkout 01351414e10df3c177939e4fef8393609ece6c55
```

`pr-1.json`, `pr-1-conversation.json`, `pr-1-review-comments.json` and `pr-1-reviews.json` preserve the PR body and all retrieved discussion, including frontmatter, rerun approval, proof order and completion-evidence review concerns. Their URLs are historical and may stop resolving after deletion. GitHub API reports Wiki enabled, but a Wiki Git endpoint check returned Repository not found: no Wiki content was retrievable; enabled setting alone does not establish an actual Wiki. Recheck before deletion if Wiki content is subsequently created.

## Attribution and license

Original procedure: [AI 위임 루프: 에이전트 대신 매뉴얼으로 일 넘기기](https://sdk-kim-builds.com/guides/ai-delegation-loop-playbook/), 낭만빌더 김스듴, 2026-09-18. Source commit attribution is retained in the bundle. The source has no LICENSE. Target LICENSE contains an incomplete MIT placeholder. This integration does not grant MIT rights or invent an owner; licensing/redistribution permission remains unresolved.

## Evidence limits and deletion conditions

Original `simulation-results.json`, native probe results and `simulation-report.v1.2.ko.md` retain the original source bytes. The current report explicitly labels these v1.2 model artifacts HISTORICAL/STALE_FOR_CURRENT_PACKAGE. v1.3 changes SKILL, manual, standalone prompts, template and acceptance specification. It does not reuse original model responses as validation of those changes.

`integration-manifest.json` classifies original files as unchanged/modified and records both source and current hashes. Package `tests/evidence-status.json` anchors historical artifact hashes to the unchanged source archive manifest and points to separate current `acceptance-results.json`. Current evidence records normalized reference/input/runner hashes for static document contracts, isolated playbook format fixtures and the oracle grader self-check. `refresh_evidence.py --check` executes those tests without writing or invoking models. Unexpected current hash drift or tampered historical bytes fails validation; `--allow-stale-evidence` cannot bypass these guards.

The v1.3 fixes preserve output contracts, add standalone untrusted-data boundaries, prohibit weakening checks for PASS, allow evidenced human-confirmed criterion corrections, and require general rules plus original/other-input regression checks. Earlier frontmatter/proof-order/rerun-approval/durable-protocol/multiple-cause fixes remain. Deterministic checks are at most L3 and do not establish model adherence or prompt injection defense. Model behavior and Codex auxiliary reads remain UNVERIFIED; web uploads, automatic invocation and real workflows are not newly validated. [Optimization measurements](OPTIMIZATION.md) distinguish payload/inventory reductions from unmeasured model quality and latency.

Before deleting the source: keep an independent copy of the verified bundle and PR snapshots, recheck new refs/comments/Wiki, and resolve license permissions. Bundle excludes GitHub-only settings, Actions artifacts, issues beyond PR #1 and unreachable/deleted refs. Repository deletion and global installation remain outside this work. Merge requires explicit authorization and verified exact-head checks; any authorized merge outcome is recorded on the PR.
