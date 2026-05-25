import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple

import aiohttp

from tg_h_l_.dto import RulePack
from tg_h_l_.sinks.http import HttpGetSink
from tg_utils import NestableAsyncContext

if TYPE_CHECKING:
    from typing import Iterable

    from tg_h_l_.formates._base import ReadableFormat, WritableFormat
    from tg_h_l_.sinks._base import ReadableContentDesc, WritableContentDesc


class SourceDesc(NamedTuple):
    storage: ReadableContentDesc
    format: ReadableFormat


class DestinationDesc(NamedTuple):
    storage: WritableContentDesc
    format: WritableFormat


def _check_binary(obj: ReadableFormat | WritableFormat):
    if isinstance(obj, ReadableFormat):
        func = obj.load
    else:
        func = obj.dump

    anno: str = func.__annotations__["fp"]
    if anno.endswith("[str]"):
        return False

    return True


@dataclass(frozen=True, kw_only=True)
class Ruleset:
    sources: Iterable[SourceDesc]
    destination: DestinationDesc

    async def fetch(self):
        logging.info("--- fetch ---")
        http_sinks = set[HttpGetSink]()
        for storage, _ in self.sources:
            if isinstance(storage.sink, HttpGetSink):
                http_sinks.add(storage.sink)

        for sink in http_sinks:
            async with NestableAsyncContext(aiohttp.ClientSession()) as ctx:
                await sink.fetch_all(ctx)

    async def build(self):
        logging.info("--- build ---")
        rulepacks = list[RulePack]()
        for storage, format in self.sources:
            mode = "rb" if _check_binary(format) else "r"
            async with storage.sink.open(storage.name, mode) as fp:
                async for rulepack in format.load(fp):
                    rulepacks.append(rulepack)

        result = RulePack()
        for rulepack in rulepacks:
            result.unsupported_rules.extend(rulepack.unsupported_rules)
            result.rules.extend(rulepack.rules)

        return result.reduce()

    async def compile(self):
        logging.info("--- compile ---")
        storage, format = self.destination
        mode = "wb" if _check_binary(format) else "w"
        async with storage.sink.open(storage.name, mode) as fp:
            await format.dump(fp, await self.build())
