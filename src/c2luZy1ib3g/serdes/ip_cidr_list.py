from itertools import chain
from typing import TYPE_CHECKING, cast

from c2luZy1ib3g.serdes.ip_range_list import dump_ip_range_list, load_ip_range_list
from tg_ip import IPRange

if TYPE_CHECKING:
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite
    from tg_ip import V4, V6, IPCidrList, IPNetwork


async def load_ip_cidr_list(fp: SupportsAsyncRead[bytes]):
    ip_ranges = await load_ip_range_list(fp)
    ip_cidrs = [
        ip_cidr for ip_range_ in ip_ranges for ip_cidr in ip_range_.to_ip_cidrs()
    ]

    return ip_cidrs


async def dump_ip_cidr_list(fp: SupportsAsyncWrite[bytes], ip_cidrs: IPCidrList):
    ipv4_cidrs = list[IPNetwork[V4]]()
    ipv6_cidrs = list[IPNetwork[V6]]()
    for ip_cidr in ip_cidrs:
        if ip_cidr.version == 4:
            ipv4_cidrs.append(cast("IPNetwork[V4]", ip_cidr))

        elif ip_cidr.version == 6:
            ipv6_cidrs.append(cast("IPNetwork[V6]", ip_cidr))

    return await dump_ip_range_list(fp, list(chain(
        IPRange[V4].from_ip_cidrs(ipv4_cidrs),
        IPRange[V6].from_ip_cidrs(ipv6_cidrs),
    )))  # fmt: off
