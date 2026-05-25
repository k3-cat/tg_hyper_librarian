import time
from pathlib import Path
from typing import TYPE_CHECKING, cast, overload

from tg_aio.io import AsyncBufferedFileIO
from tg_h_l_.sinks._base import RWContentDesc, SinkBase

if TYPE_CHECKING:
    from io import FileIO

    from _typeshed import (
        OpenBinaryModeReading,
        OpenBinaryModeWriting,
        OpenTextModeReading,
        OpenTextModeWriting,
    )

    from tg_aio._buffered_base import AsyncBufferedReader, AsyncBufferedWriter


class FileSink(SinkBase):
    def __init__(self, base_dir_path: Path, **kwargs) -> None:
        super().__init__(**kwargs)

        base_dir_path.mkdir(mode=0o700, exist_ok=True)
        self._dir_path = base_dir_path
        self._io_map = dict[str, Path]()

    def register(self, name: str):
        f_path = self._dir_path / name
        self._io_map[name] = f_path

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
        f_path = self._io_map[name]
        with open(f_path, mode) as fp:
            if "b" in mode:
                return AsyncBufferedFileIO(cast("FileIO", fp))

            raise NotImplementedError

    def is_cached(self, name: str) -> float | None:
        now = time.time()
        f_path = self._io_map[name]
        if (
            f_path.exists()
            and f_path.stat().st_size
            and ((age := (now - f_path.stat().st_mtime)) <= self.cache_age)
        ):
            return age

        return None
