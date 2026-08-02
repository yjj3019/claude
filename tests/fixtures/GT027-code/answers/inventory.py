_ITEMS = ["battery", "cable", "charger"]


def list_items():
    """Return a snapshot of the current inventory items."""
    return list(_ITEMS)


def item_count():
    return len(_ITEMS)
