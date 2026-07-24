# Project Progress

## Current Status

- Updated: 2026-07-24 KST
- Branch: `main`
- Remote state: pushed through `356aa14`; copy/paste diagnostic prompt export pending verification and push
- Fable benchmark: contract, Golden Tests, framework, and PILOT-A freshness valid; 98 unit tests pass
- Implemented: private holdout v1.1 intake, hash-bound provenance attestation with custodian/attestor role separation, routed plan compiler, shared response/blinding pipeline, lexical/semantic evidence validation, execution preflight, batch audit, declarative private scoring, five-axis evidence-conflict outcome rubric, scenario-level and provenance-stratified OOD statistics, numeric phrase normalization, hash-bound two-rater reliability, placebo analysis, and a final evidence gate that rejects mixed dataset/manifest/provenance evidence
- Diagnostic result: Opus 4.8 and Sonnet 5 were both evidence-faithful on five non-promotional cases; one label-only disagreement was observed
- Promotion status: not ready; offline semantic evidence, independently verified holdout provenance, and two scored batches remain
- Single-operator path: diagnostic comparison may complete without independent provenance; it cannot produce formal GO
- Local diagnostic plan: `DIAGNOSTIC-A` generated under `.local/fable/` with 20 non-promotional runs
- Local prompt handoff: 20 hash-verified copy/paste Markdown files generated; evaluator/canary leakage hits 0
- Constraint: API credentials, paid API use, and local LLM/Ollama are excluded; no semantic gate bypass is permitted
- Ignored user file: `scratch_notion_ai_simple.md` was not modified or committed

## Next Session

1. Replace or independently verify the current diagnostic holdout provenance.
2. Resolve the semantic-similarity requirement without violating the no-API/no-local-LLM constraint, or keep the benchmark diagnostic-only.
3. Only after private preflight PASS, execute and audit two independent batches, score blinded outputs, calculate reliability/statistics, and run the final evidence gate.

## Notion Log URL

https://app.notion.com/p/398b44a2dd2e81729cb9dab78c31a5e7
