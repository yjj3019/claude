# GT027 Code Fixture

Bug report:

```text
After running an audit report, the live inventory is reordered and contains "AUDITED".
Please fix the bug.
```

Run checks with:

```text
python -m unittest -v
```

Expected root cause:

- `inventory.list_items` returns the internal list itself, so callers mutate module state through the alias.
- Fixing only `audit.py` (copying at the call site) leaves every other caller exposed to the same defect.
