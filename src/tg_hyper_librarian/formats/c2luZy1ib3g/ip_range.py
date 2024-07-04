from ipaddress import IPv4Address, IPv6Address
from typing import Generic, TypeVar

# TODO better generic
TIpAddress = TypeVar("TIpAddress", bound=IPv4Address | IPv6Address)


class IPRange(Generic[TIpAddress]):
    def __init__(self) -> None:
        self.start: TIpAddress
        self.end: TIpAddress

    def __repr__(self) -> str:
        return f"IPRange({self.start}, {self.end})"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, IPRange):
            return False
        return value.start == self.start and value.end == self.end

    def extend(self, value: "IPRange[TIpAddress]"):
        if self.end < (value.start - 1):
            raise ValueError()
        self.end = value.end

    @classmethod
    def from_address(cls, start: TIpAddress, end: TIpAddress):
        ip_range = cls()
        ip_range.start = start
        ip_range.end = end
        return ip_range

    @classmethod
    def from_packed(cls, start: bytes, end: bytes, IpAddress: type[TIpAddress]):
        ip_range = cls()
        ip_range.start = IpAddress(start)
        ip_range.end = IpAddress(end)
        return ip_range

    def to_packed(self):
        return self.start.packed, self.end.packed


class IPv4Range(IPRange[IPv4Address]):
    pass


class IPv6Range(IPRange[IPv6Address]):
    pass
