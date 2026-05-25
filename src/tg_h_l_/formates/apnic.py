import math
from typing import TYPE_CHECKING

from tg_h_l_.dto import RulePack, SimpleRule
from tg_h_l_.formates._base import ReadableFormat
from tg_ip import IPv4Network, IPv6Network

if TYPE_CHECKING:
    from tg_aio._buffered_base import AsyncBufferedReader


class APNIC(ReadableFormat[str]):
    def __int__(self, country_codes: frozenset[str]) -> None:
        super().__init__()

        self.targets = country_codes

    async def load(self, fp: "AsyncBufferedReader[str]"):
        rule = SimpleRule()

        result = RulePack(rules=[rule])
        result.freeze()

        async for line in fp.readlines():
            if line.startswith("#"):
                continue

            line_info = line.split("|")
            if len(line_info) < 5 or line_info[1] not in self.targets:
                continue

            if line_info[2] == "ipv4":
                rule.ipv4_cidrs.append(
                    IPv4Network(f"{line_info[3]}/{32 - int(math.log2(int(line_info[4])))}")
                )

            elif line_info[2] == "ipv6":
                rule.ipv6_cidrs.append(IPv6Network(f"{line_info[3]}/{line_info[4]}"))

            else:
                # asn
                pass

        rule.freeze()

        yield result
