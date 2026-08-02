from tagging import add_tag


def tag_records(records):
    """Each record starts with its own empty tag list."""
    return [add_tag(record["tag"]) for record in records]
