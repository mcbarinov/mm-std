from decimal import Decimal

import pytest

from mm_std import number_with_separator, str_ends_with_any, str_starts_with_any, str_to_list
from mm_std.str import split_on_plus_minus_tokens


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
