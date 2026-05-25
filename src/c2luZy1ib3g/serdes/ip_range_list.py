from typing import TYPE_CHECKING

from c2luZy1ib3g.serdes.uint import dump_uint, load_uint
from c2luZy1ib3g.serdes.uvarint import dump_uvarint, load_uvarint

if TYPE_CHECKING:
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite
    from tg_ip import IPRange


async def load_ip_range_list(fp: SupportsAsyncRead[bytes]) -> list[IPRange]:
    _ = await load_uint(fp)  # version

    length = await load_uint(fp, 8)
    ip_ranges = list[IPRange]()
    for _ in range(length):
        from_len = await load_uvarint(fp)
        raw_from = await fp.read(from_len)
        to_len = await load_uvarint(fp)
        raw_to = await fp.read(to_len)

        assert from_len == to_len
        ip_ranges.append(IPRange.from_packed(raw_from, raw_to))

    return ip_ranges


async def dump_ip_range_list(fp: SupportsAsyncWrite[bytes], items: list[IPRange]):
    await dump_uint(fp, 1)  # version

    await dump_uvarint(fp, len(items))
    for ip_range in items:
        raw_from, raw_to = ip_range.to_packed()

        await dump_uvarint(fp, len(raw_from))
        await fp.write(raw_from)
        await dump_uvarint(fp, len(raw_to))
        await fp.write(raw_to)
