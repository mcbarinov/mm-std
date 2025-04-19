import pytest

from mm_std import Result


# Test static constructors, is_ok/is_err and basic attributes
def test_ok_and_err_creation():
    r = Result.ok(123)
    assert r.is_ok()
    assert not r.is_err()
    assert not r.is_exception()
    assert r.value == 123
    assert r.error is None
    assert r.extra is None

    e = Result.err("error occurred")
    assert e.is_err()
    assert not e.is_ok()
    assert e.error == "error occurred"
    assert e.value is None
    assert e.extra is None


# Test unwrap and unwrap_error
def test_unwrap_and_unwrap_error():
    r = Result.ok("value")
    assert r.unwrap() == "value"
    with pytest.raises(RuntimeError):
        Result.err("err").unwrap()

    e = Result.err("err")
    assert e.unwrap_error() == "err"
    with pytest.raises(RuntimeError):
        r.unwrap_error()


# Test unwrap_or
def test_unwrap_or():
    r = Result.ok(5)
    assert r.unwrap_or(10) == 5
    assert Result.err("e").unwrap_or(10) == 10


# Test unwrap_exception
def test_unwrap_exception():
    exc = ValueError("bad")
    r = Result.err(exc)
    # error message stored as "exception"
    assert isinstance(r.unwrap_exception(), ValueError)
    with pytest.raises(RuntimeError):
        Result.ok(1).unwrap_exception()


# Test ok_or_error
def test_ok_or_error():
    assert Result.ok("v").ok_or_error() == "v"
    assert Result.err("err").ok_or_error() == "err"


# Test to_dict
def test_to_dict():
    exc = ValueError("bad")
    r = Result.err(("msg", exc), extra={"key": "val"})
    d = r.to_dict()
    assert d == {
        "value": None,
        "error": "msg",
        "exception": str(exc),
        "extra": {"key": "val"},
    }


# Test with_value and with_error
def test_with_value_and_with_error():
    r = Result.ok(1, extra={"a": 1})
    r2 = r.with_value("new")
    assert r2.is_ok()
    assert r2.value == "new"
    assert r2.extra == {"a": 1}

    r_err = r2.with_error("oops")
    assert r_err.is_err()
    assert r_err.error == "oops"
    assert r_err.extra == {"a": 1}


# Test synchronous map
def test_map_success_and_failure():
    r = Result.ok(2)
    r2 = r.map(lambda x: x * 2)
    assert r2.is_ok() and r2.value == 4

    def bad(_x):
        raise ValueError("fail")

    r3 = r.map(bad)
    assert r3.is_err() and r3.error == "map_exception"

    e = Result.err("err")
    assert e.map(lambda x: x).is_err()


# Test asynchronous map_async
async def test_map_async_success_and_failure():
    async def add1(x: int) -> int:
        return x + 1

    r = Result.ok(3)
    r2 = await r.map_async(add1)
    assert r2.is_ok() and r2.value == 4

    async def bad_async(_x: int) -> int:
        raise RuntimeError("async fail")

    r3 = await r.map_async(bad_async)
    assert r3.is_err() and r3.error == "map_exception"

    assert await Result.err("err").map_async(add1) == Result.err("err")


# Test synchronous and_then
def test_and_then_success_and_failure():
    def next_fn(x: int) -> Result[int]:
        return Result.ok(x * 3)

    r = Result.ok(2)
    r2 = r.and_then(next_fn)
    assert r2.is_ok() and r2.value == 6

    def bad_then(_x: int) -> Result[int]:
        raise KeyError("bad")

    r3 = r.and_then(bad_then)
    assert r3.is_err() and r3.error == "and_then_exception"

    assert Result.err("err").and_then(next_fn).is_err()


# Test asynchronous and_then_async
async def test_and_then_async_success_and_failure():
    async def next_async(x: int) -> Result[int]:
        return Result.ok(x + 5)

    r = Result.ok(4)
    r2 = await r.and_then_async(next_async)
    assert r2.is_ok() and r2.value == 9

    async def bad_then_async(_x: int) -> Result[int]:
        raise IndexError("bad")

    r3 = await r.and_then_async(bad_then_async)
    assert r3.is_err() and r3.error == "and_then_exception"

    assert await Result.err("err").and_then_async(next_async) == Result.err("err")


# Test __repr__, equality and hashing
def test_repr_and_equality_and_hash():
    r1 = Result.ok(10, extra={"x": 1})
    r2 = Result.ok(10, extra={"x": 1})
    # repr should contain class name
    assert repr(r1).startswith("Result(")
    # equality
    assert r1 == r2
    # hashing: identical objects should collapse in a set
    s = {r1, r2}
    assert len(s) == 1


# Test Pydantic integration (V2)
def test_pydantic_validation_and_serialization():
    from pydantic import BaseModel

    class M(BaseModel):
        res: Result[int]

    # Validation from dict
    m = M(res={"value": 7, "error": None, "exception": None, "extra": {"data": 1}})
    assert isinstance(m.res, Result)
    assert m.res.value == 7
    assert m.res.extra == {"data": 1}

    # Serialization back to dict
    dumped = m.model_dump()
    assert dumped["res"] == {
        "value": 7,
        "error": None,
        "exception": None,
        "extra": {"data": 1},
    }
