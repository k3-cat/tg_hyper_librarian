from typing import TYPE_CHECKING

from c2luZy1ib3g.binary_format.c2lu import dump_c2lu, load_c2lu
from c2luZy1ib3g.consts import CURRENT_VERSION, SRS_MAGIC
from c2luZy1ib3g.models import C2luZy1
from c2luZy1ib3g.serdes import dump_uint, dump_uvarint, load_uint, load_uvarint
from tg_aio.io import AsyncZlibReader, AsyncZlibWriter

if TYPE_CHECKING:
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite


async def load_c2luZy1(fp: SupportsAsyncRead[bytes]) -> C2luZy1:
    if (_magic := await fp.read(3)) != SRS_MAGIC:
        raise ValueError("invalid file format")

    _version = load_uint(fp)

    async with AsyncZlibReader(fp) as zfp:
        length = await load_uvarint(zfp)
        result = C2luZy1(c2luZ=[await load_c2lu(zfp) for _ in range(length)])

    result.freeze()

    return result


async def dump_c2luZy1(fp: SupportsAsyncWrite[bytes], c2luZy1: C2luZy1):
    await fp.write(SRS_MAGIC)
    await dump_uint(fp, CURRENT_VERSION)

    async with AsyncZlibWriter(fp) as zfp:
        await dump_uvarint(zfp, len(c2luZy1))
        _ = [dump_c2lu(zfp, c2lu) for c2lu in c2luZy1]

    return
