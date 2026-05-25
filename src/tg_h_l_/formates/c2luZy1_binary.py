from dataclasses import asdict, fields
from itertools import chain
from typing import TYPE_CHECKING, cast

import tg_utils as u
from c2luZy1ib3g.binary_format import dump_c2luZy1, load_c2luZy1
from c2luZy1ib3g.models import SIMPLE_C2LU_TYPE_II_FIELDS, LogicalC2lu, SimpleC2lu
from succinct import Succinct
from tg_h_l_.dto import SIMPLE_RULE_TYPE_II_FIELDS, RulePack, SimpleRule
from tg_h_l_.formates._base import RWFormat
from tg_h_l_.formates.c2luZy1_source import _JSON_AUTO_FIELDS, _LOGIC_MODE_CLS_MAP, FieldName

if TYPE_CHECKING:
    from typing import Any

    from c2luZy1ib3g.models import C2luZy1
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite
    from tg_h_l_.dto import LogicalRule
    from tg_ip import IPv4Network, IPv6Network


_SOURCE_AUTO_FIELDS = _JSON_AUTO_FIELDS - SIMPLE_RULE_TYPE_II_FIELDS
_BINARY_AUTO_FIELDS = (
    frozenset(field.name for field in fields(SimpleC2lu)) - SIMPLE_C2LU_TYPE_II_FIELDS
)
__UNSUPPORTED_FIELDS = _BINARY_AUTO_FIELDS - _SOURCE_AUTO_FIELDS
__AUTO_FIELDS = _SOURCE_AUTO_FIELDS & _BINARY_AUTO_FIELDS


__CLS_LOGICAL_MODE_MAP = {v: k for k, v in _LOGIC_MODE_CLS_MAP.items()}


def _translate_c2lu(c2luZ: SimpleC2lu | LogicalC2lu):
    if isinstance(c2luZ, LogicalC2lu):
        rulepack = _LOGIC_MODE_CLS_MAP[c2luZ.mode].from_items(
            _translate_c2lu(inner_c2lu) for inner_c2lu in c2luZ.c2luZ
        )

        return rulepack

    for field_name in __UNSUPPORTED_FIELDS:
        if c2luZ.__getattribute__(field_name):
            return asdict(c2luZ)

    rule = SimpleRule(is_inverted=c2luZ.is_inverted)

    if c2luZ.domains:
        domains = list[str](c2luZ.domains.keys())
        for domain in domains:
            if not domain.startswith("\r."):
                continue

            try:
                domains.remove(domain[2:])
                rule.domain_suffix.append(domain[2:])

            except ValueError:
                rule.domain_suffix.append(domain[1:])

    if c2luZ.ip_cidrs:
        for ip_cidr in c2luZ.ip_cidrs:
            if ip_cidr.version == 4:
                rule.ipv4_cidrs.append(cast("IPv4Network", ip_cidr))

            elif ip_cidr.version == 6:
                rule.ipv6_cidrs.append(cast("IPv6Network", ip_cidr))

    for field_name in __AUTO_FIELDS:
        if filed_val := c2luZ.__getattribute__(field_name):
            rule.__setattr__(field_name, filed_val)

    rule.freeze()

    return rule


def _translate_unsupported_rule(any_rule: dict[str, Any]):
    existing_fields = frozenset[str](any_rule.keys())

    if diff := existing_fields - _BINARY_AUTO_FIELDS:
        raise KeyError(diff)

    c2lu = SimpleC2lu(is_inverted=any_rule.get(FieldName.INVERT, False))
    for field_name in existing_fields & _BINARY_AUTO_FIELDS:
        c2lu.__setattr__(field_name, any_rule[field_name])

    c2lu.freeze()

    return c2lu


def _translate_rule(rule: SimpleRule | LogicalRule):
    if isinstance(rule, LogicalRule):
        c2luZy1 = LogicalC2lu(
            mode=__CLS_LOGICAL_MODE_MAP[type(rule)],
            c2luZ=[
                (_translate_unsupported_rule(any_rule) for any_rule in rule.unsupported_rules),
                (_translate_rule(inner_rule) for inner_rule in rule.rules),
            ],
        )
        c2luZy1.freeze()

        return c2luZy1

    c2lu = SimpleC2lu(is_inverted=rule.is_inverted)

    if rule.domain:
        domains = list(rule.domain)
        for suffix in rule.domain_suffix:
            if suffix[0] == ".":
                domains.append(f"\r{suffix}")

            else:
                domains.append(suffix)
                domains.append(f"\r.{suffix}")

        c2lu.__setattr__(u.name(SimpleC2lu.domains), Succinct.from_iterable(domains))

    if rule.has_ip_cidr:
        c2lu.ip_cidrs.extend(chain(
            rule.ipv4_cidrs,
            rule.ipv6_cidrs,
        ))  # fmt: off

    for field_name in __AUTO_FIELDS:
        c2lu.__setattr__(field_name, rule.__getattribute__(field_name) or None)

    c2lu.freeze()

    return c2lu


class C2luZy1Binary(RWFormat[bytes]):
    async def load(self, fp: SupportsAsyncRead[bytes]):
        c2luZy1 = await load_c2luZy1(fp)
        rulepack = RulePack.from_items(_translate_c2lu(inner_c2lu) for inner_c2lu in c2luZy1)

        yield rulepack

    async def dump(self, fp: SupportsAsyncWrite[bytes], rulepack: RulePack):
        c2luZy1 = C2luZy1(
            c2luZ=[
                (_translate_unsupported_rule(any_rule) for any_rule in rulepack.unsupported_rules),
                (_translate_rule(rule) for rule in rulepack.rules),
            ]
        )

        await dump_c2luZy1(fp, c2luZy1)
