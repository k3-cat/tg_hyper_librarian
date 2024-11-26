from typing import BinaryIO

from ...io import ZlibWriterIO
from ...models.complex_rule import And, Not, Or, RuleUnit, TRule
from ...models.rule_set import RuleSet
from ._common import MAGIC, RuleType, write_uint, write_uvarint
from .c2lu import C2lu
from .complex_c2lu import LogicalGroup, Tc2lu
from .succinct import Succinct


def _write_c2lu(sp: BinaryIO, c2lu: Tc2lu):
    if isinstance(c2lu, C2lu):
        write_uint(sp, RuleType.REGULAR.value)
        c2lu.write_to(sp)

    elif isinstance(c2lu, LogicalGroup):
        write_uint(sp, RuleType.LOGIC.value)
        c2lu.write_to(sp, _write_c2lu)

    else:
        raise ValueError(c2lu)


def write_to_io_full(sp: BinaryIO, c2luZy1: list[Tc2lu]):
    sp.write(MAGIC)
    sp.write(b"\x03")  # version
    with ZlibWriterIO(sp) as zsp:
        write_uvarint(zsp, len(c2luZy1))  # type: ignore
        for c2lu in c2luZy1:
            _write_c2lu(zsp, c2lu)  # type: ignore


MODE_MAP = {
    And: LogicalGroup.Mode.AND,
    Or: LogicalGroup.Mode.OR,
}


def _translate_rule(rule: TRule) -> Tc2lu:
    result: Tc2lu
    if isinstance(rule, RuleUnit | Not):
        result = C2lu()
        if isinstance(rule, Not):
            rule = rule.unit
            result.invert = True

        if rule.ipv4_cidrs:
            result.ipv4_ranges = rule.ipv4_cidrs.to_ip_range()
        if rule.ipv6_cidrs:
            result.ipv6_ranges = rule.ipv6_cidrs.to_ip_range()
        if rule.domains:
            domains = rule.domains.copy()
            for suffix in rule.domain_suffixes:
                if suffix[0] == ".":
                    domains.append(f"\r{suffix}")
                else:
                    domains.append(suffix)
                    domains.append(f"\r.{suffix}")
            result.domains = Succinct.from_list(domains)
        if rule.domain_keywords:
            result.domain_keywords = list(rule.domain_keywords)

    elif isinstance(rule, And | Or):
        result = LogicalGroup()
        result.mode = MODE_MAP[type(rule)]
        result.c2luZy1 = [_translate_rule(rule_unit) for rule_unit in rule]

    return result


def write_to_io(sp: BinaryIO, rule_set: RuleSet):
    c2luZy1 = [_translate_rule(rule) for rule in rule_set]
    write_to_io_full(sp, c2luZy1)
