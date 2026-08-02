def order_by_id(entries):
    """Entries sorted by their numeric string id, ascending."""
    return sorted(entries, key=lambda entry: entry["id"])
