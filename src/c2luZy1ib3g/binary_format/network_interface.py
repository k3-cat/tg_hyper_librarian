from typing import TYPE_CHECKING

from c2luZy1ib3g.binary_format.enum_like_types import load_network_type
from c2luZy1ib3g.serdes import (
    dump_ip_cidr_list,
    dump_uint,
    dump_uvarint,
    load_ip_cidr_list,
    load_uvarint,
)

if TYPE_CHECKING:
    from c2luZy1ib3g.models import SimpleC2lu
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite
    from tg_ip import IPCidrList


async def load_network_interfaces(fp: SupportsAsyncRead[bytes]):
    length = await load_uvarint(fp)
    network_interfaces = dict[SimpleC2lu.NetworkType, IPCidrList]()
    for _ in range(length):
        key = await load_network_type(fp)
        network_interfaces[key] = await load_ip_cidr_list(fp)

    return network_interfaces


async def dump_network_interfaces(
    fp: SupportsAsyncWrite[bytes], field_val: dict[SimpleC2lu.NetworkType, IPCidrList]
):
    await dump_uvarint(fp, len(field_val))
    for network_type, ip_cidrs in field_val.items():
        await dump_uint(fp, network_type)

        await dump_ip_cidr_list(fp, ip_cidrs)
