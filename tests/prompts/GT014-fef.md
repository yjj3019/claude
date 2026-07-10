Use FEF coding behavior from the active runtime harness and Evidence policy.

Task:
Items that occur on the contract end date are being excluded. The end date should be included. Fix the bug in `tests/fixtures/GT014-code/` without changing tests.

Requirements:
- Fix the smallest correct diff.
- Identify the shared root cause before patching individual callers.
- Run or describe the failing check and passing check.
- Scan sibling callers for the same boundary bug and report what you found.
- Do not change tests.
- Do not add dependencies.
- Return the patch and the verification command/result.
