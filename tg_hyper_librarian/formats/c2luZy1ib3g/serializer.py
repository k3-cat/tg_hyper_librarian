import zlib
from io import BytesIO, IOBase
from ipaddress import IPv4Network, IPv6Network, collapse_addresses
from typing import TYPE_CHECKING, TypeVar

from ...models import And, Group, Not, Or, RuleUnit, TRule
from ._common import MAGIC, RuleType, write_uvarint
from .ip_range import IPv4Range, IPv6Range
from .logical_rule import LogicalRule
from .regular_rule import RegularRule
from .succinct import Succinct

if TYPE_CHECKING:
    from . import Tc2lu


def _write_c2lu(s: IOBase, c2lu: "Tc2lu"):
    if isinstance(c2lu, RegularRule):
        s.write(RuleType.REGULAR.value)
        c2lu.write_to(s)

    elif isinstance(c2lu, LogicalRule):
        s.write(RuleType.LOGIC.value)
        c2lu.write_to(s, _write_c2lu)

    else:
        raise ValueError(c2lu)


def write_to_c2luZy1ib3g_full(s: IOBase, c2luZy1: list["Tc2lu"]):
    # TODO stream io
    b = BytesIO()
    write_uvarint(b, len(c2luZy1))
    for c2lu in c2luZy1:
        _write_c2lu(b, c2lu)

    b.seek(0)
    s.write(MAGIC)
    s.write(b"\x01")  # version
    compressed_raw = zlib.compress(b.read())
    s.write(compressed_raw)


# TODO better generic
TIpRange = TypeVar("TIpRange", bound=IPv4Range | IPv6Range)
TIpNetwork = TypeVar("TIpNetwork", bound=IPv4Network | IPv6Network)


def _translate_cidr(cidrs: list[TIpNetwork], IpRange: type[TIpRange]) -> list[TIpRange]:
    partial = list()
    for cidr in collapse_addresses(cidrs):
        partial.append(cidr[0])
        partial.append(cidr[-1])

    result = list()
    first = None
    last = None
    for i in range(len(partial)):
        if not first:
            first = partial[i]

        elif not last:
            last = partial[i]

        elif partial[i] == last:
            last = None

        else:
            result.append(IpRange.from_address(first, last))
            first = None
            last = None

        i += 1

    return result


MODE_MAP = {
    And: LogicalRule.Mode.AND,
    Or: LogicalRule.Mode.OR,
}


def _translate_rule(rule: TRule) -> "Tc2lu":
    result: "Tc2lu"
    if isinstance(rule, RuleUnit | Not):
        result = RegularRule()
        if isinstance(rule, Not):
            rule = rule.unit
            result.invert = True

        if rule.ipv4_cidrs:
            result.ipv4_ranges = _translate_cidr(rule.ipv4_cidrs, IPv4Range)
        if rule.ipv6_cidrs:
            result.ipv6_ranges = _translate_cidr(rule.ipv6_cidrs, IPv6Range)
        if rule.domains:
            result.domains = Succinct.from_collection(rule.domains)
        if rule.domain_keywords:
            result.domain_keywords = list(rule.domain_keywords)

    elif isinstance(rule, And | Or):
        result = LogicalRule()
        result.mode = MODE_MAP[type(rule)]
        result.c2luZy1 = [_translate_rule(rule_unit) for rule_unit in rule]

    return result


def write_to_c2luZy1ib3g(s: IOBase, group: Group):
    c2luZy1 = [_translate_rule(rule) for rule in group.rules]
    write_to_c2luZy1ib3g_full(s, c2luZy1)
