import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from uuid import UUID

import pytest

from mm_std.json_utils import ExtendedJSONEncoder, json_dumps


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@dataclass
class Person:
    name: str
    age: int
    birth_date: date


class CustomType:
    def __init__(self, value: str) -> None:
        self.value = value


class TestExtendedJSONEncoder:
    def test_built_in_types_unchanged(self):
        """Test that built-in JSON types work normally."""
        data = {"str": "hello", "int": 42, "float": 3.14, "bool": True, "list": [1, 2], "dict": {"nested": "value"}, "null": None}
        result = json.dumps(data, cls=ExtendedJSONEncoder)
        expected = json.dumps(data)
        assert result == expected

    def test_datetime_serialization(self):
        """Test datetime serialization to ISO format."""
        dt = datetime(2023, 6, 15, 14, 30, 45)
        result = json.dumps(dt, cls=ExtendedJSONEncoder)
        assert result == '"2023-06-15T14:30:45"'

    def test_date_serialization(self):
        """Test date serialization to ISO format."""
        d = date(2023, 6, 15)
        result = json.dumps(d, cls=ExtendedJSONEncoder)
        assert result == '"2023-06-15"'

    def test_uuid_serialization(self):
        """Test UUID serialization to string."""
        uuid_obj = UUID("12345678-1234-5678-1234-567812345678")
        result = json.dumps(uuid_obj, cls=ExtendedJSONEncoder)
        assert result == '"12345678-1234-5678-1234-567812345678"'

    def test_decimal_serialization(self):
        """Test Decimal serialization to string."""
        decimal_obj = Decimal("123.456")
        result = json.dumps(decimal_obj, cls=ExtendedJSONEncoder)
        assert result == '"123.456"'

    def test_path_serialization(self):
        """Test Path serialization to string."""
        path_obj = Path("/home/user/file.txt")
        result = json.dumps(path_obj, cls=ExtendedJSONEncoder)
        assert result == '"/home/user/file.txt"'

    def test_set_serialization(self):
        """Test set serialization to list."""
        set_obj = {1, 2, 3}
        result = json.loads(json.dumps(set_obj, cls=ExtendedJSONEncoder))
        assert sorted(result) == [1, 2, 3]

    def test_frozenset_serialization(self):
        """Test frozenset serialization to list."""
        frozenset_obj = frozenset({1, 2, 3})
        result = json.loads(json.dumps(frozenset_obj, cls=ExtendedJSONEncoder))
        assert sorted(result) == [1, 2, 3]

    def test_bytes_serialization(self):
        """Test bytes serialization using latin-1 decoding."""
        bytes_obj = b"hello world"
        result = json.dumps(bytes_obj, cls=ExtendedJSONEncoder)
        assert result == '"hello world"'

    def test_complex_serialization(self):
        """Test complex number serialization to dict."""
        complex_obj = complex(3, 4)
        result = json.loads(json.dumps(complex_obj, cls=ExtendedJSONEncoder))
        assert result == {"real": 3.0, "imag": 4.0}

    def test_enum_serialization(self):
        """Test enum serialization to value."""
        result = json.dumps(Color.RED, cls=ExtendedJSONEncoder)
        assert result == '"red"'

    def test_exception_serialization(self):
        """Test exception serialization to string."""
        exc = ValueError("Something went wrong")
        result = json.dumps(exc, cls=ExtendedJSONEncoder)
        assert result == '"Something went wrong"'

    def test_dataclass_serialization(self):
        """Test dataclass serialization to dict."""
        person = Person("Alice", 30, date(1993, 6, 15))
        result = json.loads(json.dumps(person, cls=ExtendedJSONEncoder))
        assert result == {"name": "Alice", "age": 30, "birth_date": "1993-06-15"}

    def test_nested_dataclass_serialization(self):
        """Test nested objects with dataclass containing special types."""
        person = Person("Bob", 25, date(1998, 12, 25))
        data = {"person": person, "uuid": UUID("12345678-1234-5678-1234-567812345678")}
        result = json.loads(json.dumps(data, cls=ExtendedJSONEncoder))

        expected = {
            "person": {"name": "Bob", "age": 25, "birth_date": "1998-12-25"},
            "uuid": "12345678-1234-5678-1234-567812345678",
        }
        assert result == expected


class TestExtendedJSONEncoderRegistration:
    def test_register_custom_type(self):
        """Test registering a custom type handler."""
        ExtendedJSONEncoder.register(CustomType, lambda obj: f"custom:{obj.value}")

        custom_obj = CustomType("test")
        result = json.dumps(custom_obj, cls=ExtendedJSONEncoder)
        assert result == '"custom:test"'

    def test_register_non_callable_raises_error(self):
        """Test that registering non-callable serializer raises TypeError."""
        with pytest.raises(TypeError, match="Serializer must be callable"):
            ExtendedJSONEncoder.register(CustomType, "not_callable")  # type: ignore[arg-type]

    def test_register_builtin_type_raises_error(self):
        """Test that registering built-in JSON types raises ValueError."""
        builtin_types = [str, int, float, bool, list, dict, type(None)]

        for builtin_type in builtin_types:
            with pytest.raises(ValueError, match=f"Cannot override built-in JSON type: {builtin_type.__name__}"):
                ExtendedJSONEncoder.register(builtin_type, lambda obj: obj)

    def test_register_override_existing_handler(self):
        """Test that registering a type overrides existing handler."""
        # Register initial handler
        ExtendedJSONEncoder.register(CustomType, lambda obj: f"first:{obj.value}")

        custom_obj = CustomType("test")
        result1 = json.dumps(custom_obj, cls=ExtendedJSONEncoder)
        assert result1 == '"first:test"'

        # Override with new handler
        ExtendedJSONEncoder.register(CustomType, lambda obj: f"second:{obj.value}")
        result2 = json.dumps(custom_obj, cls=ExtendedJSONEncoder)
        assert result2 == '"second:test"'


class TestJsonDumps:
    def test_basic_usage_without_type_handlers(self):
        """Test json_dumps basic functionality without additional handlers."""
        data = {"date": date(2023, 6, 15), "uuid": UUID("12345678-1234-5678-1234-567812345678")}
        result = json.loads(json_dumps(data))

        expected = {"date": "2023-06-15", "uuid": "12345678-1234-5678-1234-567812345678"}
        assert result == expected

    def test_with_additional_type_handlers(self):
        """Test json_dumps with additional type handlers."""
        custom_obj = CustomType("test_value")
        data = {"custom": custom_obj, "date": date(2023, 6, 15)}

        type_handlers = {CustomType: lambda obj: f"handled:{obj.value}"}
        result = json.loads(json_dumps(data, type_handlers=type_handlers))

        expected = {"custom": "handled:test_value", "date": "2023-06-15"}
        assert result == expected

    def test_type_handlers_override_default(self):
        """Test that type_handlers take precedence over default handlers."""
        data = {"date": date(2023, 6, 15)}

        # Override date handler
        type_handlers = {date: lambda obj: f"custom_date:{obj.isoformat()}"}
        result = json.loads(json_dumps(data, type_handlers=type_handlers))

        expected = {"date": "custom_date:2023-06-15"}
        assert result == expected

    def test_kwargs_passed_to_json_dumps(self):
        """Test that additional kwargs are passed to underlying json.dumps."""
        data = {"name": "test", "value": 42}

        # Test indent parameter
        result = json_dumps(data, indent=2)
        assert "\n" in result  # Formatted JSON should contain newlines

        # Test ensure_ascii parameter
        data_with_unicode = {"message": "hello 世界"}
        result_ascii = json_dumps(data_with_unicode, ensure_ascii=True)
        result_unicode = json_dumps(data_with_unicode, ensure_ascii=False)

        assert "\\u" in result_ascii  # Unicode should be escaped
        assert "世界" in result_unicode  # Unicode should be preserved

    def test_empty_type_handlers(self):
        """Test that empty type_handlers dict works correctly."""
        data = {"date": date(2023, 6, 15)}
        result = json_dumps(data, type_handlers={})
        expected = json_dumps(data)
        assert result == expected

    def test_none_type_handlers(self):
        """Test that None type_handlers works correctly."""
        data = {"date": date(2023, 6, 15)}
        result = json_dumps(data, type_handlers=None)
        expected = json_dumps(data)
        assert result == expected

    def test_complex_nested_structure_with_custom_handlers(self):
        """Test complex nested structure with both default and custom type handlers."""

        @dataclass
        class Address:
            street: str
            city: str

        address = Address("123 Main St", "New York")
        person = Person("Alice", 30, date(1993, 6, 15))
        custom = CustomType("special")

        data = {
            "timestamp": datetime(2023, 6, 15, 14, 30),
            "person": person,
            "address": address,
            "custom": custom,
            "id": UUID("12345678-1234-5678-1234-567812345678"),
            "tags": {"important", "test"},
        }

        type_handlers = {
            CustomType: lambda obj: {"type": "custom", "value": obj.value},
            Address: lambda obj: f"{obj.street}, {obj.city}",
        }

        result = json.loads(json_dumps(data, type_handlers=type_handlers))

        expected = {
            "timestamp": "2023-06-15T14:30:00",
            "person": {"name": "Alice", "age": 30, "birth_date": "1993-06-15"},
            "address": "123 Main St, New York",
            "custom": {"type": "custom", "value": "special"},
            "id": "12345678-1234-5678-1234-567812345678",
            "tags": ["important", "test"],  # Set order may vary
        }

        # Check tags separately due to set ordering
        assert sorted(result["tags"]) == sorted(expected["tags"])
        result_without_tags = {k: v for k, v in result.items() if k != "tags"}
        expected_without_tags = {k: v for k, v in expected.items() if k != "tags"}
        assert result_without_tags == expected_without_tags
