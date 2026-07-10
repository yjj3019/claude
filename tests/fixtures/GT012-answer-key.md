# GT012 Answer Key

Use this key to score `tests/fixtures/GT012-code/` runs.

## Seeded Bug

| ID | Type | Location | Expected Finding | Severity |
|---|---|---|---|---|
| C1 | Root cause | `money.py::parse_money` | The shared parser calls `int(value)` directly, so values with thousands separators such as `"1,200"` fail. | Critical |
| C2 | Bad error handling | `money.py::parse_money` | Invalid non-empty values are silently converted to `0`, hiding bad data. Blank and `None` may remain `0`. | Major |
| C3 | Sibling caller risk | `orders.py` and `refunds.py` | Both callers depend on `parse_money`; caller-only fixes are incomplete. | Major |

## Expected Patch Shape

A strong patch should be close to:

```python
def parse_money(value):
    """Parse a whole-dollar amount from CSV input."""
    if value is None or value == "":
        return 0
    return int(str(value).replace(",", ""))
```

Equivalent minimal implementations are acceptable if they:

- parse `"1,200"` as `1200`
- keep blank string and `None` as `0`
- raise `ValueError` for invalid non-empty values
- leave `orders.py` and `refunds.py` using `parse_money`
- do not add dependencies

## Objective Checks

Run:

```text
python -m unittest -v
```

Expected: all six tests pass after applying the patch.

## Scoring Notes

- Award root-cause points only when the shared parser is fixed.
- Award sibling coverage points when both caller paths pass and the response notes that both callers share the parser, or the diff plainly preserves shared-parser use.
- Penalize fixes that add comma stripping in each caller instead of fixing `parse_money`.
- Penalize any change to tests that weakens the expected behavior.
