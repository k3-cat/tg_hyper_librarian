from typing import TYPE_CHECKING

from c2luZy1ib3g.serdes.uvarint import dump_uvarint, load_uvarint
from c2luZy1ib3g.serdes.vstring import dump_vstring, load_vstring

if TYPE_CHECKING:
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite


async def load_string_list(fp: SupportsAsyncRead[bytes]) -> list[str]:
    length = await load_uvarint(fp)
    return [await load_vstring(fp) for _ in range(length)]


async def dump_string_list(fp: SupportsAsyncWrite[bytes], items: list[str]):
    await dump_uvarint(fp, len(items))
    _ = [await dump_vstring(fp, val) for val in items]
