def parse_amount(value):
    """Parse whole-dollar CSV amounts, including commas and accounting negatives."""
    if value is None or value == "":
        return 0

    text = str(value).strip().replace(",", "")
    if text.startswith("(") and text.endswith(")"):
        return -int(text[1:-1])
    return int(text)
