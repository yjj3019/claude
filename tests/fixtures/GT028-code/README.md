# GT028 Code Fixture

Bug report:

```text
KeyError: 'name' when reading the exported CSV, but the header clearly says name,score.
Please fix the bug.
```

Run checks with:

```text
python -m unittest -v
```

Expected root cause:

- The export starts with a UTF-8 BOM, so the first header parses as "\ufeffname" instead of "name".
- `loader.parse_export` must strip the BOM; renaming keys in `summary.py` is a caller-side workaround.
