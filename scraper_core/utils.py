def convert_to_integer(value: str):
    """
    Convert shorthand units like 'K', 'M', 'B' to integers.
    We can use libraries like 'pint' to do this, but for now going with simple logic for conversion.
    Args:
        value(str): movies count with shorthand unit eg. 4K, 24.k
    Returns:
        value(int): converted movies count
    """
    value = value.upper().strip()
    if value.endswith('K'):
        return int(float(value[:-1]) * 1_000)
    elif value.endswith('M'):
        return int(float(value[:-1]) * 1_000_000)
    elif value.endswith('B'):
        return int(float(value[:-1]) * 1_000_000_000)
    else:
        return int(value)
