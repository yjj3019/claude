# GT014 Answer Key

Use this key to score `tests/fixtures/GT014-code/` runs.

## Seeded Issue

| ID | Type | Location | Expected Finding | Severity |
|---|---|---|---|---|
| C1 | Boundary bug | `periods.py::is_within_period` | The helper uses `< parse_day(end)`, treating the end date as exclusive. The fixture requires inclusive start and inclusive end. | Critical |
| C2 | Sibling caller risk | `billing.py` and `support.py` | Both callers depend on `is_within_period`; caller-only fixes are incomplete. | Major |

## Expected Patch Shape

A strong patch should be close to:

```python
def is_within_period(day, start, end):
    """Return whether day falls within the service period."""
    return parse_day(start) <= parse_day(day) <= parse_day(end)
```

Equivalent minimal implementations are acceptable if they:

- include the start date
- include the end date
- exclude the day after the end date
- leave `billing.py` and `support.py` using `is_within_period`
- do not change tests
- do not add dependencies

## Objective Checks

Run:

```text
python -m unittest -v
```

Expected: all five tests pass after applying the patch.
