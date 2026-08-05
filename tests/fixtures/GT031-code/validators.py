import re

EMAIL_RE = re.compile(r"^[A-Za-z0-9._-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_email(address):
    """Return True if address looks like a valid email."""
    return bool(EMAIL_RE.match(address))
