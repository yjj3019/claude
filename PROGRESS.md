# Project Progress

## Current Status

- Session closed: 2026-07-21 20:55 KST
- Branch: `main`
- Remote state: pushed through `410bdaa`
- Fable benchmark: contract valid; 42 benchmark tests pass; PILOT-A stale check passes
- Promotion status: not ready; actual manual runs, private holdout data, semantic leakage evidence, and two independent scored batches remain
- Ignored user file: `scratch_notion_ai_simple.md` was not modified or committed

## Next Session

1. Place independently maintained private fixtures under `.local/fable/holdout/`.
2. Create a local manifest from `config/fable-holdout-manifest.example.json` and run `scripts/validate_fable_holdout.py`.
3. Run leakage checks with secret canaries and separately produced semantic-similarity evidence.
4. Execute the Claude app manual batches only after the holdout intake gate passes.

## Notion Log URL

https://app.notion.com/p/398b44a2dd2e81729cb9dab78c31a5e7
