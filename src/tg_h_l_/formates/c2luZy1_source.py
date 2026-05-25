import enum
import logging
from dataclasses import fields
from itertools import chain
from typing import TYPE_CHECKING, cast

import jsonc
import orjson

from c2luZy1ib3g.consts import CURRENT_VERSION
from c2luZy1ib3g.models import LogicalC2lu
from tg_h_l_.dto import (
    LOGICAL_MODE_ANNO,
    SIMPLE_RULE_TYPE_I_FIELDS,
    AllOf,
    AnyOf,
    LogicalRule,
    RulePack,
    SimpleRule,
)
from tg_h_l_.formates._base import RWFormat
from tg_ip import ip_network

if TYPE_CHECKING:
    from typing import Any, Iterable, Type

    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite
    from tg_ip import IPv4Network, IPv6Network


class FieldName(enum.StrEnum):
    VERSION = "version"

    RULE_TYPE = "type"
    LOGICAL_MODE = "mode"
    RULES = "rules"
    IP_CIDR = "ip_cidr"
    INVERT = "invert"


_JSON_AUTO_FIELDS = (
    frozenset(field.name for field in fields(SimpleRule)) - SIMPLE_RULE_TYPE_I_FIELDS
)
__KNOWN_SIMPLE_RULE_FIELDS = _JSON_AUTO_FIELDS | frozenset[str](
    (FieldName.IP_CIDR, FieldName.INVERT)
)
__KNOWN_LOGICAL_RULE_FIELDS = frozenset[str]((
    FieldName.RULE_TYPE,
    FieldName.LOGICAL_MODE,
    *(field.name for field in fields(LogicalRule) if field != LogicalRule.unsupported_rules),
))  # fmt: off


LOGICAL_VAL = "logical"
_LOGIC_MODE_CLS_MAP: dict[LogicalC2lu.Mode, Type[LogicalRule]] = {
    cls.__annotations__[LOGICAL_MODE_ANNO]: cls for cls in (AllOf, AnyOf)
}


def _load_record(version: int, record: dict[str, Any]):
    existing_fields = frozenset[str](record.keys())
    if diff := existing_fields - __KNOWN_SIMPLE_RULE_FIELDS:
        logging.info("skip unknown fields:", diff)
        return record

    is_inverted = record.get(FieldName.INVERT, False)
    if record[FieldName.RULE_TYPE] == LOGICAL_VAL:
        if diff := existing_fields - __KNOWN_LOGICAL_RULE_FIELDS:
            logging.warning("unknown logical fields:", diff)
            return record

        rulepack = _LOGIC_MODE_CLS_MAP[LogicalC2lu.Mode[record[FieldName.LOGICAL_MODE]]].from_items(
            _load_record(version, inner_record) for inner_record in record[FieldName.RULES]
        )

        return rulepack

    rule = SimpleRule(is_inverted=is_inverted)

    if FieldName.IP_CIDR in existing_fields:
        for cidr_str in record[FieldName.IP_CIDR]:
            network = ip_network(cidr_str, strict=False)
            if network.version == 4:
                rule.ipv4_cidrs.append(cast("IPv4Network", network))

            elif network.version == 6:
                rule.ipv6_cidrs.append(cast("IPv6Network", network))

    for field_name in existing_fields & _JSON_AUTO_FIELDS:
        record_list: list[str] = record[field_name]
        if version == 1 and field_name == "domain_suffix":
            rule.domain_suffix.extend(
                domain_suffix if not domain_suffix.startswith(".") else domain_suffix[1:]
                for domain_suffix in record_list
            )

        else:
            rule.__getattribute__(field_name).extend(record_list)

    rule.freeze()

    return rule


def _dump_unsupported_record(any_records: Iterable[dict[str, Any]]):
    yield from any_records


def _dump_record(rule: SimpleRule | LogicalRule):
    record = {}

    if rule.is_inverted:
        record[FieldName.INVERT] = True

    if isinstance(rule, LogicalRule):
        record[FieldName.RULE_TYPE] = LOGICAL_VAL
        record[FieldName.LOGICAL_MODE] = rule.__annotations__[LOGICAL_MODE_ANNO]
        record[FieldName.RULES] = [
            (_dump_unsupported_record(rule.unsupported_rules)),
            (_dump_record(inner_rule) for inner_rule in rule.rules),
        ]

    elif isinstance(rule, SimpleRule):
        if rule.has_ip_cidr:
            record[FieldName.IP_CIDR] = [
                str(cidr) for cidr in chain(rule.ipv4_cidrs, rule.ipv6_cidrs)
            ]

        for field_name in _JSON_AUTO_FIELDS:
            if field_val := rule.__getattribute__(field_name):
                record[field_name] = field_val

    return record


class C2luZy1Source(RWFormat[bytes]):
    async def load(self, fp: SupportsAsyncRead[bytes]):
        record = jsonc.loads((await fp.read()).decode())
        version = record[FieldName.VERSION]

        rulepack = RulePack.from_items(
            _load_record(version, inner_record) for inner_record in record[FieldName.RULES]
        )

        yield rulepack

    async def dump(self, fp: SupportsAsyncWrite[bytes], rulepack: RulePack):
        await fp.write(orjson.dumps({
            FieldName.VERSION: CURRENT_VERSION,
            FieldName.RULES: [
                (_dump_unsupported_record(rulepack.unsupported_rules)),
                (_dump_record(inner_rule) for inner_rule in rulepack.rules),
            ],
        }))  # fmt: off
