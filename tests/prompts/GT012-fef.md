Use FEF coding behavior from the active runtime harness and Evidence policy.

Task:
The tests fail for amounts like "1,200". Fix the bug in `tests/fixtures/GT012-code/`.

Requirements:
- Fix the smallest shared root cause.
- Run or describe the failing check and passing check.
- Scan sibling callers for the same bug pattern and report what you found.
- Do not add dependencies.
- Return the patch and the verification command/result.
