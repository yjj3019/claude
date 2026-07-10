def total_revenue(rows):
    total = 0
    for row in rows:
        total += int(row["amount"])
    return total
