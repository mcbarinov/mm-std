import pytest

from mm_std import DataResult


class TestDataResult:
    def test_init_with_ok(self):
        result = DataResult(ok="success")
        assert result.ok == "success"
        assert result.err is None
        assert result.data is None

    def test_init_with_err(self):
        result = DataResult(err="error")
        assert result.ok is None
        assert result.err == "error"
        assert result.data is None

    def test_init_with_data(self):
        data = {"key": "value"}
        result = DataResult(ok="success", data=data)
        assert result.ok == "success"
        assert result.data == data

    def test_init_with_none_ok(self):
        # None is not valid as a success value by default
        with pytest.raises(ValueError):
            DataResult()

        # But can be explicitly allowed
        result = DataResult(ok_is_none=True)
        assert result.ok is None
        assert result.err is None
        assert result.is_ok()

    def test_init_both_ok_and_err(self):
        with pytest.raises(ValueError):
            DataResult(ok="success", err="error")

    def test_is_ok(self):
        assert DataResult(ok="success").is_ok() is True
        assert DataResult(err="error").is_ok() is False

    def test_is_err(self):
        assert DataResult(ok="success").is_err() is False
        assert DataResult(err="error").is_err() is True

    def test_unwrap_success(self):
        result = DataResult(ok="success")
        assert result.unwrap() == "success"

    def test_unwrap_error(self):
        result = DataResult(err="error")
        with pytest.raises(RuntimeError):
            result.unwrap()

    def test_unwrap_err_success(self):
        result = DataResult(ok="success")
        with pytest.raises(RuntimeError):
            result.unwrap_err()

    def test_unwrap_err_error(self):
        result = DataResult(err="error")
        assert result.unwrap_err() == "error"

    def test_unwrap_ok_or(self):
        assert DataResult(ok="success").unwrap_ok_or("default") == "success"
        assert DataResult(err="error").unwrap_ok_or("default") == "default"

    def test_dict(self):
        result = DataResult(ok="success", data={"meta": "data"})
        expected = {"ok": "success", "err": None, "data": {"meta": "data"}}
        assert result.dict() == expected

    def test_map_success(self):
        result = DataResult(ok=5)
        mapped = result.map(lambda x: x * 2)
        assert mapped.ok == 10
        assert mapped.is_ok()

    def test_map_error(self):
        result = DataResult(err="error", data={"context": True})
        mapped = result.map(lambda x: x * 2)
        assert mapped.err == "error"
        assert mapped.data == {"context": True}
        assert mapped.is_err()

    @pytest.mark.anyio
    async def test_map_async_success(self):
        result = DataResult(ok=5)

        async def double(x):
            return x * 2

        mapped = await result.map_async(double)
        assert mapped.ok == 10
        assert mapped.is_ok()

    @pytest.mark.anyio
    async def test_map_async_error(self):
        result = DataResult(err="error")

        async def double(x):
            return x * 2

        mapped = await result.map_async(double)
        assert mapped.err == "error"
        assert mapped.is_err()

    def test_repr(self):
        assert repr(DataResult(ok="success")) == "DataResult(ok='success')"
        assert repr(DataResult(err="error")) == "DataResult(err='error')"
        assert repr(DataResult(ok="val", data=1)) == "DataResult(ok='val', data=1)"

    def test_hash(self):
        r1 = DataResult(ok="success")
        r2 = DataResult(ok="success")
        r3 = DataResult(ok="different")

        assert hash(r1) == hash(r2)
        assert hash(r1) != hash(r3)

        # Can be used as dict keys
        d = {r1: "value"}
        assert d[r2] == "value"

    def test_eq(self):
        assert DataResult(ok="success") == DataResult(ok="success")
        assert DataResult(err="error") == DataResult(err="error")
        assert DataResult(ok="success") != DataResult(ok="different")
        assert DataResult(ok="success") != DataResult(err="error")

    def test_pydantic_validation(self):
        # Test validation of existing instances
        original = DataResult(ok="success")
        validated = DataResult._validate(original)  # noqa: SLF001
        assert validated is original

        # Test validation of dictionaries
        dict_input = {"ok": "from_dict", "data": {"extra": "info"}}
        result = DataResult._validate(dict_input)  # noqa: SLF001
        assert result.ok == "from_dict"
        assert result.data == {"extra": "info"}

        # Test validation of invalid inputs
        with pytest.raises(TypeError):
            DataResult._validate("not_valid")  # noqa: SLF001
