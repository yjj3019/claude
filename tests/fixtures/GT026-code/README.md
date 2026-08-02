# GT026 Code Fixture

Bug report:

```text
Records are sharing tags: tagging the second record shows the first record's tag too.
Please fix the bug.
```

Run checks with:

```text
python -m unittest -v
```

Expected root cause:

- `tagging.add_tag` uses a mutable default argument, so one list is shared across every call.
- Fixing only `reports.py` (e.g. passing `[]` at the call site) hides the defect for other callers.
