UNITS = [("GB", 1073741824), ("MB", 1048576), ("KB", 1024), ("B", 1)]


def get_size_in_largest_unit(size: int) -> tuple[str, int]:
    """
    Returns the size of the file(s) in the largest possible unit.
    """

    for unit, unit_size in UNITS:
        if size >= unit_size:
            return unit, round(size / unit_size, 2)
    return "B", size
