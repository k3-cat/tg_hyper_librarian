import os
from io import FileIO
from typing import TYPE_CHECKING

from caio.asyncio_base import AsyncioContextBase

from tg_aio._base import AsyncFileRWPair
from tg_aio._buffered_base import AsyncBufferedRWPair
from tg_aio.caio_context import get_default_context
from tg_aio.lock import with_lock

if TYPE_CHECKING:
    from io import FileIO
    from typing import Literal

    from _typeshed import ReadableBuffer
    from caio.asyncio_base import AsyncioContextBase


class AsyncFileIO(AsyncFileRWPair[bytes]):
    chunk_size = 4 * 1024

    def __init__(self, /, fp: FileIO, context: AsyncioContextBase | None = None):
        super().__init__()

        self.__fp = fp
        self.__pos = fp.tell()
        self.__ctx = context if context is not None else get_default_context()
        self.mode = fp.mode  # pyright: ignore[reportAttributeAccessIssue]

        self.fileno = fp.fileno
        self.tell = fp.tell

    @with_lock
    async def read(self, size: int = 0, /):
        data = await self.__ctx.read(size, self.fileno(), offset=self.__pos)
        self.__pos += len(data)

        return data

    @with_lock
    async def write(self, buffer: ReadableBuffer, /):
        data = buffer if isinstance(buffer, bytes) else memoryview(buffer)
        return await self.__ctx.write(data, self.fileno(), offset=self.__pos)

    @with_lock
    async def seek(self, pos: int, whence: Literal[0, 1, 2] = os.SEEK_SET, /) -> int:
        pos = self.__fp.seek(pos, whence)
        self.__pos = pos

        return pos

    @with_lock
    async def fsync(self, /) -> None:
        return await self.__ctx.fsync(self.fileno())

    @with_lock
    async def fdsync(self, /) -> None:
        return await self.__ctx.fdsync(self.fileno())

    @with_lock
    async def flush(self):
        await self.fdsync()

    @with_lock
    async def truncate(self, size: int | None = None, /):
        size = self.__fp.truncate(size)
        self.__pos = self.__fp.tell()

        return size

    @with_lock
    async def close(self, /) -> None:
        if self.closed:
            return

        await self.fdsync()
        await super().close()
        del self.__fp
        del self.fileno
        del self.tell


class AsyncBufferedFileIO(AsyncFileIO, AsyncBufferedRWPair[bytes]):
    newline = b"\n"

    def __init__(self, /, fp: FileIO, context: AsyncioContextBase | None = None):
        super().__init__(fp, context)

        self._AsyncBufferBase__buffer = bytearray()

    @with_lock
    async def _read_chunk_(self) -> bytes:
        return await super().read(self.chunk_size)

    @with_lock
    async def _write_buffer_(self) -> int:
        size = await super().write(self._buffer_)
        self._buffer_.clear()

        return size

    @with_lock
    async def flush(self):
        await super().flush()
        await self.fdsync()
