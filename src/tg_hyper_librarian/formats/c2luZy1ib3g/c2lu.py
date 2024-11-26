from enum import Enum
from typing import BinaryIO

from ...models.ip_range import IPv4Range, IPv6Range
from ._common import read_uint, read_uvarint, read_vstring, write_uint, write_uvarint, write_vstring
from .succinct import Succinct


def _read_uint16_items(sp: BinaryIO) -> list[int]:
    length = read_uvarint(sp)
    values = [read_uint(sp, 2) for _ in range(length)]
    return values


def _read_string_items(sp: BinaryIO) -> list[str]:
    length = read_uvarint(sp)
    strs = [read_vstring(sp) for _ in range(length)]
    return strs


def _read_ip_range_items(sp: BinaryIO) -> tuple[list[IPv4Range], list[IPv6Range]]:
    _ = read_uint(sp)  # version
    length = read_uint(sp, 8)
    ipv4_ranges: list[IPv4Range] = list()
    ipv6_ranges: list[IPv6Range] = list()
    for _ in range(length):
        from_len = read_uvarint(sp)
        raw_from = sp.read(from_len)
        to_len = read_uvarint(sp)
        raw_to = sp.read(to_len)
        if from_len == 4:
            ipv4_ranges.append(IPv4Range.from_packed((raw_from, raw_to)))
        elif from_len == 16:
            ipv6_ranges.append(IPv6Range.from_packed((raw_from, raw_to)))
        else:
            raise ValueError("unsupported len:", from_len)

    return ipv4_ranges, ipv6_ranges


def _write_uint16_items(sp: BinaryIO, items: list[int]):
    write_uvarint(sp, len(items))
    for val in items:
        write_uint(sp, val, 2)


def _write_string_items(sp: BinaryIO, items: list[str]):
    write_uvarint(sp, len(items))
    for val in items:
        write_vstring(sp, val)


def _write_ip_range_items(sp: BinaryIO, items: list[IPv4Range | IPv6Range]):
    write_uint(sp, 1)  # version
    write_uvarint(sp, len(items))
    for ip_range in items:
        raw_from, raw_to = ip_range.to_packed()
        write_uvarint(sp, len(raw_from))
        sp.write(raw_from)
        write_uvarint(sp, len(raw_to))
        sp.write(raw_to)


class C2lu:
    class ItemType(Enum):
        QUERY_TYPE = 0
        NETWORK = 1
        DOMAIN = 2
        DOMAIN_KEYWORD = 3
        DOMAIN_REGEX = 4
        SOURCE_IP_CIDR = 5
        IP_CIDR = 6
        SOURCE_PORT = 7
        SOURCE_PORT_RANGE = 8
        PORT = 9
        PORT_RANGE = 10
        PROCESS_NAME = 11
        PROCESS_PATH = 12
        PACKAGE_NAME = 13
        WIFI_SSID = 14
        WIFI_BSSID = 15
        AdGuard_Domain = 16
        Process_Path_Regex = 17
        Network_Type = 18
        Network_Is_Expensive = 19
        Network_Is_Constrained = 20
        Final = 0xFF

    class NetworkType(Enum):
        WIFI = 0
        Cellular = 1
        Ethernet = 2
        Other = 3

    def __init__(self) -> None:
        self.invert = False

        self.query_types: list[int] | None = None
        self.networks: list[str] | None = None
        self.domains: Succinct | None = None
        self.domain_keywords: list[str] | None = None
        self.domain_regexes: list[str] | None = None
        self.source_ipv4_ranges: list[IPv4Range] = list()
        self.source_ipv6_ranges: list[IPv6Range] = list()
        self.ipv4_ranges: list[IPv4Range] = list()
        self.ipv6_ranges: list[IPv6Range] = list()
        self.source_ports: list[int] | None = None
        self.source_port_ranges: list[str] | None = None
        self.ports: list[int] | None = None
        self.port_ranges: list[str] | None = None
        self.process_names: list[str] | None = None
        self.process_paths: list[str] | None = None
        self.process_path_regexes: list[str] | None = None
        self.package_names: list[str] | None = None
        self.network_type: C2lu.NetworkType | None = None
        self.network_is_expensive: bool = False
        self.network_is_constrained: bool = False
        self.wifi_ssids: list[str] | None = None
        self.wifi_bssids: list[str] | None = None
        self.adguard_domains: Succinct | None = None

    def _read_item(self, sp: BinaryIO) -> bool:
        item_type = C2lu.ItemType(read_uint(sp))
        if item_type == C2lu.ItemType.QUERY_TYPE:
            self.query_types = _read_uint16_items(sp)

        elif item_type == C2lu.ItemType.NETWORK:
            self.networks = _read_string_items(sp)

        elif item_type == C2lu.ItemType.DOMAIN:
            self.domains = Succinct.read_from(sp)

        elif item_type == C2lu.ItemType.DOMAIN_KEYWORD:
            self.domain_keywords = _read_string_items(sp)

        elif item_type == C2lu.ItemType.DOMAIN_REGEX:
            self.domain_regexes = _read_string_items(sp)

        elif item_type == C2lu.ItemType.SOURCE_IP_CIDR:
            self.source_ipv4_ranges, self.source_ipv6_ranges = _read_ip_range_items(sp)

        elif item_type == C2lu.ItemType.IP_CIDR:
            self.ipv4_ranges, self.ipv6_ranges = _read_ip_range_items(sp)

        elif item_type == C2lu.ItemType.SOURCE_PORT:
            self.source_ports = _read_uint16_items(sp)

        elif item_type == C2lu.ItemType.SOURCE_PORT_RANGE:
            self.source_port_ranges = _read_string_items(sp)

        elif item_type == C2lu.ItemType.PORT:
            self.ports = _read_uint16_items(sp)

        elif item_type == C2lu.ItemType.PORT_RANGE:
            self.port_ranges = _read_string_items(sp)

        elif item_type == C2lu.ItemType.PROCESS_NAME:
            self.process_names = _read_string_items(sp)

        elif item_type == C2lu.ItemType.PROCESS_PATH:
            self.process_paths = _read_string_items(sp)

        elif item_type == C2lu.ItemType.Process_Path_Regex:
            self.process_path_regexes = _read_string_items(sp)

        elif item_type == C2lu.ItemType.PACKAGE_NAME:
            self.package_names = _read_string_items(sp)

        elif item_type == C2lu.ItemType.WIFI_SSID:
            self.wifi_ssids = _read_string_items(sp)

        elif item_type == C2lu.ItemType.WIFI_BSSID:
            self.wifi_bssids = _read_string_items(sp)

        elif item_type == C2lu.ItemType.AdGuard_Domain:
            self.adguard_domains = Succinct.read_from(sp)

        elif item_type == C2lu.ItemType.Network_Type:
            self.network_type = C2lu.NetworkType(read_uvarint(sp))

        elif item_type == C2lu.ItemType.Network_Is_Expensive:
            self.network_is_expensive = True

        elif item_type == C2lu.ItemType.Network_Is_Constrained:
            self.network_is_constrained = True

        elif item_type == C2lu.ItemType.Final:
            self.invert = sp.read(1)[0] != 0
            return False

        return True

    @classmethod
    def read_from(cls, sp: BinaryIO):
        flag = True
        c2lu = cls()
        while flag:
            flag = c2lu._read_item(sp)

        return c2lu

    def write_to(self, sp: BinaryIO):
        if self.query_types:
            write_uint(sp, C2lu.ItemType.QUERY_TYPE.value)
            _write_uint16_items(sp, self.query_types)

        if self.networks:
            write_uint(sp, C2lu.ItemType.NETWORK.value)
            _write_string_items(sp, self.networks)

        if self.domains:
            write_uint(sp, C2lu.ItemType.DOMAIN.value)
            self.domains.write_to(sp)

        if self.domain_keywords:
            write_uint(sp, C2lu.ItemType.DOMAIN_KEYWORD.value)
            _write_string_items(sp, self.domain_keywords)

        if self.domain_regexes:
            write_uint(sp, C2lu.ItemType.DOMAIN_REGEX.value)
            _write_string_items(sp, self.domain_regexes)

        if self.source_ipv4_ranges or self.source_ipv6_ranges:
            write_uint(sp, C2lu.ItemType.SOURCE_IP_CIDR.value)
            _write_ip_range_items(sp, [*self.source_ipv4_ranges, *self.source_ipv6_ranges])

        if self.ipv4_ranges or self.ipv6_ranges:
            write_uint(sp, C2lu.ItemType.IP_CIDR.value)
            _write_ip_range_items(sp, [*self.ipv4_ranges, *self.ipv6_ranges])

        if self.source_ports:
            write_uint(sp, C2lu.ItemType.SOURCE_PORT.value)
            _write_uint16_items(sp, self.source_ports)

        if self.source_port_ranges:
            write_uint(sp, C2lu.ItemType.SOURCE_PORT_RANGE.value)
            _write_string_items(sp, self.source_port_ranges)

        if self.ports:
            write_uint(sp, C2lu.ItemType.PORT.value)
            _write_uint16_items(sp, self.ports)

        if self.port_ranges:
            write_uint(sp, C2lu.ItemType.PORT_RANGE.value)
            _write_string_items(sp, self.port_ranges)

        if self.process_names:
            write_uint(sp, C2lu.ItemType.PROCESS_NAME.value)
            _write_string_items(sp, self.process_names)

        if self.process_paths:
            write_uint(sp, C2lu.ItemType.PROCESS_PATH.value)
            _write_string_items(sp, self.process_paths)

        if self.process_path_regexes:
            write_uint(sp, C2lu.ItemType.Process_Path_Regex.value)
            _write_string_items(sp, self.process_path_regexes)

        if self.package_names:
            write_uint(sp, C2lu.ItemType.PACKAGE_NAME.value)
            _write_string_items(sp, self.package_names)

        if self.network_type:
            write_uint(sp, C2lu.ItemType.Network_Type.value)
            write_uvarint(sp, self.network_type.value)

        if self.network_is_expensive:
            write_uint(sp, C2lu.ItemType.Network_Is_Expensive.value)

        if self.network_is_constrained:
            write_uint(sp, C2lu.ItemType.Network_Is_Constrained.value)

        if self.wifi_ssids:
            write_uint(sp, C2lu.ItemType.WIFI_SSID.value)
            _write_string_items(sp, self.wifi_ssids)

        if self.wifi_bssids:
            write_uint(sp, C2lu.ItemType.WIFI_BSSID.value)
            _write_string_items(sp, self.wifi_bssids)

        if self.adguard_domains:
            write_uint(sp, C2lu.ItemType.AdGuard_Domain.value)
            self.adguard_domains.write_to(sp)

        write_uint(sp, C2lu.ItemType.Final.value)
        write_uint(sp, 0x01 if self.invert else 0x00)
