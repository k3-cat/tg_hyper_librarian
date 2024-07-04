from ipaddress import summarize_address_range
from typing import TYPE_CHECKING, BinaryIO

from ...io.zlib_io import ZlibReaderIO
from ...models import And, Not, Or, RuleSet, RuleUnit, TRule
from ._common import MAGIC, RuleType, read_uint, read_uvarint
from .c2lu import C2lu
from .logical_group import LogicalGroup

if TYPE_CHECKING:
    from . import Tc2lu


def _read_c2lu(sp: BinaryIO) -> "Tc2lu":
    c2lu: "Tc2lu"
    c2lu_type = RuleType(read_uint(sp))
    if c2lu_type == RuleType.REGULAR:
        c2lu = C2lu()
        c2lu.read_from(sp)

    elif c2lu_type == RuleType.LOGIC:
        c2lu = LogicalGroup()
        c2lu.read_from(sp, _read_c2lu)

    else:
        raise ValueError(c2lu_type)

    return c2lu


def load_from_io_full(sp: BinaryIO) -> list["Tc2lu"]:
    magic = sp.read(3)
    if magic != MAGIC:
        raise ValueError("invalid file format")
    _ = sp.read(1)  # version
    with ZlibReaderIO(sp) as zsp:
        length = read_uvarint(zsp)  # type: ignore
        return [_read_c2lu(zsp) for _ in range(length)]  # type: ignore


def _translate_c2lu(c2lu: "Tc2lu") -> TRule:
    result: TRule
    if isinstance(c2lu, C2lu):
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
            domains = c2lu.domains.to_list()
            for domain in domains:
                if not domain.startswith("\r."):
                    continue
                try:
                    domains.remove(domain[2:])
                    result.domain_suffixes.append(domain[2:])
                except ValueError:
                    result.domain_suffixes.append(domain[1:])

        if c2lu.domain_keywords:
            result.domain_keywords = list(c2lu.domain_keywords)

        if c2lu.invert:
            result = Not(result)

    elif isinstance(c2lu, LogicalGroup):
        rules = tuple(_translate_c2lu(rule_unit) for rule_unit in c2lu.c2luZy1)
        if c2lu.mode == LogicalGroup.Mode.AND:
            result = And.from_tuple(rules)
        elif c2lu.mode == LogicalGroup.Mode.OR:
            result = Or.from_tuple(rules)
        else:
            raise ValueError(c2lu.mode)

    return result


def load_from_io(sp: BinaryIO) -> RuleSet:
    c2luZy1 = load_from_io_full(sp)
    rule_set = RuleSet.from_collection(_translate_c2lu(rule) for rule in c2luZy1)
    return rule_set
