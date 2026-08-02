from wallet import charge_total


def statement_line(prices):
    return "TOTAL: " + str(charge_total(prices))
