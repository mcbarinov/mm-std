from mm_std.dict import replace_empty_dict_values


def test_replace_empty_dict_values():
    # Test basic replacement
    data = {"a": None, "b": "", "c": "value", "d": 0}
    defaults = {"a": "default_a", "b": "default_b", "e": "default_e"}

    result = replace_empty_dict_values(data, defaults)
    assert result == {"a": "default_a", "b": "default_b", "c": "value", "d": 0}

    # Test with zero_is_empty=True
    result_with_zero = replace_empty_dict_values(data, defaults, zero_is_empty=True)
    assert result_with_zero == {"a": "default_a", "b": "default_b", "c": "value"}

    # Test with no defaults provided
    result_no_defaults = replace_empty_dict_values(data)
    assert result_no_defaults == {"c": "value", "d": 0}

    # Test with empty data
    assert replace_empty_dict_values({}) == {}

    # Test with nested structures
    nested_data = {"a": None, "b": {"x": None, "y": "value"}}
    nested_defaults = {"a": "default_a"}
    # Note: The function doesn't recursively process nested dictionaries
    result_nested = replace_empty_dict_values(nested_data, nested_defaults)
    assert result_nested == {"a": "default_a", "b": {"x": None, "y": "value"}}
