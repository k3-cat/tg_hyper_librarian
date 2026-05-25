import zlib
from abc import ABC
from typing import TYPE_CHECKING

from tg_aio._buffered_base import AsyncBufferedReader, AsyncBufferedWriter
from tg_aio.lock import with_lock

if TYPE_CHECKING:
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite


class ZlibIOBase(ABC):
    chunk_size = 64 * 1024


class AsyncZlibReader(ZlibIOBase, AsyncBufferedReader[bytes]):
    def __init__(self, /, fp: SupportsAsyncRead[bytes]) -> None:
        super().__init__(bytearray())

        self._fp_ = fp
        self.__decompression_obj = zlib.decompressobj()
        if fp_lock := fp.__getattribute__("_lock"):
            self._lock = fp_lock

    @with_lock
    async def _read_chunk_(self, /) -> bytes:
        return self.__decompression_obj.decompress(await self._fp_.read(self.chunk_size))

    @with_lock
    async def close(self, /):
        if self.closed:
            return

        await super().close()
        del self.__decompression_obj
        del self._fp_


class AsyncZlibWriter(ZlibIOBase, AsyncBufferedWriter[bytes, int]):
    def __init__(self, /, fp: SupportsAsyncWrite[bytes]) -> None:
        super().__init__(bytearray())

        self._fp_ = fp
        self.__compression_obj = zlib.compressobj()
        if fp_lock := fp.__getattribute__("_lock"):
            self._lock = fp_lock

        self.truncate = fp.truncate

    @with_lock
    async def _write_buffer_(self, /) -> int:
        i = min(len(self._buffer_), self.chunk_size)
        size = await self._fp_.write(self.__compression_obj.compress(self._buffer_[:i]))
        del self._buffer_[:i]

        return size

    @with_lock
    async def flush(self, /) -> int:
        size = await super().flush()
        size += await self._fp_.write(self.__compression_obj.flush())
        if fp_flush := self._fp_.__getattribute__("flush") or None:
            await fp_flush()

        return size

    @with_lock
    async def truncate(self, size: int | None = None) -> int:
        return await self._fp_.truncate(size)

    @with_lock
    async def close(self, /) -> None:
        if self.closed:
            return

        await super().close()
        del self.__compression_obj
        del self._fp_
