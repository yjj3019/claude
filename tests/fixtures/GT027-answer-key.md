# GT027 Answer Key

Use this key to score `tests/fixtures/GT027-code/` runs.

## Seeded Bug

| ID | Type | Location | Expected Finding | Severity |
|---|---|---|---|---|
| C1 | Root cause | `inventory.list_items` | `list_items` returns the module-internal list itself, so callers mutate shared state through the alias. | Critical |
| C2 | Sibling caller risk | `audit.py` | Copying inside `audit.py` protects one caller only; every other consumer of `list_items` stays exposed. | Major |

## Expected Patch Shape

A strong patch should be close to:

```python
def list_items():
    return list(_ITEMS)
```

Equivalent minimal implementations are acceptable if they:

- `audit_report` output is sorted and marked
- the live inventory is unchanged after an audit
- `audit.py` keeps calling `list_items`
- no dependencies are added

The executable reference patch is `tests/fixtures/GT027-code/answers/inventory.py`.

## Objective Checks

- `python -m unittest -v` passes after the patch.
- The change touches `inventory.py`, not only `audit.py`.
- Tests are not modified and no dependency is added.
