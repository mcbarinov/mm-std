from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Generic, TypeVar, cast

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

T = TypeVar("T")
U = TypeVar("U")


class DataResult(Generic[T]):
    """
    A result wrapper that encapsulates either a successful result (`ok`) or an error message (`err`).
    Optionally carries auxiliary `data` field regardless of success or failure.
    """

    def __init__(
        self,
        ok: T | None = None,
        err: str | None = None,
        data: object = None,
        ok_is_none: bool = False,  # Allow None as a valid success value
    ) -> None:
        # Sanity check: at least one of ok or err must be provided, unless explicitly allowed via `ok_is_none`
        if ok is None and err is None and not ok_is_none:
            raise ValueError("Either ok or err must be set")
        # You can't set both ok and err unless ok_is_none is True (used to explicitly accept None as success)
        if (ok_is_none or ok is not None) and err is not None:
            raise ValueError("Cannot set both ok and err")

        self.ok = ok
        self.err = err
        self.data = data

    def is_ok(self) -> bool:
        """
        Returns True if the result represents a success.
        """
        return self.err is None

    def is_err(self) -> bool:
        """
        Returns True if the result represents an error.
        """
        return self.err is not None

    def unwrap(self) -> T:
        """
        Returns the successful value or raises an exception if this is an error result.
        """
        if self.is_err():
            raise RuntimeError(f"Called `unwrap()` on an `Err` value: {self.err!r}")
        return cast(T, self.ok)

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
            return cast(T, self.ok)
        return default

    def unwrap_err(self) -> str:
        """
        Returns the error message or raises an exception if this is a success result.
        """
        if self.is_ok():
            raise RuntimeError(f"Called `unwrap_err()` on an `Ok` value: {self.ok!r}")
        return cast(str, self.err)

    def dict(self) -> dict[str, object]:
        """
        Returns a dictionary representation of the result.
        """
        return {"ok": self.ok, "err": self.err, "data": self.data}

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
            return DataResult[U](err=self.err, data=self.data)

        try:
            mapped_ok = fn(self.unwrap())
            return DataResult[U](ok=mapped_ok, data=self.data)
        except Exception as e:
            return DataResult[U](err=f"Error in map: {e!s}", data={"original_data": self.data, "original_ok": self.ok})

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
            return DataResult[U](err=self.err, data=self.data)

        try:
            mapped_ok = await fn(self.unwrap())
            return DataResult[U](ok=mapped_ok, data=self.data)
        except Exception as e:
            return DataResult[U](err=f"Error in map_async: {e!s}", data={"original_data": self.data, "original_ok": self.ok})

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
            return DataResult[U](err=self.err, data=self.data)

        try:
            return fn(self.unwrap())
        except Exception as e:
            return DataResult[U](err=f"Error in and_then: {e!s}", data={"original_data": self.data, "original_ok": self.ok})

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
            return DataResult[U](err=self.err, data=self.data)

        try:
            return await fn(self.unwrap())
        except Exception as e:
            return DataResult[U](err=f"Error in and_then_async: {e!s}", data={"original_data": self.data, "original_ok": self.ok})

    def __repr__(self) -> str:
        """
        Returns the debug representation of the result.
        """
        result = f"DataResult(ok={self.ok!r}" if self.is_ok() else f"DataResult(err={self.err!r}"
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
        return self.ok == other.ok and self.err == other.err and self.data == other.data

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
            return cls(
                ok=v.get("ok"),
                err=v.get("err"),
                data=v.get("data"),
            )
        raise TypeError(f"Cannot parse value as {cls.__name__}: {v}")
