# GT013 Code Fixture

Bug report:

```text
Totals are wrong for values with thousands separators and accounting negatives like "(1,200)".
Please fix the bug without changing tests.
```

Run checks with:

```text
python -m unittest -v
```

Expected root cause:

- `amounts.parse_amount` already handles commas and accounting negatives.
- `revenue.py` and `refunds.py` bypass that helper and call `int(...)` directly.
- Fix both callers to use the existing helper.
