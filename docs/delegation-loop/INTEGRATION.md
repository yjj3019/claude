# Delegation Loop integration

The independent canonical package is `skills/ai-delegation-loop/`, imported from optimized commit `01351414e10df3c177939e4fef8393609ece6c55`, one commit beyond main `1e35bf0a6d16bac0c6e1dccda1014a1e78b7bb96`. The feature branch has the same tree as main but a different commit. FEF root AGENTS/CLAUDE, Kernel and selective loading rules remain intact. Default FEF installation is unchanged; delegation is explicitly installed beside it.

Tooling lives in `scripts/delegation/`. Validation scans that tooling, the package, this documentation and the delegation workflow, rather than imposing source-wide rules on FEF. It checks the package README version, preserves root FEF entry points, and uses minimal fixtures. Operational clone URLs use claude; archived source URLs are historical provenance.

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

Existing `simulation-results.json`, native probe results and Korean report are retained byte-for-byte as historical evidence. Integration changes installation documentation only; hashed SKILL, manual, prompts and simulation cases are unchanged and their frozen hashes are revalidated. Grader self-check is L3 and does not rerun paid models. Codex auxiliary prompt reads remain UNVERIFIED; web uploads, automatic invocation and full real workflows are not newly validated.

Before deleting the source: review and merge this draft only with separate authorization, keep an independent copy of the verified bundle and PR snapshots, recheck for new source refs/comments/Wiki, and resolve license permissions. Bundle excludes GitHub-only settings, Actions artifacts, issues beyond PR #1 and unreachable/deleted refs. Repository deletion, merge and global installation are outside this work.
