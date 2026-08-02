# GT028 Answer Key

Use this key to score `tests/fixtures/GT028-code/` runs.

## Seeded Bug

| ID | Type | Location | Expected Finding | Severity |
|---|---|---|---|---|
| C1 | Root cause | `loader.parse_export` | The export begins with a UTF-8 BOM, so the first header parses as `"\ufeffname"` instead of `"name"`. | Critical |
| C2 | Sibling caller risk | `summary.py` | Renaming keys in `summary.py` is a caller-side workaround; the parser must strip the BOM for every consumer. | Major |

## Expected Patch Shape

A strong patch should be close to:

```python
lines = text.lstrip("\ufeff").strip().splitlines()
```

Equivalent minimal implementations are acceptable if they:

- the first header key is `name` with and without a BOM
- `summary.names` returns the file-order names
- `summary.py` keeps calling `parse_export`
- no dependencies are added

The executable reference patch is `tests/fixtures/GT028-code/answers/loader.py`.

## Objective Checks

- `python -m unittest -v` passes after the patch.
- The change touches `loader.py`, not only `summary.py`.
- Tests are not modified and no dependency is added.
