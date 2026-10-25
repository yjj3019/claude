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

## Language conventions

Use English for shared instructions, operational documentation and code explanations. Keep the primary README in natural Korean and maintain README.en.md as its English overview. Preserve commands, configuration keys and Korean test inputs verbatim, apart from explicitly approved interface migrations. Keep historical evidence and third-party originals in their original form.
