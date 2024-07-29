from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any, Generic, Literal, NoReturn, TypeAlias, TypeVar

T = TypeVar("T", covariant=True)  # Success type
U = TypeVar("U")
F = TypeVar("F")
TBE = TypeVar("TBE", bound=BaseException)


class Ok(Generic[T]):
    __match_args__ = ("ok",)

    def __init__(self, value: T, data: Any = None) -> None:
        self._value = value
        self.data = data

    def __repr__(self) -> str:
        if self.data is None:
            return f"Ok({self._value!r})"
        else:
            return f"Ok({self._value!r}, data={self.data!r})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Ok) and self._value == other._value and self.data == other.data

    def __ne__(self, other: Any) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        return hash((True, self._value, self.data))

    def is_ok(self) -> Literal[True]:
        return True

    def is_err(self) -> Literal[False]:
        return False

    @property
    def ok(self) -> T:
        return self._value

    @property
    def err(self) -> None:
        return None

    def expect(self, _message: str) -> T:
        return self._value

    def expect_err(self, message: str) -> NoReturn:
        raise UnwrapError(self, message)

    def unwrap(self) -> T:
        return self._value

    def unwrap_err(self) -> NoReturn:
        raise UnwrapError(self, "Called `Result.unwrap_err()` on an `Ok` value")

    def unwrap_or(self, _default: U) -> T:
        return self._value

    def unwrap_or_else(self, op: object) -> T:
        return self._value

    def unwrap_or_raise(self, e: object) -> T:
        return self._value

    def map(self, op: Callable[[T], U]) -> Ok[U]:
        return Ok(op(self._value), data=self.data)

    def map_or(self, default: object, op: Callable[[T], U]) -> U:
        return op(self._value)

    def map_or_else(self, err_op: object, ok_op: Callable[[T], U]) -> U:
        """
        The contained result is `Ok`, so return original value mapped to
        a new value using the passed in `op` function.
        """
        return ok_op(self._value)

    def map_err(self, op: object) -> Ok[T]:
        """
        The contained result is `Ok`, so return `Ok` with the original value
        """
        return self

    def and_then(self, op: Callable[[T], U | Result[U]]) -> Result[U]:
        """
        The contained result is `Ok`, so return the result of `op` with the
        original value passed in. If return of `op` function is not Result, it will be a Ok value.
        """
        try:
            res = op(self._value)
            if not isinstance(res, Ok | Err):
                res = Ok(res)
        except Exception as e:
            res = Err(e)
        res.data = self.data
        return res

    def or_else(self, op: object) -> Ok[T]:
        return self

    def ok_or_err(self) -> T | str:
        return self._value

    def ok_or_none(self) -> T | None:
        return self._value


class Err:
    __match_args__ = ("err",)

    def __init__(self, value: str | Exception, data: Any = None) -> None:
        self._value = f"exception: {value}" if isinstance(value, Exception) else value
        self.data = data

    def __repr__(self) -> str:
        if self.data is None:
            return f"Err({self._value!r})"
        else:
            return f"Err({self._value!r}, data={self.data!r})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Err) and self._value == other._value and self.data == other.data

    def __ne__(self, other: Any) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        return hash((False, self._value, self.data))

    def is_ok(self) -> Literal[False]:
        return False

    def is_err(self) -> Literal[True]:
        return True

    @property
    def ok(self) -> None:
        """
        Return `None`.
        """
        return None

    @property
    def err(self) -> str:
        """
        Return the error.
        """
        return self._value

    def expect(self, message: str) -> NoReturn:
        """
        Raises an `UnwrapError`.
        """
        exc = UnwrapError(
            self,
            f"{message}: {self._value!r}",
        )
        if isinstance(self._value, BaseException):
            raise exc from self._value
        raise exc

    def expect_err(self, _message: str) -> str:
        """
        Return the inner value
        """
        return self._value

    def unwrap(self) -> NoReturn:
        """
        Raises an `UnwrapError`.
        """
        exc = UnwrapError(
            self,
            f"Called `Result.unwrap()` on an `Err` value: {self._value!r}",
        )
        if isinstance(self._value, BaseException):
            raise exc from self._value
        raise exc

    def unwrap_err(self) -> str:
        """
        Return the inner value
        """
        return self._value

    def unwrap_or(self, default: U) -> U:
        """
        Return `default`.
        """
        return default

    def unwrap_or_else(self, op: Callable[[str], T]) -> T:
        """
        The contained result is ``Err``, so return the result of applying
        ``op`` to the error value.
        """
        return op(self._value)

    def unwrap_or_raise(self, e: type[TBE]) -> NoReturn:
        """
        The contained result is ``Err``, so raise the exception with the value.
        """
        raise e(self._value)

    def map(self, op: object) -> Err:
        """
        Return `Err` with the same value
        """
        return self

    def map_or(self, default: U, op: object) -> U:
        """
        Return the default value
        """
        return default

    def map_or_else(self, err_op: Callable[[str], U], ok_op: object) -> U:
        """
        Return the result of the default operation
        """
        return err_op(self._value)

    def and_then(self, op: object) -> Err:
        """
        The contained result is `Err`, so return `Err` with the original value
        """
        return self

    def ok_or_err(self) -> T | str:
        return self._value

    def ok_or_none(self) -> T | None:
        return None


Result: TypeAlias = Ok[T] | Err


class UnwrapError(Exception):
    _result: Result[object]

    def __init__(self, result: Result[object], message: str) -> None:
        self._result = result
        super().__init__(message)

    @property
    def result(self) -> Result[Any]:
        return self._result


def try_ok(fn: Callable[..., Result[T]], *, args: tuple[object], attempts: int, delay: int | float = 0) -> Result[T]:
    if attempts <= 0:
        raise ValueError("attempts must be more than zero")
    res: Result[T] = Err("not started")
    for _ in range(attempts):
        res = fn(*args)
        if res.is_ok():
            return res
        if delay:
            time.sleep(delay)
    return res
