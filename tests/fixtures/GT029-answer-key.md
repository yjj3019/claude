# GT029 Answer Key

Use this key to score `tests/fixtures/GT029-code/` runs.

## Seeded Bug

| ID | Type | Location | Expected Finding | Severity |
|---|---|---|---|---|
| C1 | Root cause | `ranking.order_by_id` | `order_by_id` sorts by the raw string, so `"10" < "9"` lexicographically. | Critical |
| C2 | Sibling caller risk | `leaderboard.py` | Re-sorting inside `leaderboard.py` fixes one view; every other consumer of `order_by_id` stays wrong. | Major |

## Expected Patch Shape

A strong patch should be close to:

```python
return sorted(entries, key=lambda entry: int(entry["id"]))
```

Equivalent minimal implementations are acceptable if they:

- ids sort as 2, 9, 10
- `top_entry` returns the numerically smallest id
- `leaderboard.py` keeps calling `order_by_id`
- no dependencies are added

The executable reference patch is `tests/fixtures/GT029-code/answers/ranking.py`.

## Objective Checks

- `python -m unittest -v` passes after the patch.
- The change touches `ranking.py`, not only `leaderboard.py`.
- Tests are not modified and no dependency is added.
