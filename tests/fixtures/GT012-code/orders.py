from money import parse_money


def total_orders(rows):
    return sum(parse_money(row["amount"]) for row in rows)
