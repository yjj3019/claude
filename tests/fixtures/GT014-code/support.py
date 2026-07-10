from periods import is_within_period


def entitled_tickets(tickets, start, end):
    return [ticket for ticket in tickets if is_within_period(ticket["day"], start, end)]
