from decimal import Decimal

import pytest

from mm_std import number_with_separator, str_ends_with_any, str_starts_with_any, str_to_list
from mm_std.str import split_on_plus_minus_tokens, str_contains_any


def test_str_to_list():
    data = """
A # 1
b

c 3
b
    """
    assert str_to_list(data) == ["A # 1", "b", "c 3", "b"]
    assert str_to_list(data, lower=True, remove_comments=True, unique=True) == ["a", "b", "c 3"]
    assert str_to_list(data, lower=True, remove_comments=True, unique=True, split_line=True) == ["a", "b", "c", "3"]
    assert str_to_list(None) == []
    assert str_to_list("") == []
    assert str_to_list([1, 2, 3]) == ["1", "2", "3"]


def test_number_with_separator():
    assert number_with_separator(123.123) == "123.12"
    assert number_with_separator(123123) == "123_123"
    assert number_with_separator(Decimal("1231234")) == "1_231_234"


def test_str_starts_with_any():
    assert str_starts_with_any("a11", ["b1", "a1"])
    assert not str_starts_with_any("a21", ["b1", "a1"])


def test_str_ends_with_any():
    assert str_ends_with_any("zzza1", ["b1", "a1"])
    assert not str_ends_with_any("zzza21", ["b1", "a1"])


def test_str_contains_any():
    # Test basic functionality
    assert str_contains_any("hello world", ["hello", "test"]) is True
    assert str_contains_any("hello world", ["world"]) is True
    assert str_contains_any("hello world", ["test", "sample"]) is False

    # Test with empty inputs
    assert str_contains_any("hello world", []) is False
    assert str_contains_any("", ["test"]) is False
    assert str_contains_any("", []) is False

    # Test case sensitivity
    assert str_contains_any("Hello World", ["hello"]) is False
    assert str_contains_any("Hello World", ["Hello"]) is True

    # Test with special characters
    assert str_contains_any("example.com/path?query=value", ["query="]) is True
    assert str_contains_any("example.com/path?query=value", ["@"]) is False

    # Test with substring at different positions
    assert str_contains_any("testing", ["test"]) is True  # prefix
    assert str_contains_any("testing", ["ing"]) is True  # suffix
    assert str_contains_any("testing", ["sti"]) is True  # middle


def test_split_on_plus_minus_tokens():
    assert split_on_plus_minus_tokens("a b") == ["+ab"]
    assert split_on_plus_minus_tokens("ab") == ["+ab"]
    assert split_on_plus_minus_tokens("-a b") == ["-ab"]
    assert split_on_plus_minus_tokens("a + b + c") == ["+a", "+b", "+c"]
    assert split_on_plus_minus_tokens("-a + 12 b - c") == ["-a", "+12b", "-c"]

    with pytest.raises(ValueError):
        split_on_plus_minus_tokens(" ")
    with pytest.raises(ValueError):
        split_on_plus_minus_tokens("")
    with pytest.raises(ValueError):
        split_on_plus_minus_tokens("a++b")
    with pytest.raises(ValueError):
        split_on_plus_minus_tokens("a--b")
    with pytest.raises(ValueError):
        split_on_plus_minus_tokens("---ab")
    with pytest.raises(ValueError):
        split_on_plus_minus_tokens("a+b+")
    with pytest.raises(ValueError):
        split_on_plus_minus_tokens("a+b-")
