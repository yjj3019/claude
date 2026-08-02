RAW_EXPORT = "\ufeffname,score\nalice,10\nbob,7\n"


def parse_export(text):
    """Parse a small CSV export into a list of row dicts."""
    lines = text.strip().splitlines()
    headers = lines[0].split(",")
    return [dict(zip(headers, line.split(","))) for line in lines[1:]]
