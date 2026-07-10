from money import parse_money


def total_refunds(rows):
    return sum(parse_money(row["refund_amount"]) for row in rows)
