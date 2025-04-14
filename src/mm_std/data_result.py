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

        Args:
            fn: A function that transforms the success value from type T to type U.

        Returns:
            A new DataResult with the transformed success value or the original error.
        """
        if self.is_err():
            return DataResult[U](err=self.err, data=self.data)

        mapped_ok = fn(self.unwrap())
        return DataResult[U](ok=mapped_ok, data=self.data)

    async def map_async(self, fn: Callable[[T], Awaitable[U]]) -> DataResult[U]:
        """
        Asynchronously transforms the success value using the provided async function if this is a success result.
        If this is an error result, returns a new error result with the same error message.

        Args:
            fn: An async function that transforms the success value from type T to type U.

        Returns:
            A new DataResult with the transformed success value or the original error.
        """
        if self.is_err():
            return DataResult[U](err=self.err, data=self.data)

        mapped_ok = await fn(self.unwrap())
        return DataResult[U](ok=mapped_ok, data=self.data)

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
