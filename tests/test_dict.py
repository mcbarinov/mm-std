from collections import defaultdict
from collections.abc import Mapping
from typing import TypedDict

import pytest

from mm_std import replace_empty_dict_entries


class SampleDict(TypedDict, total=False):
    a: str
    b: int
    c: bool
    d: str


@pytest.mark.parametrize(
    "data,defaults,expected,flags",
    [
        # Replace empty string with default
        ({"a": ""}, {"a": "x"}, {"a": "x"}, {"empty_string_is_empty": True}),
        # Keep empty string if flag is off
        ({"a": ""}, {"a": "X"}, {"a": ""}, {"empty_string_is_empty": False}),
        # Replace False with default
        ({"a": False}, {"a": True}, {"a": True}, {"false_is_empty": True}),
        # Keep False if flag is off
        ({"a": False}, {"a": True}, {"a": False}, {"false_is_empty": False}),
        # Replace 0 with default
        ({"a": 0}, {"a": 5}, {"a": 5}, {"zero_is_empty": True}),
        # Keep 0 if flag is off
        ({"a": 0}, {"a": 5}, {"a": 0}, {"zero_is_empty": False}),
        # Remove empty key with no default
        ({"a": None, "b": ""}, {"a": "x"}, {"a": "x"}, {"empty_string_is_empty": True}),
        ({"a": "", "b": ""}, {}, {}, {"empty_string_is_empty": True}),
        ({"a": 0, "b": False}, {}, {}, {"zero_is_empty": True, "false_is_empty": True}),
    ],
)
def test_replace_empty_dict_entries_flags(
    data: dict[str, object],
    defaults: Mapping[str, object],
    expected: dict[str, object],
    flags: dict[str, bool],
) -> None:
    result = replace_empty_dict_entries(
        data,
        defaults=defaults,
        zero_is_empty=flags.get("zero_is_empty", False),
        false_is_empty=flags.get("false_is_empty", False),
        empty_string_is_empty=flags.get("empty_string_is_empty", True),
    )
    assert dict(result) == expected


def test_preserves_input_type_with_defaultdict() -> None:
    original = defaultdict(lambda: "default", {"a": None, "b": "keep"})
    result = replace_empty_dict_entries(original, {"a": "x"})
    assert isinstance(result, defaultdict)
    assert result["a"] == "x"
    assert result["b"] == "keep"
    assert result["zzz"] == "default"  # Check factory works


def test_typed_dict_support() -> None:
    original: SampleDict = {"a": "", "b": 0, "c": False}
    defaults: SampleDict = {"a": "filled", "b": 10, "c": True}
    result = replace_empty_dict_entries(
        original,
        defaults=defaults,
        zero_is_empty=True,
        false_is_empty=True,
        empty_string_is_empty=True,
    )
    assert result == {"a": "filled", "b": 10, "c": True}


def test_removal_behavior() -> None:
    # Ensure keys without defaults are dropped
    data = {"a": "", "b": None, "c": 0, "d": False}
    defaults = {"a": "A"}  # Only 'a' has default
    result = replace_empty_dict_entries(
        data,
        defaults=defaults,
        zero_is_empty=True,
        false_is_empty=True,
        empty_string_is_empty=True,
    )
    assert result == {"a": "A"}
