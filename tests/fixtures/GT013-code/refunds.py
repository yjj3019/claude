def total_refunds(rows):
    total = 0
    for row in rows:
        total += int(row["refund_amount"])
    return total
