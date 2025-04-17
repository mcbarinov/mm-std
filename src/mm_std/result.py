from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, cast

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

T = TypeVar("T")
U = TypeVar("U")

type Extra = dict[str, Any] | None


class Result[T]:
    """
    A container representing either a successful result or an error.
    Use `Result.success()` or `Result.failure()` to create instances.
    """

    ok: T | None  # Success value, if any
    error: str | None  # Error message, if any
    exception: Exception | None  # Exception, if any. It's optional.
    extra: Extra  # Optional extra metadata

    def __init__(self) -> None:
        raise RuntimeError("Result is not intended to be instantiated directly. Use the static methods instead.")

    def is_ok(self) -> bool:
        """
        Returns True if the result represents success.
        """
        return self.error is None

    def is_error(self) -> bool:
        """
        Returns True if the result represents an error.
        """
        return self.error is not None

    def is_exception(self) -> bool:
        """
        Returns True if an exception is attached to the result.
        """
        return self.exception is not None

    def unwrap(self) -> T:
        """
        Returns the success value.
        Raises RuntimeError if the result is an error.
        """
        if not self.is_ok():
            raise RuntimeError(f"Called unwrap() on a failure value: {self.error}")
        return cast(T, self.ok)

    def unwrap_or(self, default: T) -> T:
        """
        Returns the success value if available, otherwise returns the given default.
        """
        if not self.is_ok():
            return default
        return cast(T, self.ok)

    def unwrap_error(self) -> str:
        """
        Returns the error message.
        Raises RuntimeError if the result is a success.
        """
        if self.is_ok():
            raise RuntimeError("Called unwrap_error() on a success value")
        return cast(str, self.error)

    def unwrap_exception(self) -> Exception:
        """
        Returns the attached exception if present.
        Raises RuntimeError if the result has no exception attached.
        """
        if self.exception is not None:
            return self.exception
        raise RuntimeError("No exception provided")

    def ok_or_error(self) -> T | str:
        """
        Returns the success value if available, otherwise returns the error message.
        """
        if self.is_ok():
            return self.unwrap()
        return self.unwrap_error()

    def to_dict(self) -> dict[str, object]:
        """
        Returns a dictionary representation of the result.
        Note: the exception is converted to a string if present.
        """
        return {
            "ok": self.ok,
            "error": self.error,
            "exception": str(self.exception) if self.exception else None,
            "extra": self.extra,
        }

    def map(self, fn: Callable[[T], U]) -> Result[U]:
        if self.is_ok():
            try:
                new_value = fn(cast(T, self.ok))
                return Result.success(new_value, extra=self.extra)
            except Exception as e:
                return Result.failure(("map_exception", e), extra=self.extra)
        return cast(Result[U], self)

    async def map_async(self, fn: Callable[[T], Awaitable[U]]) -> Result[U]:
        if self.is_ok():
            try:
                new_value = await fn(cast(T, self.ok))
                return Result.success(new_value, extra=self.extra)
            except Exception as e:
                return Result.failure(("map_exception", e), extra=self.extra)
        return cast(Result[U], self)

    def and_then(self, fn: Callable[[T], Result[U]]) -> Result[U]:
        if self.is_ok():
            try:
                return fn(cast(T, self.ok))
            except Exception as e:
                return Result.failure(("and_then_exception", e), extra=self.extra)
        return cast(Result[U], self)

    async def and_then_async(self, fn: Callable[[T], Awaitable[Result[U]]]) -> Result[U]:
        if self.is_ok():
            try:
                return await fn(cast(T, self.ok))
            except Exception as e:
                return Result.failure(("and_then_exception", e), extra=self.extra)
        return cast(Result[U], self)

    def __repr__(self) -> str:
        parts: list[str] = []
        if self.ok is not None:
            parts.append(f"ok={self.ok!r}")
        if self.error is not None:
            parts.append(f"error={self.error!r}")
        if self.exception is not None:
            parts.append(f"exception={self.exception!r}")
        if self.extra is not None:
            parts.append(f"extra={self.extra!r}")
        return f"Result({', '.join(parts)})"

    def __hash__(self) -> int:
        return hash(
            (
                self.ok,
                self.error,
                self.exception,
                frozenset(self.extra.items()) if self.extra else None,
            )
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Result):
            return False
        return (
            self.ok == other.ok and self.error == other.error and self.exception == other.exception and self.extra == other.extra
        )

    @classmethod
    def _create(cls, ok: T | None, error: str | None, exception: Exception | None, extra: Extra) -> Result[T]:
        obj = object.__new__(cls)
        obj.ok = ok
        obj.error = error
        obj.exception = exception
        obj.extra = extra
        return obj

    @staticmethod
    def success(ok: T, extra: Extra = None) -> Result[T]:
        """
        Creates a successful Result instance.

        Args:
            ok: The success value to store in the Result.
            extra: Optional extra metadata to associate with the Result.

        Returns:
            A Result instance representing success with the provided value.
        """
        return Result._create(ok=ok, error=None, exception=None, extra=extra)

    @staticmethod
    def failure(error: str | Exception | tuple[str, Exception], extra: Extra = None) -> Result[T]:
        """
        Creates a Result instance representing a failure.

        Args:
            error: The error information, which can be:
                - A string error message
                - An Exception object
                - A tuple containing (error_message, exception)
            extra: Optional extra metadata to associate with the Result.

        Returns:
            A Result instance representing failure with the provided error information.
        """
        if isinstance(error, tuple):
            error_, exception = error
        elif isinstance(error, Exception):
            error_ = "exception"
            exception = error
        else:
            error_ = error
            exception = None

        return Result._create(ok=None, error=error_, exception=exception, extra=extra)

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: type[Any], _handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.any_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: x.to_dict()),
        )

    @classmethod
    def _validate(cls, value: object) -> Result[Any]:
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            return cls._create(
                ok=value.get("ok"),
                error=value.get("error"),
                exception=value.get("exception"),
                extra=value.get("extra"),
            )
        raise TypeError(f"Invalid value for Result: {value}")
