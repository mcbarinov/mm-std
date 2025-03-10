def replace_empty_dict_values(
    data: dict[object, object],
    defaults: dict[object, object] | None = None,
    zero_is_empty: bool = False,
) -> dict[object, object]:
    """
    Replace empty values in a dictionary with provided default values, or remove them if no default exists.

    An "empty" value is defined as one of the following:
      - None
      - An empty string ("")

    If the flag `zero_is_empty` is True, the numeric value 0 is also considered empty.

    For each key in the input dictionary `data`, if its value is empty, the function checks the
    `defaults` dictionary for a replacement. If a default exists, it uses that value; otherwise, the
    key is omitted from the resulting dictionary.

    Parameters:
        data (dict[object, object]): The input dictionary with key-value pairs to process.
        defaults (dict[object, object] | None, optional): A dictionary of default values to use as
            replacements for empty entries. If None, no default replacements are applied.
        zero_is_empty (bool, optional): If True, treats the value 0 as empty. Defaults to False.

    Returns:
        dict[object, object]: A new dictionary with empty values replaced by defaults or removed if no
        default is provided.
    """
    if defaults is None:
        defaults = {}
    result = {}
    for key, value in data.items():
        if value is None or value == "" or (zero_is_empty and value == 0):
            value = defaults.get(key, None)  # noqa: PLW2901
        if value is not None:
            result[key] = value
    return result
