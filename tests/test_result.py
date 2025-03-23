import pytest

from mm_std import Result


def test_ok_result():
    # Create an ok result and verify its properties.
    value = "success"
    result = Result.ok(value, data={"info": "test_ok_result"})
    assert result.is_ok()
    assert not result.is_err()
    assert result.value == value
    assert result.error is None
    assert result.data == {"info": "test_ok_result"}
    # unwrap should return the value without error.
    assert result.unwrap() == value


def test_err_result():
    # Create an error result and verify its properties.
    error_message = "Something went wrong"
    result = Result.err(error_message, data={"info": "test_err_result"})
    assert result.is_err()
    assert not result.is_ok()
    assert result.value is None
    assert error_message in str(result.error)
    assert result.data == {"info": "test_err_result"}
    # unwrap should raise the error.
    with pytest.raises(Exception) as excinfo:
        result.unwrap()
    assert error_message in str(excinfo.value)


def test_unwrap_or():
    default_value = "default"
    ok_result = Result.ok("value")
    err_result = Result.err("error occurred")
    # unwrap_or should return the value when ok.
    assert ok_result.unwrap_or(default_value) == "value"
    # and default when error.
    assert err_result.unwrap_or(default_value) == default_value


def test_map_on_ok():
    # map should transform the value for ok results.
    result = Result.ok(2)
    mapped = result.map(lambda x: x * 3)
    assert mapped.is_ok()
    assert mapped.unwrap() == 6


def test_map_on_err():
    # map should propagate the error for error results.
    error_text = "fail"
    result = Result.err(error_text)
    mapped = result.map(lambda x: x * 3)
    assert mapped.is_err()
    # The original error is retained.
    assert error_text in str(mapped.error)


def test_map_err_on_err():
    # map_err should transform the error.
    error_text = "original error"
    result = Result.err(error_text)
    mapped = result.map_err(lambda err: f"modified: {err}")
    assert mapped.is_err()
    assert "modified:" in str(mapped.error)


def test_map_err_on_ok():
    # map_err should have no effect if result is ok.
    result = Result.ok("ok value")
    mapped = result.map_err(lambda err: f"modified: {err}")
    assert mapped.is_ok()
    assert mapped.unwrap() == "ok value"


def test_and_then_on_ok():
    # and_then should chain a function returning a Result.
    result = Result.ok(5)
    chained = result.and_then(lambda x: Result.ok(x + 10))
    assert chained.is_ok()
    assert chained.unwrap() == 15


def test_and_then_on_err():
    # and_then should propagate error if the original result is an error.
    error_text = "chain error"
    result = Result.err(error_text)
    chained = result.and_then(lambda x: Result.ok(x + 10))
    assert chained.is_err()
    assert error_text in str(chained.error)


def test_or_else_on_err():
    # or_else should allow error handling and recovery.
    error_text = "initial error"
    result = Result.err(error_text)
    recovered = result.or_else(lambda err: Result.ok(f"Recovered from {err}"))
    assert recovered.is_ok()
    assert "Recovered from" in recovered.unwrap()


def test_or_else_on_ok():
    # or_else should not affect a successful result.
    result = Result.ok("good")
    recovered = result.or_else(lambda _err: Result.ok("won't be used"))
    assert recovered.is_ok()
    assert recovered.unwrap() == "good"
