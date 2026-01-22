"""Tests for json_utils module."""

import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from uuid import UUID

import pydantic
import pytest

from mm_std import ExtendedJSONEncoder, json_dumps


class TestExtendedJSONEncoderBuiltinTypes:
    """Tests for built-in Python type serialization."""

    def test_datetime(self) -> None:
        """Serializes datetime to isoformat string."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        result = json.dumps(dt, cls=ExtendedJSONEncoder)
        assert result == '"2024-01-15T10:30:45"'

    def test_date(self) -> None:
        """Serializes date to isoformat string."""
        d = date(2024, 1, 15)
        result = json.dumps(d, cls=ExtendedJSONEncoder)
        assert result == '"2024-01-15"'

    def test_uuid(self) -> None:
        """UUID is serialized to string."""
        uuid = UUID("12345678-1234-5678-1234-567812345678")
        result = json.dumps(uuid, cls=ExtendedJSONEncoder)
        assert result == '"12345678-1234-5678-1234-567812345678"'

    def test_decimal(self) -> None:
        """Decimal is serialized to string."""
        dec = Decimal("123.45")
        result = json.dumps(dec, cls=ExtendedJSONEncoder)
        assert result == '"123.45"'

    def test_path(self) -> None:
        """Path is serialized to string."""
        path = Path("/home/user/file.txt")
        result = json.dumps(path, cls=ExtendedJSONEncoder)
        assert result == '"/home/user/file.txt"'

    def test_set(self) -> None:
        """Serializes set to list."""
        s = {1}
        result = json.dumps(s, cls=ExtendedJSONEncoder)
        assert json.loads(result) == [1]

    def test_frozenset(self) -> None:
        """Serializes frozenset to list."""
        fs = frozenset([1])
        result = json.dumps(fs, cls=ExtendedJSONEncoder)
        assert json.loads(result) == [1]

    def test_bytes(self) -> None:
        """Decodes bytes as latin-1 string."""
        b = b"hello"
        result = json.dumps(b, cls=ExtendedJSONEncoder)
        assert result == '"hello"'

    def test_bytes_with_high_bytes(self) -> None:
        """High byte values (>127) are decoded correctly via latin-1."""
        b = bytes([0xFF, 0x80])
        result = json.dumps(b, cls=ExtendedJSONEncoder)
        decoded = json.loads(result)
        assert decoded == "\xff\x80"

    def test_complex(self) -> None:
        """Serializes complex to dict with real and imag keys."""
        c = complex(3.5, -2.1)
        result = json.dumps(c, cls=ExtendedJSONEncoder)
        data = json.loads(result)
        assert data == {"real": 3.5, "imag": -2.1}

    def test_enum(self) -> None:
        """Enum is serialized to its value."""

        class Status(Enum):
            ACTIVE = "active"
            INACTIVE = "inactive"

        result = json.dumps(Status.ACTIVE, cls=ExtendedJSONEncoder)
        assert result == '"active"'

    def test_enum_int_value(self) -> None:
        """Enum with int value is serialized to that int."""

        class Priority(Enum):
            LOW = 1
            HIGH = 10

        result = json.dumps(Priority.HIGH, cls=ExtendedJSONEncoder)
        assert result == "10"

    def test_exception(self) -> None:
        """Exception is serialized to its string representation."""
        exc = ValueError("something went wrong")
        result = json.dumps(exc, cls=ExtendedJSONEncoder)
        assert result == '"something went wrong"'


class TestExtendedJSONEncoderDataclass:
    """Tests for dataclass serialization."""

    def test_simple_dataclass(self) -> None:
        """Dataclass is serialized via asdict."""

        @dataclass
        class User:
            name: str
            age: int

        user = User(name="Alice", age=30)
        result = json.dumps(user, cls=ExtendedJSONEncoder)
        data = json.loads(result)
        assert data == {"name": "Alice", "age": 30}

    def test_nested_dataclass(self) -> None:
        """Nested dataclasses are serialized recursively."""

        @dataclass
        class Address:
            city: str

        @dataclass
        class Person:
            name: str
            address: Address

        person = Person(name="Bob", address=Address(city="NYC"))
        result = json.dumps(person, cls=ExtendedJSONEncoder)
        data = json.loads(result)
        assert data == {"name": "Bob", "address": {"city": "NYC"}}

    def test_dataclass_with_special_types(self) -> None:
        """Dataclass with special types like UUID and datetime."""

        @dataclass
        class Event:
            id: UUID
            timestamp: datetime

        event = Event(id=UUID("12345678-1234-5678-1234-567812345678"), timestamp=datetime(2024, 1, 15, 10, 30))
        result = json.dumps(event, cls=ExtendedJSONEncoder)
        data = json.loads(result)
        assert data == {"id": "12345678-1234-5678-1234-567812345678", "timestamp": "2024-01-15T10:30:00"}


class TestExtendedJSONEncoderPydantic:
    """Tests for pydantic model serialization."""

    def test_pydantic_model(self) -> None:
        """Pydantic BaseModel is serialized via model_dump."""

        class Item(pydantic.BaseModel):
            name: str
            price: float

        item = Item(name="Widget", price=9.99)
        result = json.dumps(item, cls=ExtendedJSONEncoder)
        data = json.loads(result)
        assert data == {"name": "Widget", "price": 9.99}


class TestExtendedJSONEncoderRegister:
    """Tests for custom type registration."""

    def test_register_custom_type(self) -> None:
        """Custom types can be registered with handlers."""

        class CustomId:
            def __init__(self, value: int) -> None:
                self.value = value

        ExtendedJSONEncoder.register(CustomId, lambda obj: f"id-{obj.value}")

        cid = CustomId(42)
        result = json.dumps(cid, cls=ExtendedJSONEncoder)
        assert result == '"id-42"'

    @pytest.mark.parametrize(
        "builtin_type",
        [str, int, float, bool, list, dict, type(None)],
        ids=["str", "int", "float", "bool", "list", "dict", "NoneType"],
    )
    def test_register_builtin_raises_value_error(self, builtin_type: type) -> None:
        """Registering built-in JSON types raises ValueError."""
        with pytest.raises(ValueError, match="Cannot override built-in JSON type"):
            ExtendedJSONEncoder.register(builtin_type, str)


class TestJsonDumps:
    """Tests for json_dumps function."""

    def test_basic_serialization(self) -> None:
        """Basic types are serialized correctly."""
        data = {"name": "test", "value": 42}
        result = json_dumps(data)
        assert json.loads(result) == data

    def test_extended_types(self) -> None:
        """Extended types are serialized correctly."""
        data = {"id": UUID("12345678-1234-5678-1234-567812345678"), "amount": Decimal("99.99")}
        result = json_dumps(data)
        parsed = json.loads(result)
        assert parsed == {"id": "12345678-1234-5678-1234-567812345678", "amount": "99.99"}

    def test_type_handlers_override(self) -> None:
        """Custom type_handlers override default behavior."""
        data = {"amount": Decimal("99.99")}
        result = json_dumps(data, type_handlers={Decimal: float})
        parsed = json.loads(result)
        assert parsed == {"amount": 99.99}
        assert isinstance(parsed["amount"], float)

    def test_kwargs_passed_to_json_dumps(self) -> None:
        """Additional kwargs are passed to json.dumps."""
        data = {"b": 2, "a": 1}
        result = json_dumps(data, sort_keys=True)
        assert result == '{"a": 1, "b": 2}'

    def test_kwargs_indent(self) -> None:
        """The indent kwarg works correctly."""
        data = {"key": "value"}
        result = json_dumps(data, indent=2)
        assert result == '{\n  "key": "value"\n}'
