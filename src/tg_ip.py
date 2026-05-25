import ipaddress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, Self

if TYPE_CHECKING:
    from typing import Generator, Iterable, Iterator, Literal, TypeAlias


class V4(Protocol):
    pass


class V6(Protocol):
    pass


class IP[T: V4 | V6](Protocol):
    version: Literal[4, 6]

    def __lt__(self, other: Self, /) -> bool: ...
    def __gt__(self, other: Self, /) -> bool: ...


class IPAddress[T: V4 | V6](IP[T], Protocol):
    @property
    def packed(self) -> bytes: ...

    def __add__(self, other: int, /) -> Self: ...
    def __sub__(self, other: int, /) -> Self: ...


class IPNetwork[T: V4 | V6](IP[T], Protocol):
    def __contains__(self, val: IPAddress[T], /) -> bool: ...
    def __getitem__(self, key: int, /) -> IPAddress[T]: ...


class IPv4Address(ipaddress.IPv4Address, IPAddress[V4]):
    pass


class IPv6Address(ipaddress.IPv6Address, IPAddress[V6]):
    pass


class IPv4Network(ipaddress.IPv4Network, IPNetwork[V4]):
    pass


class IPv6Network(ipaddress.IPv6Network, IPNetwork[V6]):
    pass


def ip_address(address: int | bytes | str | IPv4Address | IPv6Address) -> IPAddress:
    return ipaddress.ip_address(address)  # pyright: ignore[reportReturnType]


def ip_network[T: V4 | V6](
    address: int
    | str
    | bytes
    | IPAddress[T]
    | IPNetwork[T]
    | tuple[IPAddress[T]]
    | tuple[IPAddress[T], int],
    strict=True,
) -> IPNetwork[T]:
    return ipaddress.ip_network(address, strict)  # pyright: ignore[reportArgumentType, reportReturnType]


def summarize_address_range[T: V4 | V6](
    first: IPAddress[T], last: IPAddress[T]
) -> Iterator[IPNetwork[T]]:
    return ipaddress.summarize_address_range(first, last)  # pyright: ignore[reportCallIssue, reportArgumentType]


def collapse_addresses[T: IPNetwork](addresses: Iterable[T]) -> Iterator[T]:
    return ipaddress.collapse_addresses(addresses)  # pyright: ignore[reportArgumentType]


@dataclass(frozen=True, kw_only=True)
class IPRange[T: V4 | V6]:
    start: IPAddress[T]
    end: IPAddress[T]

    def __repr__(self) -> str:
        return f"IpRange({self.start}, {self.end})"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, type(self)):
            return False

        return value.start == self.start and value.end == self.end

    @property
    def version(self):
        return self.start.version

    @classmethod
    def from_address(cls, start: IPAddress[T], end: IPAddress[T]):
        return cls(start=start, end=end)

    @classmethod
    def from_packed(cls, raw_from: bytes, raw_to: bytes):
        return cls(start=ip_address(raw_from), end=ip_address(raw_to))

    def to_packed(self) -> tuple[bytes, bytes]:
        return self.start.packed, self.end.packed

    def to_ip_cidrs(self) -> Generator[IPNetwork[T]]:
        yield from summarize_address_range(self.start, self.end)

    @classmethod
    def from_ip_cidrs(cls, ip_cidrs: Iterable[IPNetwork[T]]):
        itor = iter(sorted(ip_cidrs))
        priv_cidr = next(itor)

        start_addr = priv_cidr[0]
        try:
            while True:
                next_cidr = next(itor)
                if priv_cidr[-1] + 1 == next_cidr[0]:
                    priv_cidr = next_cidr

                    continue

                yield cls.from_address(start_addr, priv_cidr[-1])

                start_addr = next_cidr[0]
                priv_cidr = next_cidr

        except StopIteration:
            pass

        yield cls.from_address(start_addr, priv_cidr[-1])


if TYPE_CHECKING:
    IPCidrList: TypeAlias = list[IPNetwork[V4] | IPNetwork[V6]]

    IPv4Range: TypeAlias = IPRange[V4]
    IPv6Range: TypeAlias = IPRange[V6]
