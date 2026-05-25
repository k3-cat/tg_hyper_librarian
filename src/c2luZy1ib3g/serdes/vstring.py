from typing import TYPE_CHECKING

from c2luZy1ib3g.serdes.uvarint import dump_uvarint, load_uvarint

if TYPE_CHECKING:
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite


async def load_vstring(fp: SupportsAsyncRead[bytes]) -> str:
    length = await load_uvarint(fp)
    return (await fp.read(length)).decode("utf-8")


async def dump_vstring(fp: SupportsAsyncWrite[bytes], string: str) -> int:
    await dump_uvarint(fp, len(string))
    return await fp.write(string.encode("utf-8"))
