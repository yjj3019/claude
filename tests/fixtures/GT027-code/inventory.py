_ITEMS = ["battery", "cable", "charger"]


def list_items():
    """Return the current inventory items."""
    return _ITEMS


def item_count():
    return len(_ITEMS)
