import pytest

from mm_std.data_result import DataResult


def test_ok_creation():
    result = DataResult.ok("success")
    assert result.is_ok()
    assert not result.is_err()
    assert result.unwrap() == "success"
    assert result._ok == "success"  # noqa: SLF001
    assert result._err is None  # noqa: SLF001
    assert result.data is None


def test_ok_with_data():
    data = {"meta": "info"}
    result = DataResult.ok("success", data)
    assert result.is_ok()
    assert result.unwrap() == "success"
    assert result.data == data


def test_err_creation():
    result = DataResult.err("failed")
    assert result.is_err()
    assert not result.is_ok()
    assert result.unwrap_err() == "failed"
    assert result._ok is None  # noqa: SLF001
    assert result._err == "failed"  # noqa: SLF001


def test_err_with_data():
    data = {"debug": "info"}
    result = DataResult.err("failed", data)
    assert result.is_err()
    assert result.unwrap_err() == "failed"
    assert result.data == data


def test_exception():
    error = ValueError("something went wrong")
    result = DataResult.exception(error)
    assert result.is_err()
    assert result.unwrap_err() == "exception"
    assert "exception_message" in result.data
    assert result.data["exception_message"] == "something went wrong"


def test_unwrap():
    result = DataResult.ok(42)
    assert result.unwrap() == 42

    error_result = DataResult.err("error")
    with pytest.raises(RuntimeError, match="Called `unwrap\\(\\)` on an `Err` value"):
        error_result.unwrap()


def test_unwrap_err():
    result = DataResult.err("error message")
    assert result.unwrap_err() == "error message"

    ok_result = DataResult.ok(42)
    with pytest.raises(RuntimeError, match="Called `unwrap_err\\(\\)` on an `Ok` value"):
        ok_result.unwrap_err()


def test_unwrap_ok_or():
    result = DataResult.ok(42)
    assert result.unwrap_ok_or(0) == 42

    error_result = DataResult.err("error")
    assert error_result.unwrap_ok_or(0) == 0


def test_dict():
    result = DataResult.ok(42, {"extra": "data"})
    assert result.dict() == {"ok": 42, "err": None, "data": {"extra": "data"}}

    error_result = DataResult.err("failed", {"debug": "info"})
    assert error_result.dict() == {"ok": None, "err": "failed", "data": {"debug": "info"}}


def test_map():
    result = DataResult.ok(5)
    mapped = result.map(lambda x: x * 2)
    assert mapped.is_ok()
    assert mapped.unwrap() == 10

    error_result = DataResult.err("error")
    mapped_error = error_result.map(lambda x: x * 2)
    assert mapped_error.is_err()
    assert mapped_error.unwrap_err() == "error"

    # Test exception in mapping function
    def failing_map(_):
        raise ValueError("map failed")

    result_with_exception = result.map(failing_map)
    assert result_with_exception.is_err()
    assert result_with_exception.unwrap_err() == "exception"


@pytest.mark.anyio
async def test_map_async():
    result = DataResult.ok(5)

    async def double(x):
        return x * 2

    mapped = await result.map_async(double)
    assert mapped.is_ok()
    assert mapped.unwrap() == 10

    error_result = DataResult.err("error")
    mapped_error = await error_result.map_async(double)
    assert mapped_error.is_err()

    # Test exception in async mapping function
    async def failing_map(_):
        raise ValueError("map failed")

    result_with_exception = await result.map_async(failing_map)
    assert result_with_exception.is_err()


def test_and_then():
    result = DataResult.ok(5)
    chained = result.and_then(lambda x: DataResult.ok(x * 2))
    assert chained.is_ok()
    assert chained.unwrap() == 10

    error_result = DataResult.err("error")
    chained_error = error_result.and_then(lambda x: DataResult.ok(x * 2))
    assert chained_error.is_err()

    # Should pass through errors from the function
    def failing_chain(_):
        return DataResult.err("chaining failed")

    result_with_error = result.and_then(failing_chain)
    assert result_with_error.is_err()
    assert result_with_error.unwrap_err() == "chaining failed"


@pytest.mark.anyio
async def test_and_then_async():
    result = DataResult.ok(5)

    async def double_ok(x):
        return DataResult.ok(x * 2)

    chained = await result.and_then_async(double_ok)
    assert chained.is_ok()
    assert chained.unwrap() == 10

    error_result = DataResult.err("error")
    chained_error = await error_result.and_then_async(double_ok)
    assert chained_error.is_err()


def test_equality():
    result1 = DataResult.ok(42)
    result2 = DataResult.ok(42)
    result3 = DataResult.ok(43)
    error1 = DataResult.err("error")
    error2 = DataResult.err("error")

    assert result1 == result2
    assert result1 != result3
    assert error1 == error2
    assert result1 != error1

    # Test with data
    result_with_data1 = DataResult.ok(42, {"meta": "info"})
    result_with_data2 = DataResult.ok(42, {"meta": "info"})
    result_with_diff_data = DataResult.ok(42, {"meta": "different"})

    assert result_with_data1 == result_with_data2
    assert result_with_data1 != result_with_diff_data


def test_hash():
    result = DataResult.ok(42)
    error = DataResult.err("error")

    # These should not raise exceptions
    hash(result)
    hash(error)

    # Test hash can be used in dictionaries
    result_dict = {result: "success", error: "failure"}
    assert len(result_dict) == 2


def test_repr():
    result = DataResult.ok(42)
    error = DataResult.err("failed")
    result_with_data = DataResult.ok(42, {"extra": "data"})

    assert repr(result) == "DataResult(ok=42)"
    assert repr(error) == "DataResult(err='failed')"
    assert "DataResult(ok=42, data=" in repr(result_with_data)


def test_direct_instantiation():
    with pytest.raises(RuntimeError, match="DataResult is not intended to be instantiated directly"):
        DataResult()
