from decimal import Decimal

from mm_std import random_choice, random_decimal, random_str_choice


def test_random_choice():
    assert random_choice(None) is None
    assert random_choice([]) is None
    assert random_choice(["a", "a"]) == "a"
    assert random_choice([1, 1]) == 1
    assert random_choice((1, 1)) == 1
    assert random_choice(1) == 1
    assert random_choice("abc") == "abc"


def test_random_decimal():
    from_ = Decimal("0")
    to = Decimal("100.00000")
    rnd = random_decimal(from_, to)
    rnd_ngidits = abs(rnd.as_tuple().exponent)
    assert rnd >= from_
    assert rnd <= to
    assert rnd_ngidits <= 5


def test_random_str_choice():
    assert random_str_choice(None) is None
    assert random_str_choice([]) is None
    assert random_str_choice("abc") == "abc"
    assert random_str_choice(["abc", "abc"]) == "abc"
