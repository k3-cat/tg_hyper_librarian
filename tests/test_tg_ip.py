import random
from typing import TYPE_CHECKING

import pytest

from tg_ip import IPRange, IPv4Address, IPv4Network

if TYPE_CHECKING:
    from tg_ip import V4, IPNetwork

TEST_DATA = [
    (
        [
            IPv4Network("10.0.0.1/32"),
            IPv4Network("10.0.0.2/31"),
            IPv4Network("10.0.0.4/30"),
            IPv4Network("10.0.0.8/29"),
            IPv4Network("10.0.0.16/28"),
            IPv4Network("10.0.0.32/27"),
            IPv4Network("10.0.0.64/26"),
            IPv4Network("10.0.0.128/25"),
            IPv4Network("10.0.1.0/24"),
            IPv4Network("10.0.2.0/23"),
            IPv4Network("10.0.4.0/22"),
            IPv4Network("10.0.8.0/21"),
            IPv4Network("10.0.16.0/20"),
            IPv4Network("10.0.32.0/19"),
            IPv4Network("10.0.64.0/18"),
            IPv4Network("10.0.128.0/17"),
            IPv4Network("10.1.0.0/16"),
            IPv4Network("10.2.0.0/15"),
            IPv4Network("10.4.0.0/14"),
            IPv4Network("10.8.0.0/13"),
            IPv4Network("10.16.0.0/16"),
            IPv4Network("10.17.0.0/24"),
        ],
        [
            IPRange.from_address(IPv4Address("10.0.0.1"), IPv4Address("10.17.0.255")),
        ],
    ),
    (
        [
            IPv4Network("10.0.0.0/20"),
            IPv4Network("10.0.16.0/21"),
            IPv4Network("10.0.24.0/24"),
            IPv4Network("192.168.1.0/24"),
            IPv4Network("192.168.2.0/24"),
            IPv4Network("192.168.3.0/32"),
        ],
        [
            IPRange.from_address(IPv4Address("10.0.0.0"), IPv4Address("10.0.24.255")),
            IPRange.from_address(IPv4Address("192.168.1.0"), IPv4Address("192.168.3.0")),
        ],
    ),
]


@pytest.mark.parametrize("ip_cidrs, ip_ranges", TEST_DATA)
class TestCidrTranslation:
    def test_ip_range_to_cidr(self, ip_cidrs: list[IPNetwork[V4]], ip_ranges: list[IPRange[V4]]):
        ip_cidrs_ = ip_cidrs.copy()
        random.shuffle(ip_cidrs_)

        assert list(IPRange.from_ip_cidrs(ip_cidrs_)) == ip_ranges

    def test_cidr_to_ip_range(self, ip_cidrs: list[IPNetwork[V4]], ip_ranges: list[IPRange[V4]]):
        assert ip_cidrs == list(
            ip_cidr for ip_range_ in ip_ranges for ip_cidr in ip_range_.to_ip_cidrs()
        )
