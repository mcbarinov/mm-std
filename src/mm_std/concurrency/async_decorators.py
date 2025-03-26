import asyncio
import functools
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
