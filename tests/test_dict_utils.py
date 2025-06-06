from collections import OrderedDict, defaultdict
from decimal import Decimal

from mm_std import replace_empty_dict_entries


class TestReplaceEmptyDictEntries:
    def test_basic_none_removal(self):
        """Test that None values are removed by default."""
        data = {"a": 1, "b": None, "c": "hello"}
        result = replace_empty_dict_entries(data)

        assert result == {"a": 1, "c": "hello"}
        assert type(result) is dict

    def test_none_replacement_with_defaults(self):
        """Test that None values are replaced with defaults when provided."""
        data = {"a": 1, "b": None, "c": "hello"}
        defaults = {"b": 42}
        result = replace_empty_dict_entries(data, defaults)

        assert result == {"a": 1, "b": 42, "c": "hello"}

    def test_empty_string_handling(self):
        """Test empty string handling with treat_empty_string_as_empty flag."""
        data = {"a": "hello", "b": "", "c": "world"}

        # Default behavior - empty strings are treated as empty
        result = replace_empty_dict_entries(data)
        assert result == {"a": "hello", "c": "world"}

        # With defaults
        result = replace_empty_dict_entries(data, {"b": "default"})
        assert result == {"a": "hello", "b": "default", "c": "world"}

        # Disabled - empty strings are kept
        result = replace_empty_dict_entries(data, treat_empty_string_as_empty=False)
        assert result == {"a": "hello", "b": "", "c": "world"}

    def test_zero_handling(self):
        """Test zero handling with treat_zero_as_empty flag."""
        data = {"a": 1, "b": 0, "c": 0.0, "d": Decimal("0")}

        # Default behavior - zeros are kept
        result = replace_empty_dict_entries(data)
        assert result == {"a": 1, "b": 0, "c": 0.0, "d": Decimal("0")}

        # Enabled - zeros are removed
        result = replace_empty_dict_entries(data, treat_zero_as_empty=True)
        assert result == {"a": 1}

        # With defaults
        defaults = {"b": 10, "c": 3.14, "d": Decimal("100")}
        result = replace_empty_dict_entries(data, defaults, treat_zero_as_empty=True)
        assert result == {"a": 1, "b": 10, "c": 3.14, "d": Decimal("100")}

    def test_false_handling(self):
        """Test False handling with treat_false_as_empty flag."""
        data = {"a": True, "b": False, "c": "hello"}

        # Default behavior - False is kept
        result = replace_empty_dict_entries(data)
        assert result == {"a": True, "b": False, "c": "hello"}

        # Enabled - False is removed
        result = replace_empty_dict_entries(data, treat_false_as_empty=True)
        assert result == {"a": True, "c": "hello"}

        # With defaults
        result = replace_empty_dict_entries(data, {"b": True}, treat_false_as_empty=True)
        assert result == {"a": True, "b": True, "c": "hello"}

    def test_bool_vs_int_conflict(self):
        """Test that False is not treated as zero when both flags are enabled."""
        data = {"a": False, "b": 0, "c": True, "d": 1}
        defaults = {"a": "false_default", "b": "zero_default"}

        result = replace_empty_dict_entries(data, defaults, treat_zero_as_empty=True, treat_false_as_empty=True)

        # False should be handled by treat_false_as_empty, not treat_zero_as_empty
        assert result == {"a": "false_default", "b": "zero_default", "c": True, "d": 1}

    def test_type_preservation_dict(self):
        """Test that regular dict type is preserved."""
        data = {"a": 1, "b": None}
        result = replace_empty_dict_entries(data)

        assert type(result) is dict
        assert result == {"a": 1}

    def test_type_preservation_defaultdict(self):
        """Test that defaultdict type and default_factory are preserved."""
        data = defaultdict(list, {"a": [1, 2], "b": None, "c": []})
        result = replace_empty_dict_entries(data)

        assert isinstance(result, defaultdict)
        assert result.default_factory is list
        assert result == {"a": [1, 2], "c": []}

        # Test that default_factory still works
        result["new_key"].append("test")
        assert result["new_key"] == ["test"]

    def test_type_preservation_ordered_dict(self):
        """Test that OrderedDict type is preserved."""
        data = OrderedDict([("a", 1), ("b", None), ("c", 2)])
        result = replace_empty_dict_entries(data)

        assert type(result) is OrderedDict
        assert list(result.keys()) == ["a", "c"]
        assert result == OrderedDict([("a", 1), ("c", 2)])

    def test_all_flags_combined(self):
        """Test behavior when all treat_*_as_empty flags are enabled."""
        data = {
            "none": None,
            "empty_str": "",
            "zero_int": 0,
            "zero_float": 0.0,
            "zero_decimal": Decimal("0"),
            "false": False,
            "keep_this": "value",
            "keep_true": True,
            "keep_one": 1,
        }

        result = replace_empty_dict_entries(
            data, treat_zero_as_empty=True, treat_false_as_empty=True, treat_empty_string_as_empty=True
        )

        assert result == {"keep_this": "value", "keep_true": True, "keep_one": 1}

    def test_empty_dict(self):
        """Test behavior with empty input dictionary."""
        result = replace_empty_dict_entries({})
        assert result == {}
        assert type(result) is dict

    def test_no_empty_values(self):
        """Test behavior when no values are considered empty."""
        data = {"a": 1, "b": "hello", "c": True}
        result = replace_empty_dict_entries(data)

        assert result == data
        assert result is not data  # Should be a new instance

    def test_partial_defaults(self):
        """Test behavior when defaults are provided only for some empty keys."""
        data = {"a": None, "b": None, "c": 1}
        defaults = {"a": "replaced"}
        result = replace_empty_dict_entries(data, defaults)

        # "a" gets replaced, "b" gets removed, "c" stays
        assert result == {"a": "replaced", "c": 1}

    def test_numeric_edge_cases(self):
        """Test edge cases with different numeric types."""
        data = {
            "negative_zero": -0.0,
            "positive_zero": +0.0,
            "decimal_zero": Decimal("0.00"),
            "small_float": 0.0000001,
            "negative": -1,
        }

        result = replace_empty_dict_entries(data, treat_zero_as_empty=True)

        # Only actual zeros should be removed
        assert result == {"small_float": 0.0000001, "negative": -1}
