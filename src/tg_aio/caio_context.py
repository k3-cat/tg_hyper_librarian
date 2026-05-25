import asyncio
from typing import TYPE_CHECKING
from weakref import finalize

from caio import AsyncioContext

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop

    from caio.asyncio_base import AsyncioContextBase


DEFAULT_CONTEXT_STORE = dict["AbstractEventLoop", "AsyncioContextBase"]()


def create_context(max_requests: int = AsyncioContext.MAX_REQUESTS_DEFAULT) -> AsyncioContextBase:
    loop = asyncio.get_event_loop()
    context = AsyncioContext(max_requests, loop=loop)

    def finalizer() -> None:
        context.close()
        DEFAULT_CONTEXT_STORE.pop(loop, None)

    finalize(loop, finalizer)
    DEFAULT_CONTEXT_STORE[loop] = context

    return context


def get_default_context() -> AsyncioContextBase:
    loop = asyncio.get_event_loop()
    context = DEFAULT_CONTEXT_STORE.get(loop)

    if context is not None:
        return context

    return create_context()
