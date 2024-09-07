from decimal import Decimal

from pydantic import BaseModel

from mm_std import json_dumps


def test_json_dumps():
    class Data(BaseModel):
        name: str
        price: Decimal

    data = Data(name="n1", price=Decimal("123.456"))
    assert json_dumps(data) == """{"name": "n1", "price": "123.456"}"""
