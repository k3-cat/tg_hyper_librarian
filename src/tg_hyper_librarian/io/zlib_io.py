import zlib
from collections.abc import Buffer
from io import BufferedIOBase
from typing import BinaryIO

BUFFER_SIZE = 64 * 1024


class ZlibIOBase(BufferedIOBase):
    def __init__(self, sp: BinaryIO) -> None:
        super().__init__()
        self._sp = sp

    def __getstate__(self):
        if self.closed:
            raise ValueError("__getstate__ on closed file")
        return self.__dict__.copy()


class ZlibReaderIO(ZlibIOBase):
    def __init__(self, sp: BinaryIO) -> None:
        super().__init__(sp)
        self._decompression_obj = zlib.decompressobj()
        self._buffer = bytearray()

    def readable(self) -> bool:
        if self.closed:
            raise ValueError("I/O operation on closed file.")
        return True

    def read(self, size: int | None = -1) -> bytes:
        if self.closed:
            raise ValueError("read from closed file")
        if size is None:
            size = -1
        else:
            try:
                size_index = size.__index__
            except AttributeError:
                raise TypeError(f"{size!r} is not an integer")
            else:
                size = size_index()

        self._buffer += self._decompression_obj.decompress(self._sp.read(BUFFER_SIZE if size >= 0 else -1))

        if size < 0:
            size = len(self._buffer)
        b = self._buffer[:size]
        self._buffer = self._buffer[size:]

        return bytes(b)

    def read1(self, size=-1):
        """This is the same as read."""
        return self.read(size)

    def close(self):
        if self._buffer is not None:
            self._buffer.clear()
        self._sp.close()
        super().close()


class ZlibWriterIO(ZlibIOBase):
    def __init__(self, sp: BinaryIO) -> None:
        super().__init__(sp)
        self._compression_obj = zlib.compressobj()

    def writable(self) -> bool:
        if self.closed:
            raise ValueError("I/O operation on closed file.")
        return True

    def write(self, b: Buffer) -> int:
        if self.closed:
            raise ValueError("write to closed file")
        if isinstance(b, str):
            raise TypeError("can't write str to binary stream")
        with memoryview(b) as view:
            n = view.nbytes  # Size of any bytes-like object
        if n == 0:
            return 0

        self._sp.write(self._compression_obj.compress(b))

        return n

    def close(self) -> None:
        if not self.closed:
            self._sp.write(self._compression_obj.flush())
        super().close()
