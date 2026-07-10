# GT014 Code Fixture

Bug report:

```text
Items that occur on the contract end date are being excluded. The end date should be included.
Please fix the bug without changing tests.
```

Run checks with:

```text
python -m unittest -v
```

Expected root cause:

- `periods.is_within_period` is the shared helper.
- It currently treats the end date as exclusive.
- Business rule for this fixture: start and end dates are both inclusive.
- Fix the helper, not individual callers.
