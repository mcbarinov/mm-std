def replace_empty_dict_values(
    data: dict[object, object],
    defaults: dict[object, object] | None = None,
    zero_is_empty: bool = False,
    false_is_empty: bool = False,
) -> dict[object, object]:
    """Replace empty values in a dictionary with provided default values, or remove them if no default exists."""
    if defaults is None:
        defaults = {}
    result = {}
    for key, value in data.items():
        if value is None or value == "" or (zero_is_empty and value == 0) or (false_is_empty and value is False):
            value = defaults.get(key, None)  # noqa: PLW2901
        if value is not None:
            result[key] = value
    return result
