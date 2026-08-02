def charge_total(prices):
    """Total of dollar prices, exact to the cent."""
    total_cents = 0
    for price in prices:
        total_cents += round(price * 100)
    return total_cents / 100
