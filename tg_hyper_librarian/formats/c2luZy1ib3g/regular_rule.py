from enum import Enum
from io import IOBase
from ipaddress import IPv4Address, IPv6Address

from ._common import read_uint, read_uvarint, read_vstring, write_uint, write_uvarint, write_vstring
from .ip_range import IPRange, IPv4Range, IPv6Range
from .succinct import Succinct


class RegularRule:
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
        Final = 0xFF

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
        self.package_names: list[str] | None = None
        self.wifi_ssids: list[str] | None = None
        self.wifi_bssids: list[str] | None = None

    @staticmethod
    def _read_uint16_item(s: IOBase) -> list[int]:
        length = read_uvarint(s)
        values = [read_uint(s, 2) for _ in range(length)]
        return values

    @staticmethod
    def _read_string_item(s: IOBase) -> list[str]:
        length = read_uvarint(s)
        strs = [read_vstring(s) for _ in range(length)]
        return strs

    @staticmethod
    def _read_ip_range_item(s: IOBase) -> tuple[list[IPv4Range], list[IPv6Range]]:
        _ = read_uint(s)  # version
        length = read_uint(s, 8)
        ipv4_ranges: list[IPv4Range] = list()
        ipv6_ranges: list[IPv6Range] = list()
        for _ in range(length):
            from_len = read_uvarint(s)
            raw_from = s.read(from_len)
            to_len = read_uvarint(s)
            raw_to = s.read(to_len)
            if from_len == 4:
                ipv4_ranges.append(IPv4Range.from_packed(raw_from, raw_to, IPv4Address))
            elif from_len == 16:
                ipv6_ranges.append(IPv6Range.from_packed(raw_from, raw_to, IPv6Address))
            else:
                raise ValueError("unsupported len:", from_len)

        return ipv4_ranges, ipv6_ranges

    def _read_item(self, s: IOBase) -> bool:
        item_type = RegularRule.ItemType(read_uint(s))
        if item_type == RegularRule.ItemType.QUERY_TYPE:
            self.query_types = self._read_uint16_item(s)

        elif item_type == RegularRule.ItemType.NETWORK:
            self.networks = self._read_string_item(s)

        elif item_type == RegularRule.ItemType.DOMAIN:
            self.domains = Succinct.read_from(s)

        elif item_type == RegularRule.ItemType.DOMAIN_KEYWORD:
            self.domain_keywords = self._read_string_item(s)

        elif item_type == RegularRule.ItemType.DOMAIN_REGEX:
            self.domain_regexes = self._read_string_item(s)

        elif item_type == RegularRule.ItemType.SOURCE_IP_CIDR:
            self.source_ipv4_ranges, self.source_ipv6_ranges = self._read_ip_range_item(s)

        elif item_type == RegularRule.ItemType.IP_CIDR:
            self.ipv4_ranges, self.ipv6_ranges = self._read_ip_range_item(s)

        elif item_type == RegularRule.ItemType.SOURCE_PORT:
            self.source_ports = self._read_uint16_item(s)

        elif item_type == RegularRule.ItemType.SOURCE_PORT_RANGE:
            self.source_port_ranges = self._read_string_item(s)

        elif item_type == RegularRule.ItemType.PORT:
            self.ports = self._read_uint16_item(s)

        elif item_type == RegularRule.ItemType.PORT_RANGE:
            self.port_ranges = self._read_string_item(s)

        elif item_type == RegularRule.ItemType.PROCESS_NAME:
            self.process_names = self._read_string_item(s)

        elif item_type == RegularRule.ItemType.PROCESS_PATH:
            self.process_paths = self._read_string_item(s)

        elif item_type == RegularRule.ItemType.PACKAGE_NAME:
            self.package_names = self._read_string_item(s)

        elif item_type == RegularRule.ItemType.WIFI_SSID:
            self.wifi_ssids = self._read_string_item(s)

        elif item_type == RegularRule.ItemType.WIFI_BSSID:
            self.wifi_bssids = self._read_string_item(s)

        elif item_type == RegularRule.ItemType.Final:
            self.invert = s.read(1)[0] != 0
            return False

        return True

    @classmethod
    def read_from(cls, s: IOBase):
        flag = True
        c2lu = cls()
        while flag:
            flag = c2lu._read_item(s)

        return c2lu

    @staticmethod
    def _write_uint16_item(s: IOBase, item: list[int]):
        write_uvarint(s, len(item))
        for val in item:
            write_uint(s, val, 2)

    @staticmethod
    def _write_string_item(s: IOBase, item: list[str]):
        write_uvarint(s, len(item))
        for val in item:
            write_vstring(s, val)

    @staticmethod
    def _write_ip_range_item(s: IOBase, item: list[IPRange]):
        write_uint(s, 1)  # version
        write_uvarint(s, len(item))
        for ip_range in item:
            raw_from, raw_to = ip_range.to_packed()
            write_uvarint(s, len(raw_from))
            s.write(raw_from)
            write_uvarint(s, len(raw_to))
            s.write(raw_to)

    def write_to(self, s: IOBase):
        if self.query_types:
            write_uint(s, RegularRule.ItemType.QUERY_TYPE.value)
            self._write_uint16_item(s, self.query_types)

        if self.networks:
            write_uint(s, RegularRule.ItemType.NETWORK.value)
            self._write_string_item(s, self.networks)

        if self.domains:
            write_uint(s, RegularRule.ItemType.DOMAIN.value)
            self.domains.write_to(s)

        if self.domain_keywords:
            write_uint(s, RegularRule.ItemType.DOMAIN_KEYWORD.value)
            self._write_string_item(s, self.domain_keywords)

        if self.domain_regexes:
            write_uint(s, RegularRule.ItemType.DOMAIN_REGEX.value)
            self._write_string_item(s, self.domain_regexes)

        if self.source_ipv4_ranges or self.source_ipv6_ranges:
            write_uint(s, RegularRule.ItemType.SOURCE_IP_CIDR.value)
            self._write_ip_range_item(s, [*self.source_ipv4_ranges, *self.source_ipv6_ranges])

        if self.ipv4_ranges or self.ipv6_ranges:
            write_uint(s, RegularRule.ItemType.IP_CIDR.value)
            self._write_ip_range_item(s, [*self.ipv4_ranges, *self.ipv6_ranges])

        if self.source_ports:
            write_uint(s, RegularRule.ItemType.SOURCE_PORT.value)
            self._write_uint16_item(s, self.source_ports)

        if self.source_port_ranges:
            write_uint(s, RegularRule.ItemType.SOURCE_PORT_RANGE.value)
            self._write_string_item(s, self.source_port_ranges)

        if self.ports:
            write_uint(s, RegularRule.ItemType.PORT.value)
            self._write_uint16_item(s, self.ports)

        if self.port_ranges:
            write_uint(s, RegularRule.ItemType.PORT_RANGE.value)
            self._write_string_item(s, self.port_ranges)

        if self.process_names:
            write_uint(s, RegularRule.ItemType.PROCESS_NAME.value)
            self._write_string_item(s, self.process_names)

        if self.process_paths:
            write_uint(s, RegularRule.ItemType.PROCESS_PATH.value)
            self._write_string_item(s, self.process_paths)

        if self.package_names:
            write_uint(s, RegularRule.ItemType.PACKAGE_NAME.value)
            self._write_string_item(s, self.package_names)

        if self.wifi_ssids:
            write_uint(s, RegularRule.ItemType.WIFI_SSID.value)
            self._write_string_item(s, self.wifi_ssids)

        if self.wifi_bssids:
            write_uint(s, RegularRule.ItemType.WIFI_BSSID.value)
            self._write_string_item(s, self.wifi_bssids)

        write_uint(s, RegularRule.ItemType.Final.value)
        s.write(0x01 if self.invert else 0x00)
