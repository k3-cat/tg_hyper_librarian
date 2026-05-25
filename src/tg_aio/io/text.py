import asyncio
import os
from typing import TYPE_CHECKING

from tg_aio._buffered_base import AsyncBufferedRWPair
from tg_aio.lock import with_lock

if TYPE_CHECKING:
    from typing import Literal, TextIO, cast

    from tg_aio.protocols import SupportsAsyncSeek


class AsyncTextIO(AsyncBufferedRWPair[str]):
    newline = "\n"

    def __init__(self, fp: TextIO) -> None:
        super().__init__(None)

        self.__fp = fp
        self.tell = self.__fp.tell

    async def _read_chunk_(self, /) -> str:
        raise NotImplementedError

    @with_lock
    async def read(self, size=-1, /):
        return await asyncio.to_thread(self.__fp.read, size)

    @with_lock
    async def readline(self, /, size: int = -1) -> str:
        return await asyncio.to_thread(self.__fp.readline, size)

    async def _write_buffer_(self) -> int:
        raise NotImplementedError

    @with_lock
    async def write(self, data: str, /) -> int:
        return await asyncio.to_thread(self.__fp.write, data)

    @with_lock
    async def seek(self, pos: int, whence: Literal[0, 1, 2] = os.SEEK_SET, /) -> int:
        return self.__fp.seek(pos, whence)

    @with_lock
    async def truncate(self, size: int | None = None, /) -> int:
        return self.__fp.truncate(size)

    @with_lock
    async def flush(self) -> None:
        return await asyncio.to_thread(self.__fp.flush)

    @with_lock
    async def close(self, /) -> None:
        if self.closed:
            return

        await super().close()
        del self.__fp


if TYPE_CHECKING:
    __aio_text: SupportsAsyncSeek = cast(AsyncTextIO, None)
