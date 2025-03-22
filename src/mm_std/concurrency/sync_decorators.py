import functools
from collections import defaultdict
from collections.abc import Callable
from threading import Lock


def synchronized_parameter[T, **P](arg_index: int = 0, skip_if_locked: bool = False) -> Callable[..., Callable[P, T | None]]:
    locks: dict[object, Lock] = defaultdict(Lock)

    def outer(func: Callable[P, T]) -> Callable[P, T | None]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            if skip_if_locked and locks[args[arg_index]].locked():
                return None
            try:
                with locks[args[arg_index]]:
                    return func(*args, **kwargs)
            finally:
                locks.pop(args[arg_index], None)

        wrapper.locks = locks  # type: ignore[attr-defined]
        return wrapper

    return outer


def synchronized[T, **P](fn: Callable[P, T]) -> Callable[P, T]:
    lock = Lock()

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        with lock:
            return fn(*args, **kwargs)

    return wrapper
