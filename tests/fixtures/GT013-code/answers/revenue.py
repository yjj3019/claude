from amounts import parse_amount


def total_revenue(rows):
    total = 0
    for row in rows:
        total += parse_amount(row["amount"])
    return total
