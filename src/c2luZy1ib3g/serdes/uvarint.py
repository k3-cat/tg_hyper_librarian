from typing import TYPE_CHECKING

from c2luZy1ib3g.serdes.uint import dump_uint

if TYPE_CHECKING:
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite


MAX_VARINT_LEN64 = 10
_OVERFLOW_ERROR = OverflowError(f"integer > {MAX_VARINT_LEN64} bytes")


async def load_uvarint(fp: SupportsAsyncRead[bytes]) -> int:
    x = 0
    sig = 0
    for i in range(MAX_VARINT_LEN64):
        chunk = await fp.read(1)
        if not chunk:
            raise EOFError()

        byte = chunk[0]
        if byte < 0x80:
            if i == MAX_VARINT_LEN64 - 1 and byte > 1:
                raise _OVERFLOW_ERROR

            return x | (byte << sig)

        x |= (byte & 0x7F) << sig
        sig += 7

    raise _OVERFLOW_ERROR


async def dump_uvarint(fp: SupportsAsyncWrite[bytes], x: int) -> int:
    i = 0
    while x >= 0x80:
        await dump_uint(fp, (x % 0xFF) | 0x80)
        x >>= 7
        i += 1

    await dump_uint(fp, x)

    return i + 1
