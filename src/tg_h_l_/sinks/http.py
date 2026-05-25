import binascii
import logging
from typing import TYPE_CHECKING

import aiohttp

from tg_h_l_.sinks._base import ReadableContentDesc, SinkBase
from tg_utils import NestableAsyncContext

if TYPE_CHECKING:
    from typing import Callable, Iterable

    from aiohttp import ClientSession
    from yarl import URL

    from tg_aio.protocols import SupportsAsyncWrite


CHUNK_SIZE = 32 * 1024


async def __do_fetch__(session: aiohttp.ClientSession, url: URL, fp: SupportsAsyncWrite[bytes]):
    async with session.get(url) as res:
        if not res.ok:
            logging.error(res.status, res.reason, url)

            return

        async for chunk in res.content.iter_chunked(CHUNK_SIZE):
            await fp.write(chunk)

        logging.info(url, "DONE", res.status, f"{(res.content_length or 0) / 1024:.1f} kiB")


class HttpGetSink(SinkBase):
    def __init__(self, base_sink: SinkBase, base_url: URL) -> None:
        super().__init__()

        self.base_url = base_url
        self.url_id = f"{binascii.crc32(str(base_url).encode()):x}"
        self.__base_sink = base_sink
        self.__url_map = dict[str, URL]()

        self.open = self.__base_sink.open

    def register(self, name: str, key: str | None = None):
        key = f"{self.url_id}_{key or name}"
        url = self.base_url.joinpath(name)
        self.__url_map[key] = url

        return ReadableContentDesc

    def register_urls(
        self, names: Iterable[str], map_keys: Callable[[str], str] = lambda name: name
    ):
        yield from (self.register(name, map_keys(name)) for name in names)

    async def fetch_all(self, ctx: NestableAsyncContext[ClientSession] | None = None):
        async with ctx or aiohttp.ClientSession() as session:
            for filename, url in self.__url_map.items():
                if age := self.is_cached(filename):
                    logging.info(filename, "cache: HIT, age:", f"{age / 60:.1f} min")

                    continue

                async with self.open(filename, "wb") as fp:
                    await __do_fetch__(session, url, fp)
