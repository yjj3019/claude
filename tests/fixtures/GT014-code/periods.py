from datetime import date


def parse_day(value):
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def is_within_period(day, start, end):
    """Return whether day falls within the service period."""
    return parse_day(start) <= parse_day(day) < parse_day(end)
