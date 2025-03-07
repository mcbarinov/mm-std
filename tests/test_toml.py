from decimal import Decimal

from mm_std.toml import toml_dumps


def test_toml_dumps():
    data = {"string": "value", "integer": 42, "boolean": True, "decimal": Decimal("3.14")}
    result = toml_dumps(data)

    assert 'string = "value"' in result
    assert "integer = 42" in result
    assert "boolean = true" in result
    assert "decimal = 3.14" in result
