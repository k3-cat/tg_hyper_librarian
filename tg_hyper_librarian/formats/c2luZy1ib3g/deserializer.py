import zlib
from io import BytesIO, IOBase
from ipaddress import summarize_address_range
from typing import TYPE_CHECKING

from ...models import And, Group, Not, Or, RuleUnit, TRule
from ._common import MAGIC, RuleType, read_uint, read_uvarint
from .logical_rule import LogicalRule
from .regular_rule import RegularRule

if TYPE_CHECKING:
    from . import Tc2lu


def _read_c2lu(s: IOBase) -> "Tc2lu":
    c2lu: "Tc2lu"
    c2lu_type = RuleType(read_uint(s))
    if c2lu_type == RuleType.REGULAR:
        c2lu = RegularRule()
        c2lu.read_from(s)

    elif c2lu_type == RuleType.LOGIC:
        c2lu = LogicalRule()
        c2lu.read_from(s, _read_c2lu)

    else:
        raise ValueError(c2lu_type)

    return c2lu


def load_from_c2luZy1ib3g_full(s: IOBase) -> list["Tc2lu"]:
    # TODO stream io
    magic = s.read(3)
    if magic != MAGIC:
        raise ValueError("invalid file format")
    _ = s.read(1)  # version
    uncompressed_raw = zlib.decompress(s.read())
    s = BytesIO(uncompressed_raw)
    length = read_uvarint(s)
    return [_read_c2lu(s) for _ in range(length)]


def _translate_c2lu(c2lu: "Tc2lu") -> TRule:
    result: TRule
    if isinstance(c2lu, RegularRule):
        result = RuleUnit()
        if c2lu.ipv4_ranges:
            result.ipv4_cidrs = list(
                cidr for ip_range in c2lu.ipv4_ranges for cidr in summarize_address_range(ip_range.start, ip_range.end)
            )
        if c2lu.ipv6_ranges:
            result.ipv6_cidrs = list(
                cidr for ip_range in c2lu.ipv6_ranges for cidr in summarize_address_range(ip_range.start, ip_range.end)
            )
        if c2lu.domains:
            result.domains = c2lu.domains.to_list()
        if c2lu.domain_keywords:
            result.domain_keywords = list(c2lu.domain_keywords)

        if c2lu.invert:
            result = Not(result)

    elif isinstance(c2lu, LogicalRule):
        rules = tuple(_translate_c2lu(rule_unit) for rule_unit in c2lu.c2luZy1)
        if c2lu.mode == LogicalRule.Mode.AND:
            result = And.from_tuple(rules)
        elif c2lu.mode == LogicalRule.Mode.OR:
            result = Or.from_tuple(rules)
        else:
            raise ValueError(c2lu.mode)

    return result


def load_from_c2luZy1ib3g(s: IOBase) -> Group:
    c2luZy1 = load_from_c2luZy1ib3g_full(s)
    rule_set = Group.from_tuple(tuple(_translate_c2lu(rule) for rule in c2luZy1))
    return rule_set
