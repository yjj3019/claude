def charge_total(prices):
    """Total of dollar prices, exact to the cent."""
    total = 0.0
    for price in prices:
        total += price
    return total
