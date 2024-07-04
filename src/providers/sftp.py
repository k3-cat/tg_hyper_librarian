from contextlib import contextmanager
from io import BufferedReader, BufferedWriter
from pathlib import Path
from typing import Any, Generator, Mapping


class Sftp:
    def __init__(self, _: Mapping[str, Any]) -> None:
        pass

    @contextmanager
    def fetch(self, path: Path) -> Generator[BufferedReader]:
        raise NotImplementedError()

    @contextmanager
    def push(self, path: Path) -> Generator[BufferedWriter]:
        raise NotImplementedError()

    def push_bytes(self, path: Path, content: bytes):
        raise NotImplementedError()
