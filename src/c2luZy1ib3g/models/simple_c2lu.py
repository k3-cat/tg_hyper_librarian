import enum
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import tg_utils as u
from tg_utils import PatchedDto

if TYPE_CHECKING:
    from succinct import Succinct
    from tg_ip import IPCidrList

C2LU_ITEMTYPE_ANNO = "item_type"


class _ItemType(enum.IntEnum):
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
    ADGUARD_DOMAIN = 16
    PROCESS_PATH_REGEX = 17
    NETWORK_TYPE = 18
    NETWORK_IS_EXPENSIVE = 19
    NETWORK_IS_CONSTRAINED = 20
    NETWORK_INTERFACE_ADDRESS = 21
    DEFAULT_INTERFACE_ADDRESS = 22
    PACKAGE_NAME_REGEX = 23
    FINAL = 0xFF


@dataclass(frozen=True, kw_only=True)
class SimpleC2lu(PatchedDto):
    ItemType = _ItemType

    class NetworkType(enum.IntEnum):
        WIFI = 0
        Cellular = 1
        Ethernet = 2
        Other = 3

    query_type: list[int] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.QUERY_TYPE},
    )
    network: list[str] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.NETWORK},
    )
    domains: Succinct | None = field(
        default=None,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.DOMAIN},
    )
    domain_keyword: list[str] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.DOMAIN_KEYWORD},
    )
    domain_regex: list[str] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.DOMAIN_REGEX},
    )
    source_ip_cidr: IPCidrList = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.SOURCE_IP_CIDR},
    )
    ip_cidrs: IPCidrList = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.IP_CIDR},
    )
    source_port: list[int] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.SOURCE_PORT},
    )
    source_port_range: list[str] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.SOURCE_PORT_RANGE},
    )
    port: list[int] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.PORT},
    )
    port_range: list[str] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.PORT_RANGE},
    )
    process_name: list[str] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.PROCESS_NAME},
    )
    process_path: list[str] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.PROCESS_PATH},
    )
    package_name: list[str] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.PACKAGE_NAME},
    )
    wifi_ssid: list[str] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.WIFI_SSID},
    )
    wifi_bssid: list[str] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.WIFI_BSSID},
    )
    adguard_domain: Succinct | None = field(
        default=None,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.ADGUARD_DOMAIN},
    )
    process_path_regex: list[str] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.PROCESS_PATH_REGEX},
    )
    network_type: SimpleC2lu.NetworkType | None = field(
        default=None,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.NETWORK_TYPE},
    )
    network_is_expensive: bool = field(
        default=False,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.NETWORK_IS_EXPENSIVE},
    )
    network_is_constrained: bool = field(
        default=False,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.NETWORK_IS_CONSTRAINED},
    )
    network_interface_address: "dict[SimpleC2lu.NetworkType, IPCidrList]" = field(
        default_factory=dict,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.NETWORK_INTERFACE_ADDRESS},
    )
    default_interface_address: IPCidrList = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.DEFAULT_INTERFACE_ADDRESS},
    )
    package_name_regex: list[str] = field(
        default_factory=list,
        metadata={C2LU_ITEMTYPE_ANNO: _ItemType.PACKAGE_NAME_REGEX},
    )
    is_inverted: bool = False


SIMPLE_C2LU_TYPE_I_FIELDS = frozenset[str]((
    u.name(SimpleC2lu.is_inverted),
))  # fmt: off

SIMPLE_C2LU_TYPE_II_FIELDS = frozenset[str]((
    u.name(SimpleC2lu.domains),
    u.name(SimpleC2lu.ip_cidrs),
    u.name(SimpleC2lu.is_inverted),
))  # fmt: off
