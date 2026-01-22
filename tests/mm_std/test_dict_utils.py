"""Tests for dict_utils module."""

from collections import OrderedDict, defaultdict
from decimal import Decimal

import pytest

from mm_std import compact_dict


class TestCompactDict:
    """Tests for compact_dict function."""

    def test_removes_none_values(self) -> None:
        """None values are removed by default."""
        data = {"a": 1, "b": None, "c": "hello"}
        result = compact_dict(data)
        assert result == {"a": 1, "c": "hello"}

    def test_removes_empty_strings_by_default(self) -> None:
        """Empty strings are removed by default."""
        data = {"a": 1, "b": "", "c": "hello"}
        result = compact_dict(data)
        assert result == {"a": 1, "c": "hello"}

    def test_preserves_non_empty_values(self) -> None:
        """Non-empty values are preserved."""
        data = {"a": 1, "b": "text", "c": [1, 2, 3], "d": {"nested": True}}
        result = compact_dict(data)
        assert result == data


class TestCompactDictTreatZeroAsEmpty:
    """Tests for treat_zero_as_empty parameter."""

    @pytest.mark.parametrize(
        ("zero_value",),
        [
            (0,),
            (0.0,),
            (Decimal(0),),
            (Decimal("0.00"),),
        ],
    )
    def test_removes_zero_when_enabled(self, zero_value: float | Decimal) -> None:
        """Zero values are removed when treat_zero_as_empty=True."""
        data = {"a": 1, "b": zero_value, "c": "hello"}
        result = compact_dict(data, treat_zero_as_empty=True)
        assert result == {"a": 1, "c": "hello"}

    @pytest.mark.parametrize(
        ("zero_value",),
        [
            (0,),
            (0.0,),
            (Decimal(0),),
        ],
    )
    def test_preserves_zero_by_default(self, zero_value: float | Decimal) -> None:
        """Zero values are preserved by default."""
        data = {"a": 1, "b": zero_value}
        result = compact_dict(data)
        assert "b" in result
        assert result["b"] == zero_value


class TestCompactDictTreatFalseAsEmpty:
    """Tests for treat_false_as_empty parameter."""

    def test_removes_false_when_enabled(self) -> None:
        """False is removed when treat_false_as_empty=True."""
        data = {"a": 1, "b": False, "c": True}
        result = compact_dict(data, treat_false_as_empty=True)
        assert result == {"a": 1, "c": True}

    def test_preserves_false_by_default(self) -> None:
        """False is preserved by default."""
        data = {"a": 1, "b": False, "c": True}
        result = compact_dict(data)
        assert result == {"a": 1, "b": False, "c": True}


class TestCompactDictTreatEmptyStringAsEmpty:
    """Tests for treat_empty_string_as_empty parameter."""

    def test_preserves_empty_string_when_disabled(self) -> None:
        """Empty strings are preserved when treat_empty_string_as_empty=False."""
        data = {"a": 1, "b": "", "c": "hello"}
        result = compact_dict(data, treat_empty_string_as_empty=False)
        assert result == {"a": 1, "b": "", "c": "hello"}

    def test_removes_empty_string_when_enabled(self) -> None:
        """Empty strings are removed when treat_empty_string_as_empty=True (default)."""
        data = {"a": 1, "b": "", "c": "hello"}
        result = compact_dict(data, treat_empty_string_as_empty=True)
        assert result == {"a": 1, "c": "hello"}


class TestCompactDictDefaults:
    """Tests for defaults parameter."""

    def test_replaces_empty_values_with_defaults(self) -> None:
        """Empty values are replaced with values from defaults."""
        data = {"a": 1, "b": None, "c": ""}
        defaults = {"b": 100, "c": "default"}
        result = compact_dict(data, defaults=defaults)
        assert result == {"a": 1, "b": 100, "c": "default"}

    def test_keys_without_defaults_are_removed(self) -> None:
        """Empty keys not in defaults are removed."""
        data = {"a": 1, "b": None, "c": None}
        defaults = {"b": 100}
        result = compact_dict(data, defaults=defaults)
        assert result == {"a": 1, "b": 100}
        assert "c" not in result

    def test_defaults_work_with_zero_parameter(self) -> None:
        """Defaults work with treat_zero_as_empty=True."""
        data = {"a": 1, "b": 0}
        defaults = {"b": 42}
        result = compact_dict(data, defaults=defaults, treat_zero_as_empty=True)
        assert result == {"a": 1, "b": 42}

    def test_defaults_work_with_false_parameter(self) -> None:
        """Defaults work with treat_false_as_empty=True."""
        data = {"a": 1, "b": False}
        defaults = {"b": True}
        result = compact_dict(data, defaults=defaults, treat_false_as_empty=True)
        assert result == {"a": 1, "b": True}


class TestCompactDictTypePreservation:
    """Tests for type preservation behavior."""

    def test_dict_returns_dict(self) -> None:
        """Regular dict input returns regular dict."""
        data: dict[str, int | None] = {"a": 1, "b": None}
        result = compact_dict(data)
        assert type(result) is dict
        assert result == {"a": 1}

    def test_ordered_dict_returns_ordered_dict(self) -> None:
        """OrderedDict input returns OrderedDict."""
        data: OrderedDict[str, int | None] = OrderedDict([("a", 1), ("b", None), ("c", 3)])
        result = compact_dict(data)
        assert type(result) is OrderedDict
        assert list(result.keys()) == ["a", "c"]

    def test_defaultdict_returns_defaultdict(self) -> None:
        """Input defaultdict returns defaultdict with preserved default_factory."""
        data: defaultdict[str, int | None] = defaultdict(int)
        data["a"] = 1
        data["b"] = None
        result = compact_dict(data)
        assert type(result) is defaultdict
        assert result.default_factory is int
        assert dict(result) == {"a": 1}


class TestCompactDictEdgeCases:
    """Tests for edge cases."""

    def test_empty_input_dict(self) -> None:
        """Empty dict returns empty dict."""
        data: dict[str, int] = {}
        result = compact_dict(data)
        assert result == {}

    def test_all_values_empty_returns_empty_dict(self) -> None:
        """Dict with all empty values returns empty dict."""
        data = {"a": None, "b": "", "c": None}
        result = compact_dict(data)
        assert result == {}

    def test_false_and_zero_distinction(self) -> None:
        """False and 0 are handled independently."""
        data = {"a": False, "b": 0, "c": 1}
        # Only remove False, keep 0
        result = compact_dict(data, treat_false_as_empty=True, treat_zero_as_empty=False)
        assert result == {"b": 0, "c": 1}
        # Only remove 0, keep False
        result = compact_dict(data, treat_false_as_empty=False, treat_zero_as_empty=True)
        assert result == {"a": False, "c": 1}
        # Remove both
        result = compact_dict(data, treat_false_as_empty=True, treat_zero_as_empty=True)
        assert result == {"c": 1}

    def test_zero_not_treated_as_false(self) -> None:
        """Integer 0 is not affected by treat_false_as_empty."""
        data = {"a": 0, "b": False}
        result = compact_dict(data, treat_false_as_empty=True, treat_zero_as_empty=False)
        assert result == {"a": 0}

    def test_false_not_treated_as_zero(self) -> None:
        """Boolean False is not affected by treat_zero_as_empty."""
        data = {"a": 0, "b": False}
        result = compact_dict(data, treat_zero_as_empty=True, treat_false_as_empty=False)
        assert result == {"b": False}
