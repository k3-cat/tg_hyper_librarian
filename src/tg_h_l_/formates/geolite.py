import enum
from typing import TYPE_CHECKING, cast

import aiocsv
import asyncstdlib as a

from tg_h_l_.dto import RulePack, SimpleRule
from tg_h_l_.formates._base import ReadableFormat
from tg_ip import ip_network

if TYPE_CHECKING:
    from tg_aio._buffered_base import AsyncBufferedReader
    from tg_ip import IPNetwork, IPv4Network, IPv6Network


class GeonameId(enum.IntEnum):
    CN = 1814991
    HK = 1819730


__GEOLITE_CSV_FIELDS = (
    "network",
    "geoname_id",
    "registered_country_geoname_id",
    "represented_country_geoname_id",
    "is_anonymous_proxy",
    "is_satellite_provider",
    "is_anycast",
)


class Geolite(ReadableFormat[str]):
    def __int__(self, target_geoname_ids: frozenset[GeonameId]) -> None:
        super().__init__()

        self.targets = target_geoname_ids

    async def load(self, fp: AsyncBufferedReader[str]):
        ip_cidrs = list[IPNetwork]()
        csv_reader = aiocsv.AsyncDictReader(fp, __GEOLITE_CSV_FIELDS)
        async for row in a.filter(lambda row: row["geoname_id"] in self.targets, csv_reader):
            ip_cidrs.append(ip_network(row["network"]))

        if ip_cidrs and ip_cidrs[0].version == 4:
            rule = SimpleRule(ipv4_cidrs=cast("list[IPv4Network]", ip_cidrs))

        else:
            rule = SimpleRule(ipv6_cidrs=cast("list[IPv6Network]", ip_cidrs))

        rule.freeze()

        result = RulePack(rules=[rule])
        result.freeze()

        yield result
