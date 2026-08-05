from validators import is_valid_email


def register(email):
    """Register a new account. Raises ValueError for an invalid address."""
    if not is_valid_email(email):
        raise ValueError(f"invalid email: {email}")
    return {"email": email, "status": "registered"}
