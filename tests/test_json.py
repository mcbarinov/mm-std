from decimal import Decimal

from pydantic import BaseModel

from mm_std import json_dumps


class Data1(BaseModel):
    name: str
    price: Decimal


class Data2:
    def __init__(self, value: int) -> None:
        self.value = value

    def to_str(self) -> str:
        return f"Data2: value={self.value}"


def test_json_dumps():
    data = Data1(name="n1", price=Decimal("123.456"))
    assert json_dumps(data) == """{"name": "n1", "price": "123.456"}"""


def test_json_dumps_with_default():
    data = {"value": Data2(value=42)}
    assert json_dumps(data, default=lambda o: o.to_str()) == """{"value": "Data2: value=42"}"""
