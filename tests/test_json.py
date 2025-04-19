from decimal import Decimal

from pydantic import BaseModel

from mm_std import Result, json_dumps


class Data1(BaseModel):
    name: str
    price: Decimal


class Data2:
    def __init__(self, value: int) -> None:
        self.value = value

    def to_str(self) -> str:
        return f"Data2: value={self.value}"

    def __repr__(self) -> str:
        return f"Data2({self.value})"


def test_json_dumps():
    data = {
        "data1": Data1(name="n1", price=Decimal("123.456")),
        "data2": Result.ok(Data2(value=42), extra={"logs": [1, 2, 3]}),
    }
    output = """{"data1": "name='n1' price=Decimal('123.456')", "data2": "Result(value=Data2(42), extra={'logs': [1, 2, 3]})"}"""
    assert json_dumps(data) == output


def test_json_dumps_with_default():
    data = {"value": Data2(value=42)}
    assert json_dumps(data, default_serializer=lambda o: o.to_str()) == """{"value": "Data2: value=42"}"""
