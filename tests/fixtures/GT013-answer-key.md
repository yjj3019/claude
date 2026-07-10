# GT013 Answer Key

Use this key to score `tests/fixtures/GT013-code/` runs.

## Seeded Issues

| ID | Type | Location | Expected Finding | Severity |
|---|---|---|---|---|
| C1 | Existing helper bypassed | `revenue.py::total_revenue` | Caller uses `int(row["amount"])` instead of existing `amounts.parse_amount`. | Major |
| C2 | Existing helper bypassed | `refunds.py::total_refunds` | Sibling caller uses `int(row["refund_amount"])` instead of existing `amounts.parse_amount`. | Major |

## Expected Patch Shape

A strong patch should be close to:

```python
from amounts import parse_amount


def total_revenue(rows):
    total = 0
    for row in rows:
        total += parse_amount(row["amount"])
    return total
```

and the equivalent change in `refunds.py`.

Equivalent minimal implementations are acceptable if they:

- reuse `amounts.parse_amount`
- fix both revenue and refund paths
- do not duplicate parsing logic in the callers
- do not change tests
- do not add dependencies

## Objective Checks

Run:

```text
python -m unittest -v
```

Expected: all four tests pass after applying the patch.
