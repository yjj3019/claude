from ranking import order_by_id


def top_entry(entries):
    """The entry with the smallest numeric id."""
    return order_by_id(entries)[0]
