from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite


async def load_uint(fp: SupportsAsyncRead[bytes], length: int = 1) -> int:
    return int.from_bytes(await fp.read(length), byteorder="big", signed=False)


async def dump_uint(fp: SupportsAsyncWrite[bytes], x: int, length: int = 1) -> int:
    return await fp.write(x.to_bytes(length, byteorder="big", signed=False))
