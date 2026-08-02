def add_tag(tag, tags=None):
    """Return the tag list for one record with the new tag appended."""
    if tags is None:
        tags = []
    tags.append(tag)
    return tags
