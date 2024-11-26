import json
from ipaddress import collapse_addresses
from typing import Any, BinaryIO

from ...models.complex_rule import And, Not, Or, RuleUnit, TRule
from ...models.rule_set import RuleSet

MODE_MAP = {
    And: "and",
    Or: "or",
}


def _dump_rule_set(rule: TRule) -> dict[str, Any]:
    part: dict[str, Any]
    if isinstance(rule, RuleUnit):
        part = dict()
        ipv4_cidrs = [str(cidr) for cidr in collapse_addresses(rule.ipv4_cidrs)]
        ipv6_cidrs = [str(cidr) for cidr in collapse_addresses(rule.ipv6_cidrs)]
        if ipv4_cidrs or ipv6_cidrs:
            part["ip_cidr"] = [*ipv4_cidrs, *ipv6_cidrs]
        if rule.domains:
            part["domain"] = rule.domains
        if rule.domain_suffixes:
            part["domain_suffix"] = rule.domain_suffixes
        if rule.domain_keywords:
            part["domain_keyword"] = rule.domain_keywords

    elif isinstance(rule, Not):
        part = _dump_rule_set(rule.unit)
        part["invert"] = True

    elif isinstance(rule, And | Or):
        part = {
            "type": "logical",
            "mode": MODE_MAP[type(rule)],
            "rules": [_dump_rule_set(rule_unit) for rule_unit in rule],
        }

    return part


def dumps(rule_set: RuleSet) -> bytes:
    return json.dumps(
        {"version": 1, "rules": [_dump_rule_set(rule) for rule in rule_set]},
        indent=2,
    ).encode("utf-8")


def write_to_io(sp: BinaryIO, rule_set: RuleSet) -> int:
    return sp.write(dumps(rule_set))
