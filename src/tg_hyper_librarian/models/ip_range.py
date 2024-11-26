from ipaddress import IPv4Address, IPv6Address, _BaseAddress
from typing import Generic, Type, TypeVar

TIpAddress = TypeVar("TIpAddress", bound=_BaseAddress)


class _BaseIpRange(Generic[TIpAddress]):
    _ip_address_cls: Type[TIpAddress]

    def __init__(self) -> None:
        self.start: TIpAddress
        self.end: TIpAddress

    def __repr__(self) -> str:
        return f"IpRange({self.start}, {self.end})"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, type(self)):
            return False
        return value.start == self.start and value.end == self.end

    @classmethod
    def from_address(cls, start: TIpAddress, end: TIpAddress):
        ip_range = cls()
        ip_range.start = start
        ip_range.end = end
        return ip_range

    @classmethod
    def from_packed(cls, packed: tuple[bytes, bytes]):
        ip_range = cls()
        ip_range.start = cls._ip_address_cls(packed[0])
        ip_range.end = cls._ip_address_cls(packed[1])
        return ip_range

    def to_packed(self) -> tuple[bytes, bytes]:
        return (self.start.packed, self.end.packed)


class IPv4Range(_BaseIpRange[IPv4Address]):
    _ip_address_cls = IPv4Address


class IPv6Range(_BaseIpRange[IPv6Address]):
    _ip_address_cls = IPv6Address


TIpRange = TypeVar("TIpRange", bound=IPv4Range | IPv6Range)
