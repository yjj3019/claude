def parse_money(value):
    """Parse a whole-dollar amount from CSV input."""
    if value is None or value == "":
        return 0

    try:
        return int(value)
    except ValueError:
        return 0
