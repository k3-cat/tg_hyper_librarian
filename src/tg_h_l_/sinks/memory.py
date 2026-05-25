import os
import time
from io import BytesIO, TextIOWrapper
from typing import TYPE_CHECKING, NamedTuple, overload

from tg_aio.io import AsyncBytesIO, AsyncTextIO
from tg_h_l_.sinks._base import RWContentDesc, SinkBase

if TYPE_CHECKING:
    from _typeshed import (
        OpenBinaryModeReading,
        OpenBinaryModeWriting,
        OpenTextModeReading,
        OpenTextModeWriting,
    )

    from tg_aio._buffered_base import AsyncBufferedReader, AsyncBufferedWriter


class _Metadata(NamedTuple):
    mtime: float
    size: int


__NEW_CACHE_INFO = _Metadata(0.0, 0)


class MemorySink(SinkBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._io_map = dict[str, BytesIO | None]()
        self._metadata_map = dict[str, _Metadata]()

    def register(self, name: str):
        self._io_map[name] = None

        return RWContentDesc(self, name)

    @overload
    def open(self, name: str, mode: OpenTextModeReading) -> AsyncBufferedReader[str]: ...
    @overload
    def open(self, name: str, mode: OpenTextModeWriting) -> AsyncBufferedWriter[str]: ...
    @overload
    def open(self, name: str, mode: OpenBinaryModeReading) -> AsyncBufferedReader[bytes]: ...
    @overload
    def open(self, name: str, mode: OpenBinaryModeWriting) -> AsyncBufferedWriter[bytes]: ...
    def open(self, name: str, mode: str) -> AsyncBufferedReader | AsyncBufferedWriter:
        mem_file = self._io_map[name]
        if mem_file is not None and "x" in mode:
            raise FileExistsError(name)

        mem_file = mem_file or BytesIO()
        mem_file.seek(0, os.SEEK_SET if "a" not in mode else os.SEEK_END)

        if "w" in mode:
            self._metadata_map[name] = _Metadata(time.time(), 0)
            mem_file.truncate(0)

        if "b" in mode:
            return AsyncBytesIO(mem_file)

        return AsyncTextIO(TextIOWrapper(mem_file))

    def is_cached(self, name: str) -> float | None:
        now = time.time()
        if (cache_info := self._metadata_map.get(name, __NEW_CACHE_INFO)) and (
            (age := (now - cache_info.mtime)) <= self.cache_age
        ):
            return age

        return None
