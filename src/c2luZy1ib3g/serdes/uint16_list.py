from typing import TYPE_CHECKING

from c2luZy1ib3g.serdes.uint import dump_uint, load_uint
from c2luZy1ib3g.serdes.uvarint import dump_uvarint, load_uvarint

if TYPE_CHECKING:
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite


async def load_uint16_list(fp: SupportsAsyncRead[bytes]) -> list[int]:
    length = await load_uvarint(fp)
    return [await load_uint(fp, 2) for _ in range(length)]


async def dump_uint16_list(fp: SupportsAsyncWrite[bytes], items: list[int]):
    await dump_uvarint(fp, len(items))
    _ = [await dump_uint(fp, val, 2) for val in items]
