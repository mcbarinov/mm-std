from __future__ import annotations

from collections.abc import Callable
from typing import Generic, NoReturn, TypeVar, cast, final

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E", bound=Exception)


@final
class Result(Generic[T]):
    """
    A result type that represents either a successful value (ok) or an error.
    """

    __slots__ = ("_data", "_error", "_value")
    __match_args__ = ("_value", "_error")

    def __init__(self, value: T | None, error: Exception | None, data: object | None) -> None:
        self._value = value
        self._error = error
        self._data = data

    def is_ok(self) -> bool:
        """Check if result contains a successful value."""
        return self._error is None

    def is_err(self) -> bool:
        """Check if result contains an error."""
        return self._error is not None

    def __new__(cls, *_args: object, **_kwargs: object) -> NoReturn:
        raise TypeError("Use Result.ok() or Result.err() to create instances.")

    @classmethod
    def ok(cls, value: T, data: object = None) -> Result[T]:
        """Create a successful result with the given value."""
        instance: Result[T] = super().__new__(cls)
        # Initialize directly instead of calling __init__
        instance._value = value
        instance._error = None
        instance._data = data
        return instance

    @classmethod
    def err(cls, error: str | Exception, data: object = None) -> Result[T]:
        """Create an error result with the given error."""
        exception = error if isinstance(error, Exception) else RuntimeError(error)
        instance: Result[T] = super().__new__(cls)
        # Initialize directly instead of calling __init__
        instance._value = None
        instance._error = exception
        instance._data = data
        return instance

    def unwrap(self) -> T:
        """Extract the value or raise the error if present."""
        if self._error:
            raise self._error
        # None is a valid value, so we cast to satisfy mypy
        return cast(T, self._value)

    def unwrap_or(self, default: T) -> T:
        """Extract the value or return the default if error."""
        if self._error:
            return default
        # None is a valid value, so we cast to satisfy mypy
        return cast(T, self._value)

    def unwrap_err(self) -> Exception:
        """Extract the error or raise a RuntimeError if value is present."""
        if self._error is None:
            raise RuntimeError(f"Expected error but got value: {self._value}")
        return self._error

    def map(self, fn: Callable[[T], U]) -> Result[U]:
        """Apply function to value if ok, otherwise propagate error."""
        if self._error:
            return Result[U].err(self._error, self._data)
            # return Result[U]._create_raw(None, self._error, self._data)
        try:
            # None is a valid value, so we cast to satisfy mypy
            return Result.ok(fn(cast(T, self._value)), self._data)
        except Exception as e:
            return Result.err(e, self._data)

    def map_err(self, fn: Callable[[Exception], E]) -> Result[T]:
        """Apply function to error if err, otherwise propagate value."""
        if self._error is None:
            return self
        try:
            return Result.err(fn(self._error), self._data)
        except Exception as e:
            return Result.err(e, self._data)

    def and_then(self, fn: Callable[[T], Result[U]]) -> Result[U]:
        """Chain operation that returns another Result."""
        if self._error:
            return Result[U].err(self._error, self._data)
            # return Result[U]._create_raw(None, self._error, self._data)
        try:
            # None is a valid value, so we cast to satisfy mypy
            return fn(cast(T, self._value))
        except Exception as e:
            return Result.err(e, self._data)

    def or_else(self, fn: Callable[[Exception], Result[T]]) -> Result[T]:
        """Chain operation that handles an error by returning another Result."""
        if self._error is None:
            return self
        try:
            return fn(self._error)
        except Exception as e:
            return Result.err(e, self._data)

    @property
    def value(self) -> T | None:
        """Get the success value, if any."""
        return self._value

    @property
    def error(self) -> Exception | None:
        """Get the error, if any."""
        return self._error

    @property
    def data(self) -> object | None:
        """Get additional data."""
        return self._data

    @classmethod
    def _create_raw(cls, value: T | None, error: Exception | None, data: object | None) -> Result[T]:
        """Internal method to create a Result instance directly."""
        instance: Result[T] = super().__new__(cls)
        instance._value = value
        instance._error = error
        instance._data = data
        return instance
