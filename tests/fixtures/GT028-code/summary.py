from loader import RAW_EXPORT, parse_export


def names():
    """All names from the export, in file order."""
    return [row["name"] for row in parse_export(RAW_EXPORT)]
