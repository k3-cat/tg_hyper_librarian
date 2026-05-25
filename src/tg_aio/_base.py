import asyncio
import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, AsyncContextManager

from typing_extensions import disjoint_base

from tg_aio.lock import iter_with_lock, with_lock
from tg_utils import NestableAsyncContext

if TYPE_CHECKING:
    from types import TracebackType
    from typing import Literal, cast

    from _typeshed import OpenBinaryMode, OpenTextMode

    from tg_aio.lock import SupportsAsyncLock
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncSeek, SupportsAsyncWrite


@disjoint_base
class AsyncIOBase(AsyncContextManager):
    chunk_size: int = 0

    def __init__(self, /) -> None:
        super().__init__()

        self._lock = NestableAsyncContext(asyncio.Lock())
        self.closed: bool = False

    @with_lock
    async def close(self):
        if self.closed:
            return

        self.closed = True

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
        /,
    ):
        await self.close()

        return None


if TYPE_CHECKING:
    __aio_base: SupportsAsyncLock = cast(AsyncIOBase, None)


class AsyncReader[T](AsyncIOBase):
    def readable(self, /) -> bool:
        if self.closed:
            raise ValueError("I/O operation on closed file.")

        return True

    @abstractmethod
    async def read(self, size: int = ..., /) -> T: ...

    @abstractmethod
    async def _read_chunk_(self, /) -> T: ...

    @iter_with_lock
    async def iter_chunked(self, /):
        while chunk := await self._read_chunk_():
            yield chunk


if TYPE_CHECKING:
    __aio_reader: SupportsAsyncRead = cast(AsyncReader, None)


class AsyncWriter[T, R_f = None, R_w = int](AsyncIOBase):
    def writable(self, /) -> bool:
        if self.closed:
            raise ValueError("I/O operation on closed file.")

        return True

    @abstractmethod
    async def write(self, s: T, /) -> R_w: ...

    @abstractmethod
    async def truncate(self, size: int | None = None) -> int: ...

    @abstractmethod
    async def flush(self, /) -> R_f:
        await asyncio.sleep(0)

        return 0  # pyright: ignore[reportReturnType]


if TYPE_CHECKING:
    __aio_writer: SupportsAsyncWrite = cast(AsyncWriter, None)


class AsyncRWPair[T, R_f = None, R_w = int](AsyncReader[T], AsyncWriter[T, R_f, R_w]): ...


@disjoint_base
class AsyncFileBase[T_name = str](AsyncIOBase, ABC):
    mode: OpenBinaryMode | OpenTextMode
    name: T_name

    @abstractmethod
    def fileno(self) -> int: ...

    def seekable(self, /) -> bool:
        if self.closed:
            raise ValueError("I/O operation on closed file.")

        return True

    @abstractmethod
    async def seek(self, pos: int, whence: Literal[0, 1, 2] = os.SEEK_SET, /) -> int: ...

    @abstractmethod
    def tell(self) -> int: ...


if TYPE_CHECKING:
    __aio_file_base: SupportsAsyncSeek = cast(AsyncFileBase, None)


class AsyncFileReader[T](AsyncFileBase, AsyncReader[T]): ...


class AsyncFileWriter[T, R_f = None, R_w = int](AsyncFileBase, AsyncWriter[T, R_f, R_w]): ...


class AsyncFileRWPair[T, R_f = None, R_w = int](
    AsyncFileReader[T], AsyncFileWriter[T, R_f, R_w]
): ...
