import asyncio
from functools import wraps
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from types import CoroutineType
    from typing import AsyncGenerator, Callable, Protocol

    from tg_utils import NestableAsyncContext

    class SupportsAsyncLock(Protocol):
        _lock: NestableAsyncContext[None]


def with_lock[**P, Y, R](
    func: Callable[P, CoroutineType[Y, None, R]], /
) -> Callable[P, CoroutineType[Y, None, R]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs):
        _lock = cast("SupportsAsyncLock", args[0])._lock
        async with _lock:
            return await func(*args, **kwargs)

    return wrapper


def iter_with_lock[**P, Y](
    func: Callable[P, AsyncGenerator[Y, None]], /
) -> Callable[P, AsyncGenerator[Y, None]]:
    def outter_wrapper(*args: P.args, **kwargs: P.kwargs):
        @wraps(func)
        async def inner_wrapper(*args: P.args, **kwargs: P.kwargs):
            return func(*args, **kwargs)

        return asyncio.run(with_lock(inner_wrapper)(*args, **kwargs))

    return outter_wrapper
