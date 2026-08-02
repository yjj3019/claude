# GT029 Code Fixture

Bug report:

```text
Entry id "10" is ranked before id "9". Ids are numeric strings and must sort numerically.
Please fix the bug.
```

Run checks with:

```text
python -m unittest -v
```

Expected root cause:

- `ranking.order_by_id` sorts by the raw string, so "10" < "9" lexicographically.
- Fixing only `leaderboard.py` (re-sorting at the call site) leaves other consumers of `order_by_id` wrong.
