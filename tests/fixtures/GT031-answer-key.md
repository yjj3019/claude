# GT031 Answer Key

Use this key to score `tests/fixtures/GT031-code/` runs.

## Seeded Bug

| ID | Type | Location | Expected Finding | Severity |
|---|---|---|---|---|
| C1 | Root cause | `validators.EMAIL_RE` | The local-part character class (`[A-Za-z0-9._-]`) excludes `+`, so tagged addresses like `user+promo@example.com` are rejected. | Critical |
| C2 | Sibling caller risk | `signup.py`, `newsletter.py` | Both call `is_valid_email` directly; patching either caller's own logic instead of the shared regex leaves the other broken. | Major |
| C3 | Dependency trap | n/a | The bug reads like a classic "reach for an email-validation library" case; a correct minimal fix stays in stdlib `re`. | Major |

## Expected Patch Shape

A strong patch should be close to:

```python
EMAIL_RE = re.compile(r"^[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
```

Equivalent minimal implementations are acceptable if they:

- accept `user+promo@example.com`
- still reject addresses with no `@`
- `signup.py` and `newsletter.py` keep calling `is_valid_email`
- no third-party dependency is added (only the stdlib `re` module)

The executable reference patch is `tests/fixtures/GT031-code/answers/validators.py`.

## Objective Checks

- `python -m unittest -v` passes after the patch.
- The change touches `validators.py`, not only `signup.py`/`newsletter.py`.
- Tests are not modified and no dependency is added.
