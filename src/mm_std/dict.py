from collections import defaultdict
from collections.abc import Mapping, MutableMapping
from typing import TypeVar, cast

K = TypeVar("K")
V = TypeVar("V")
DictType = TypeVar("DictType", bound=MutableMapping[K, V])  # type: ignore[valid-type]


def replace_empty_dict_entries(
    data: DictType,
    defaults: Mapping[K, V] | None = None,
    zero_is_empty: bool = False,
    false_is_empty: bool = False,
    empty_string_is_empty: bool = True,
) -> DictType:
    """
    Replace empty entries in a dictionary with provided default values,
    or remove them if no default is available. Returns the same type as the input dictionary.
    """
    if defaults is None:
        defaults = {}

    try:
        if isinstance(data, defaultdict):
            result: MutableMapping[K, V] = defaultdict(data.default_factory)
        else:
            result = data.__class__()
    except Exception:
        result = {}

    for key, value in data.items():
        should_replace = (
            value is None
            or (empty_string_is_empty and value == "")
            or (zero_is_empty and value == 0)
            or (false_is_empty and value is False)
        )

        if should_replace:
            if key in defaults:
                new_value = defaults[key]
            else:
                continue  # Skip the key if no default is available
        else:
            new_value = value

        result[key] = new_value
    return cast(DictType, result)
