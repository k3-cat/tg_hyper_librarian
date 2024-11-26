from collections import UserList
from ipaddress import IPv4Network, IPv6Network, _BaseNetwork, collapse_addresses, summarize_address_range
from typing import Generic, TypeVar

from .ip_range import IPv4Range, IPv6Range, TIpRange

TIpNetwork = TypeVar("TIpNetwork", bound=_BaseNetwork)


class BaseIpNetworkList(UserList[TIpNetwork], Generic[TIpNetwork, TIpRange]):
    _ip_range_cls: TIpRange

    @classmethod
    def from_ip_ranges(cls, ip_ranges: list[TIpRange]):
        cidrs: list[TIpNetwork] = list(
            cidr
            for ip_range in ip_ranges
            for cidr in summarize_address_range(ip_range.start, ip_range.end)  # type: ignore
        )
        return cls(collapse_addresses(cidrs))  # type: ignore

    def to_ip_range(self):
        result: list[TIpRange] = list()
        cidrs: list[TIpNetwork] = list(collapse_addresses(self))  # type: ignore
        start_addr = cidrs[0][0]
        for i in range(len(cidrs) - 1):
            if cidrs[i][-1] + 1 == cidrs[i + 1][0]:
                continue
            result.append(self._ip_range_cls.from_address(start_addr, cidrs[i][-1]))
            start_addr = cidrs[i + 1][0]

        result.append(self._ip_range_cls.from_address(start_addr, cidrs[-1][-1]))

        return result


class IPv4NetworkList(BaseIpNetworkList[IPv4Network, IPv4Range]):
    _ip_range_cls = IPv4Range  # type: ignore


class IPv6NetworkList(BaseIpNetworkList[IPv6Network, IPv6Range]):
    _ip_range_cls = IPv6Range  # type: ignore
