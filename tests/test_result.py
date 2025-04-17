import pytest
from pydantic import BaseModel

from mm_std import Result

pytestmark = pytest.mark.anyio


def test_success_result():
    result = Result.success(42)
    assert result.is_ok() is True
    assert result.is_error() is False
    assert result.unwrap() == 42
    assert result.unwrap_or(0) == 42
    assert result.to_dict() == {"ok": 42, "error": None, "exception": None, "extra": None}


def test_failure_result():
    result = Result.failure("something went wrong")
    assert result.is_ok() is False
    assert result.is_error() is True
    assert result.unwrap_or(123) == 123
    assert result.unwrap_error() == "something went wrong"
    with pytest.raises(RuntimeError):
        result.unwrap()


def test_failure_with_exception():
    exc = ValueError("boom")
    result = Result.failure(exc)
    assert result.is_exception() is True
    assert result.unwrap_exception() == exc
    assert result.to_dict()["exception"] == str(exc)
    with pytest.raises(RuntimeError):
        result.unwrap()


def test_map_success():
    result = Result.success(10)
    mapped = result.map(lambda x: x * 2)
    assert mapped.is_ok()
    assert mapped.unwrap() == 20


def test_map_failure():
    result = Result.failure("fail")
    mapped = result.map(lambda x: x * 2)
    assert mapped.is_error()
    assert mapped.unwrap_error() == "fail"


def test_map_exception():
    def fail_fn(_: int) -> int:
        raise RuntimeError("fail in map")

    result = Result.success(10)
    mapped = result.map(fail_fn)
    assert mapped.is_error()
    assert mapped.is_exception()
    assert isinstance(mapped.unwrap_exception(), RuntimeError)


async def test_map_async_success():
    async def async_double(x: int) -> int:
        return x * 2

    result = Result.success(5)
    new_result = await result.map_async(async_double)
    assert new_result.is_ok()
    assert new_result.unwrap() == 10


def test_and_then_success():
    def add_one(x: int) -> Result[int]:
        return Result.success(x + 1)

    result = Result.success(1).and_then(add_one).and_then(add_one)
    assert result.is_ok()
    assert result.unwrap() == 3


def test_and_then_failure():
    def fail(_: int) -> Result[int]:
        return Result.failure("fail in chain")

    result = Result.success(1).and_then(fail)
    assert result.is_error()
    assert result.unwrap_error() == "fail in chain"


async def test_and_then_async_success():
    async def plus_one(x: int) -> Result[int]:
        return Result.success(x + 1)

    result = Result.success(2)
    result = await result.and_then_async(plus_one)
    result = await result.and_then_async(plus_one)
    assert result.is_ok()
    assert result.unwrap() == 4


def test_equality_and_hash():
    r1 = Result.success(123, extra={"meta": "info"})
    r2 = Result.success(123, extra={"meta": "info"})
    assert r1 == r2
    assert hash(r1) == hash(r2)


def test_repr_output():
    r = Result.success(5, extra={"foo": "bar"})
    repr_str = repr(r)
    assert "ok=5" in repr_str
    assert "extra={'foo': 'bar'}" in repr_str


def test_result_with_pydantic_model_dump():
    class Wrapper(BaseModel):
        result: Result[int]

    wrapper = Wrapper(result=Result.success(123, extra={"info": "test"}))
    dumped = wrapper.model_dump()
    assert dumped == {
        "result": {
            "ok": 123,
            "error": None,
            "exception": None,
            "extra": {"info": "test"},
        }
    }
