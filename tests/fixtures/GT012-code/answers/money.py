def parse_money(value):
    """Parse a whole-dollar amount from CSV input."""
    if value is None or value == "":
        return 0
    return int(str(value).replace(",", ""))
