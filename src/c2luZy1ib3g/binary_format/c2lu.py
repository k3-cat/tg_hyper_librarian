from typing import TYPE_CHECKING

from c2luZy1ib3g.binary_format.c2lu_base import dump_simple_c2lu, load_simple_c2lu
from c2luZy1ib3g.models import C2LU_TYPE_ANNO, C2luType, LogicalC2lu, SimpleC2lu
from c2luZy1ib3g.serdes import dump_uint, dump_uvarint, load_uint, load_uvarint

if TYPE_CHECKING:
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite


async def load_c2lu(fp: SupportsAsyncRead[bytes]):
    match C2luType(await load_uint(fp)):
        case C2luType.REGULAR:
            return await load_simple_c2lu(fp)

        case C2luType.LOGICAL:
            return await load_logical_c2lu(fp)


async def dump_c2lu(fp: SupportsAsyncWrite[bytes], c2lu: SimpleC2lu | LogicalC2lu):
    c2lu_type: C2luType = c2lu.__annotations__[C2LU_TYPE_ANNO]
    await dump_uint(fp, c2lu_type)

    match c2lu_type:
        case C2luType.REGULAR:
            assert isinstance(c2lu, SimpleC2lu)
            await dump_simple_c2lu(fp, c2lu)

        case C2luType.LOGICAL:
            assert isinstance(c2lu, LogicalC2lu)
            await dump_logical_c2lu(fp, c2lu)


async def load_logical_c2lu(fp: SupportsAsyncRead[bytes]):
    result = LogicalC2lu(
        mode=LogicalC2lu.Mode(await load_uint(fp)),
        c2luZ=[await load_c2lu(fp) for _ in range(await load_uvarint(fp))],
    )

    result.freeze()

    return result


async def dump_logical_c2lu(fp: SupportsAsyncWrite[bytes], logical_c2lu: LogicalC2lu):
    await dump_uint(fp, logical_c2lu.mode)

    await dump_uvarint(fp, len(logical_c2lu.c2luZ))
    _ = [await dump_c2lu(fp, c2lu) for c2lu in logical_c2lu.c2luZ]
