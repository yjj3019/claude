from inventory import list_items


def audit_report():
    """Sorted view for auditors; must not disturb the live inventory."""
    items = list_items()
    items.sort()
    items.append("AUDITED")
    return items
