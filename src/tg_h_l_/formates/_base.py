from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import AsyncGenerator

    from tg_aio._buffered_base import AsyncBufferedReader, AsyncBufferedWriter
    from tg_h_l_.dto import RulePack


class ReadableFormat[T: str | bytes](ABC):
    @abstractmethod
    def load(self, fp: AsyncBufferedReader[T]) -> AsyncGenerator[RulePack]: ...


class WritableFormat[T: str | bytes](ABC):
    @abstractmethod
    async def dump(self, fp: AsyncBufferedWriter[T], rulepack: RulePack) -> None: ...


class RWFormat[T: str | bytes](ReadableFormat[T], WritableFormat[T]): ...
