from periods import is_within_period


def billable_events(events, start, end):
    return [event for event in events if is_within_period(event["day"], start, end)]
