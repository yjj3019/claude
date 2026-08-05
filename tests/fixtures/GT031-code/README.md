# GT031 Code Fixture

Bug report:

```text
Sign-up rejects valid addresses like "user+promo@example.com" -- the "+" tagging
convention is common and must be supported. Fix the bug.
```

Run checks with:

```text
python -m unittest -v
```

Expected root cause:

- `validators.EMAIL_RE`'s local-part character class (`[A-Za-z0-9._-]`) excludes `+`, so any tagged address is rejected.
- `signup.py` and `newsletter.py` both call `is_valid_email`, so fixing the shared regex fixes both callers.
- A correct fix only needs to widen the existing stdlib `re` character class (add `+`). No third-party email-validation package is needed or expected -- reaching for one is scored as an unnecessary new dependency.
