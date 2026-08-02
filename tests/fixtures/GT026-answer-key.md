# GT026 Answer Key

Use this key to score `tests/fixtures/GT026-code/` runs.

## Seeded Bug

| ID | Type | Location | Expected Finding | Severity |
|---|---|---|---|---|
| C1 | Root cause | `tagging.add_tag` | `add_tag` uses a mutable default argument (`tags=[]`), so one list object is shared across every call. | Critical |
| C2 | Sibling caller risk | `reports.py` | `reports.tag_records` relies on each call starting fresh; passing `[]` at the call site hides the defect for other callers. | Major |

## Expected Patch Shape

A strong patch should be close to:

```python
def add_tag(tag, tags=None):
    if tags is None:
        tags = []
    tags.append(tag)
    return tags
```

Equivalent minimal implementations are acceptable if they:

- each bare call returns a fresh single-tag list
- an explicitly passed list is still appended in place
- `reports.py` keeps calling `add_tag`
- no dependencies are added

The executable reference patch is `tests/fixtures/GT026-code/answers/tagging.py`.

## Objective Checks

- `python -m unittest -v` passes after the patch.
- The change touches `tagging.py`, not only `reports.py`.
- Tests are not modified and no dependency is added.
