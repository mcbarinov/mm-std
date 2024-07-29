from decimal import Decimal

from mm_std import print_console


def test_console_print():
    print_console(Decimal("1.123"), print_json=True)
