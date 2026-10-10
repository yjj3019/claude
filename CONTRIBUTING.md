# Contributing

## Principles

- Do not expand the kernel unless necessary.
- Add task-specific content as modules.
- Add domain knowledge as domain packs.
- Validate changes with golden tests.
- Avoid vague persona rules.
- Prefer behavior-oriented instructions.

## Validation and Releases

- Run `python scripts/validate_repository.py`, `python scripts/validate_routes.py`, and `python scripts/run_golden_tests.py --validate-only` before submitting changes.
- Follow `docs/release-process.md` for Semantic Versioning and release preparation.

## Reviewer source and generated agents

Edit the applicable `reviewers/CodeChangeReviewer.md` (or another source in the reviewers directory) source, not `.claude/agents/*.md` alone.
From the clone root, regenerate and inspect the resulting diff:

```sh
python scripts/generate_agents.py
python scripts/validate_repository.py
python -m unittest discover -s tests -p "test_*.py"
git diff --check
```

The repository validator checks generated-agent equality. Preserve the read-only
one-pass contract (`Read, Grep, Glob`, Opus and maxTurns 15); source fixes do not
authorize tool/model/permission changes. The caller supplies scope and actual
verification evidence; after accepted fixes, the parent checks them without an
automatic second reviewer pass.

## Reproducible examples and evidence

Start with an input, selected packs, expected output and verification criteria,
as in [GT003/GT004 examples](docs/Examples.md). Use synthetic identifiers and
measurements, separate evaluator answer keys from model input, and mark unrun
manual comparisons NOT_RUN. Register all required fixtures/prompts in
`config/golden-tests.json`. Preserve historical raw files and INVALID labels;
use the [evidence index](docs/evidence-index.md) before citing outcomes. Publication
and licensing decisions require their own authority; do not infer rights from
this repository's placeholder LICENSE.
