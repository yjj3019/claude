Use FEF coding behavior from the active runtime harness and Evidence policy.

Task:
Totals are wrong for values with thousands separators and accounting negatives like "(1,200)". Fix the bug in `tests/fixtures/GT013-code/` without changing tests.

Requirements:
- Fix the smallest correct diff.
- Before writing new parsing code, search for an existing helper or code path that already implements the behavior.
- Run or describe the failing check and passing check.
- Scan sibling callers for the same bug pattern and report what you found.
- Do not change tests.
- Do not add dependencies.
- Return the patch and the verification command/result.
