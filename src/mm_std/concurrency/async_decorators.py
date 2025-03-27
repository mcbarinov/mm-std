import asyncio
import functools
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def async_synchronized(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    lock = asyncio.Lock()

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        async with lock:
            return await func(*args, **kwargs)

    return wrapper


T = TypeVar("T")


def async_synchronized_parameter[T, **P](
    arg_index: int = 0, skip_if_locked: bool = False
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T | None]]]:
    locks: dict[object, asyncio.Lock] = defaultdict(asyncio.Lock)

    def outer(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T | None]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            if len(args) <= arg_index:
                raise ValueError(f"Function called with fewer than {arg_index + 1} positional arguments")

            key = args[arg_index]

            if skip_if_locked and locks[key].locked():
                return None

            try:
                async with locks[key]:
                    return await func(*args, **kwargs)
            finally:
                # Clean up the lock if no one is waiting
                # TODO: I'm not sure if the next like is OK
                if not locks[key].locked() and not locks[key]._waiters:  # noqa: SLF001
                    locks.pop(key, None)

        # Store locks for potential external access
        wrapper.locks = locks  # type: ignore[attr-defined]
        return wrapper

    return outer
