from collections.abc import Awaitable, Callable
from typing import Any

type CallableAny = Callable[..., Any]
type Func = Callable[..., object]
type AsyncFunc = Callable[..., Awaitable[object]]
type Args = tuple[object, ...]
type Kwargs = dict[str, object]
