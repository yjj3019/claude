# GT030 Code Fixture

Bug report:

```text
Charging 0.10 + 0.20 shows 0.30000000000000004 on the statement.
Please fix the bug.
```

Run checks with:

```text
python -m unittest -v
```

Expected root cause:

- `wallet.charge_total` accumulates binary floats, so cent amounts drift.
- Rounding only in `statements.py` masks the display while totals stay wrong for other callers.
