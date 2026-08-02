from amounts import parse_amount


def total_refunds(rows):
    total = 0
    for row in rows:
        total += parse_amount(row["refund_amount"])
    return total
