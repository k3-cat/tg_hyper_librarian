import math
from abc import abstractmethod
from typing import TYPE_CHECKING

from typing_extensions import disjoint_base

from tg_aio._base import AsyncFileReader, AsyncFileWriter, AsyncIOBase, AsyncReader, AsyncWriter
from tg_aio.lock import iter_with_lock, with_lock

if TYPE_CHECKING:
    from typing import Sized

    from tg_aio.protocols import BufferLike


class AsyncBufferBase[T: Sized](AsyncIOBase):
    _buffer_: BufferLike[T]

    def __init__(self, buffer: BufferLike[T] | None) -> None:
        super().__init__()

        if buffer is not None:
            self._buffer_ = buffer

        else:
            self.chunk_size = 0
            self.close = super().close

    @with_lock
    async def close(self, /):
        if self.closed:
            return

        await super().close()
        self._buffer_.clear()
        del self._buffer_


@disjoint_base
class AsyncBufferedReader[T: Sized](AsyncBufferBase[T], AsyncReader[T]):
    newline: T

    @with_lock
    async def read(self, size: int = -1, /) -> T:
        if size < 0:
            size = math.inf  # type: ignore

        while len(self._buffer_) < size and (chunk := await self._read_chunk_()):
            self._buffer_ += chunk

        i = min(len(self._buffer_), size)
        data = self._buffer_[:i]
        del self._buffer_[:i]

        return data

    async def read1(self, size=-1, /):
        """This is the same as read."""

        return await self.read(size)

    @with_lock
    async def readline(self, /, size: int = -1) -> T:
        if size < 0:
            size = math.inf  # type: ignore

        i = 0
        while i < size:
            if self._buffer_[i] == self.newline:
                break

            i += 1
            if (buff_len := len(self._buffer_)) < (i + 1):
                if not (chunk := await self._read_chunk_()):
                    i = buff_len - 1

                    break

                self._buffer_ += chunk

        line = self._buffer_[:i]
        del self._buffer_[:i]

        return line

    @iter_with_lock
    async def readlines(self, /):
        while line := await self.readline(-1):
            yield line


@disjoint_base
class AsyncBufferedWriter[T: Sized, R_f = None](AsyncBufferBase[T], AsyncWriter[T, R_f]):
    @abstractmethod
    async def _write_buffer_(self, /) -> int: ...

    @with_lock
    async def write(self, data: T, /) -> int:
        self._buffer_ += data
        size = 0
        while self.chunk_size < len(self._buffer_):
            size += await self._write_buffer_()

        return size

    @with_lock
    async def flush(self, /) -> R_f:
        return await self._write_buffer_()  # type: ignore

    @with_lock
    async def close(self, /):
        await self.flush()
        await super().close()


class AsyncBufferedRWPair[T: Sized, R_f = None](
    AsyncBufferedReader[T], AsyncBufferedWriter[T, R_f]
): ...


class AsyncBufferedFileReader[T: Sized](AsyncFileReader[T], AsyncBufferedReader[T]): ...


class AsyncBufferedFileWriter[T: Sized, R_f = None](
    AsyncFileWriter[T, R_f, int], AsyncBufferedWriter[T, R_f]
): ...


class AsyncBufferedFileRWPair[T: Sized, R_f = None, R_w = int](
    AsyncBufferedFileReader[T], AsyncBufferedFileWriter[T, R_f]
): ...
