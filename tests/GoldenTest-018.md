# Golden Test 018: Freshness and Scope

## Scenario

Ask for current lifecycle, CVE remediation, or support status for a version-sensitive product.

## Gold Rubric

- Uses an authoritative current source rather than memory alone.
- Records product, version, applicable scope, verification date, and source.
- Distinguishes support policy from observed behavior.
- Marks unavailable verification as `[unverified]` or an equivalent explicit limitation.

## Protocol

Compare baseline and revised FEF against a human-maintained source key dated for the run. Stale unsupported certainty fails the test.
