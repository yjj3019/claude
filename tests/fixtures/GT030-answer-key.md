# GT030 Answer Key

Use this key to score `tests/fixtures/GT030-code/` runs.

## Seeded Bug

| ID | Type | Location | Expected Finding | Severity |
|---|---|---|---|---|
| C1 | Root cause | `wallet.charge_total` | `charge_total` accumulates binary floats, so cent amounts drift. | Critical |
| C2 | Sibling caller risk | `statements.py` | Rounding only in `statements.py` masks the display while totals stay wrong for other callers. | Major |

## Expected Patch Shape

A strong patch should be close to:

```python
total_cents += round(price * 100)
...
return total_cents / 100
```

Equivalent minimal implementations are acceptable if they:

- 0.10 + 0.20 totals exactly 0.30
- repeated cent amounts stay exact
- `statements.py` keeps calling `charge_total`
- no dependencies are added

The executable reference patch is `tests/fixtures/GT030-code/answers/wallet.py`.

## Objective Checks

- `python -m unittest -v` passes after the patch.
- The change touches `wallet.py`, not only `statements.py`.
- Tests are not modified and no dependency is added.
