from validators import is_valid_email


def subscribe(email):
    """Add an address to the newsletter list. Raises ValueError for an invalid address."""
    if not is_valid_email(email):
        raise ValueError(f"invalid email: {email}")
    return {"email": email, "subscribed": True}
