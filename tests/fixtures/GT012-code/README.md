# GT012 Code Fixture

Bug report:

```text
Totals are wrong when amount values contain comma thousands separators, for example "1,200".
Please fix the bug.
```

Run checks with:

```text
python -m unittest -v
```

Expected root cause:

- `money.parse_money` is the shared parser.
- It incorrectly returns `0` for values such as `"1,200"` because `int("1,200")` fails and the exception is swallowed.
- Fixing only `orders.py` leaves `refunds.py` broken.
