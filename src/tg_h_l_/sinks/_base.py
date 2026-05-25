from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, NamedTuple, overload

if TYPE_CHECKING:
    from _typeshed import (
        OpenBinaryModeReading,
        OpenBinaryModeWriting,
        OpenTextModeReading,
        OpenTextModeWriting,
    )

    from tg_aio._buffered_base import AsyncBufferedReader, AsyncBufferedWriter


class ContentDescBase(NamedTuple):
    sink: "SinkBase"
    name: str


class ReadableContentDesc(ContentDescBase): ...


class WritableContentDesc(ContentDescBase): ...


class RWContentDesc(ContentDescBase): ...


class SinkBase[T: ContentDescBase](ABC):
    def __init__(self, /, cache_age: int = 3600) -> None:
        super().__init__()

        self.cache_age = cache_age

    @abstractmethod
    def register(self, name: str) -> T: ...

    def is_cached(self, name: str) -> float | None:
        return None

    @overload
    def open(self, name: str, mode: OpenTextModeReading) -> AsyncBufferedReader[str]: ...
    @overload
    def open(self, name: str, mode: OpenTextModeWriting) -> AsyncBufferedWriter[str]: ...
    @overload
    def open(self, name: str, mode: OpenBinaryModeReading) -> AsyncBufferedReader[bytes]: ...
    @overload
    def open(self, name: str, mode: OpenBinaryModeWriting) -> AsyncBufferedWriter[bytes]: ...
    @abstractmethod
    def open(self, name: str, mode: str) -> AsyncBufferedReader | AsyncBufferedWriter: ...
