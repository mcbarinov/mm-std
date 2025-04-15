from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Generic, TypeVar, cast

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

T = TypeVar("T")
U = TypeVar("U")


type Data = dict[str, object] | None


class DataResult(Generic[T]):
    """
    A result wrapper that encapsulates either a successful result (`ok`) or an error message (`err`).
    Optionally carries `data` field regardless of success or failure.
    """

    _ok: T | None
    _err: str | None
    data: Data | None

    def __init__(self) -> None:
        raise RuntimeError("DataResult is not intended to be instantiated directly. Use the static methods instead.")

    def is_ok(self) -> bool:
        """
        Returns True if the result represents a success.
        """
        return self._err is None

    def is_err(self) -> bool:
        """
        Returns True if the result represents an error.
        """
        return self._err is not None

    def unwrap(self) -> T:
        """
        Returns the successful value or raises an exception if this is an error result.
        """
        if self.is_err():
            raise RuntimeError(f"Called `unwrap()` on an `Err` value: {self.err!r}")
        return cast(T, self._ok)

    def unwrap_ok_or(self, default: T) -> T:
        """
        Returns the contained success value if this is a success result,
        or returns the provided default value if this is an error result.

        Args:
            default: The value to return if this is an error result.

        Returns:
            The success value or the default value.
        """
        if self.is_ok():
            return cast(T, self._ok)
        return default

    def unwrap_err(self) -> str:
        """
        Returns the error message or raises an exception if this is a success result.
        """
        if self.is_ok():
            raise RuntimeError(f"Called `unwrap_err()` on an `Ok` value: {self.ok!r}")
        return cast(str, self._err)

    def dict(self) -> dict[str, object]:
        """
        Returns a dictionary representation of the result.
        """
        return {"ok": self._ok, "err": self._err, "data": self.data}

    def map(self, fn: Callable[[T], U]) -> DataResult[U]:
        """
        Transforms the success value using the provided function if this is a success result.
        If this is an error result, returns a new error result with the same error message.
        If the function raises an exception, returns a new error result with the exception message.

        Args:
            fn: A function that transforms the success value from type T to type U.

        Returns:
            A new DataResult with the transformed success value or an error.
        """
        if self.is_err():
            return DataResult[U].err(self.unwrap_err(), self.data)

        try:
            mapped_ok = fn(self.unwrap())
            return DataResult[U].ok(mapped_ok, self.data)
        except Exception as e:
            return DataResult[U].exception(e, data={"original_data": self.data, "original_ok": self.ok})

    async def map_async(self, fn: Callable[[T], Awaitable[U]]) -> DataResult[U]:
        """
        Asynchronously transforms the success value using the provided async function if this is a success result.
        If this is an error result, returns a new error result with the same error message.
        If the function raises an exception, returns a new error result with the exception message.

        Args:
            fn: An async function that transforms the success value from type T to type U.

        Returns:
            A new DataResult with the transformed success value or an error.
        """
        if self.is_err():
            return DataResult[U].err(self.unwrap_err(), self.data)

        try:
            mapped_ok = await fn(self.unwrap())
            return DataResult[U].ok(mapped_ok, self.data)
        except Exception as e:
            return DataResult[U].exception(e, data={"original_data": self.data, "original_ok": self.ok})

    def and_then(self, fn: Callable[[T], DataResult[U]]) -> DataResult[U]:
        """
        Applies the function to the success value if this is a success result.
        If this is an error result, returns a new error result with the same error message.

        Unlike map, the function must return a DataResult.

        Args:
            fn: A function that takes the success value and returns a new DataResult.

        Returns:
            The result of the function application or the original error.
        """
        if self.is_err():
            return DataResult[U].err(self.unwrap_err(), self.data)

        try:
            return fn(self.unwrap())
        except Exception as e:
            return DataResult[U].exception(e, data={"original_data": self.data, "original_ok": self.ok})

    async def and_then_async(self, fn: Callable[[T], Awaitable[DataResult[U]]]) -> DataResult[U]:
        """
        Asynchronously applies the function to the success value if this is a success result.
        If this is an error result, returns a new error result with the same error message.

        Unlike map_async, the function must return a DataResult.

        Args:
            fn: An async function that takes the success value and returns a new DataResult.

        Returns:
            The result of the function application or the original error.
        """
        if self.is_err():
            return DataResult[U].err(self.unwrap_err(), self.data)

        try:
            return await fn(self.unwrap())
        except Exception as e:
            return DataResult[U].exception(e, {"original_data": self.data, "original_ok": self.ok})

    def __repr__(self) -> str:
        """
        Returns the debug representation of the result.
        """
        result = f"DataResult(ok={self._ok!r}" if self.is_ok() else f"DataResult(err={self._err!r}"
        if self.data is not None:
            result += f", data={self.data!r}"
        return result + ")"

    def __hash__(self) -> int:
        """
        Enables hashing for use in sets and dict keys.
        """
        return hash((self.ok, self.err, self.data))

    def __eq__(self, other: object) -> bool:
        """
        Compares two DataResult instances by value.
        """
        if not isinstance(other, DataResult):
            return NotImplemented
        return self._ok == other._ok and self._err == other._err and self.data == other.data

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: type[Any], _handler: GetCoreSchemaHandler) -> CoreSchema:
        """
        Custom Pydantic v2 integration method for schema generation and validation.
        """
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.any_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: x.dict()),
        )

    @classmethod
    def _validate(cls, v: object) -> DataResult[T]:
        """
        Internal validation logic for Pydantic.
        Accepts either an instance of DataResult or a dict-like input.
        """
        if isinstance(v, cls):
            return v
        if isinstance(v, dict):
            return cls._create(
                ok=v.get("ok"),
                err=v.get("err"),
                data=v.get("data"),
            )
        raise TypeError(f"Cannot parse value as {cls.__name__}: {v}")

    @classmethod
    def _create(cls, ok: T | None, err: str | None, data: Data) -> DataResult[T]:
        """
        Internal method to create a DataResult instance.
        """
        obj = object.__new__(cls)
        obj._ok = ok  # noqa: SLF001
        obj._err = err  # noqa: SLF001
        obj.data = data
        return obj

    @staticmethod
    def ok(value: T, data: Data = None) -> DataResult[T]:
        """
        Static method to create a successful DataResult.
        """
        return DataResult._create(ok=value, err=None, data=data)

    @staticmethod
    def err(error: str, data: Data = None) -> DataResult[T]:
        """
        Static method to create an error DataResult.
        """
        return DataResult._create(ok=None, err=error, data=data)

    @staticmethod
    def exception(err: Exception, data: Data = None) -> DataResult[T]:
        """
        Static method to create an error DataResult from an exception.
        """
        if data is None:
            data = {}
        key = "exception_message"
        while key in data:
            key += "_"
        data[key] = str(err)

        return DataResult._create(ok=None, err="exception", data=data)
