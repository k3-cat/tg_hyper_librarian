import json
from ipaddress import IPv4Network, IPv6Network, collapse_addresses
from typing import Any

from ...models import And, Group, Not, Or, RuleUnit, TRule

MODE_MAP: dict[str, type[And] | type[Or]] = {
    "and": And,
    "or": Or,
}


def _load_rule_set(part: dict[str, Any]) -> TRule:
    if "type" not in part:
        rule = RuleUnit()
        if "ip_cidr" in part:
            ipv4_cidrs: list[IPv4Network] = list()
            ipv6_cidrs: list[IPv6Network] = list()
            for cidr in part["ip_cidr"]:
                if ":" in cidr:
                    ipv6_cidrs.append(IPv6Network(cidr))
                else:
                    ipv4_cidrs.append(IPv4Network(cidr))

            rule.ipv4_cidrs = list(collapse_addresses(ipv4_cidrs))
            rule.ipv6_cidrs = list(collapse_addresses(ipv6_cidrs))

        if "domain" in part:
            rule.domains.extend(rule.domains)

        if "domain_suffix" in part:
            for domain_suffix in part["domain_suffix"]:
                rule.add_domain_suffix(domain_suffix)

        if "domain_keyword" in part:
            rule.domain_keywords.extend(part["domain_keyword"])

        if "invert" in part and part["invert"] is True:
            rule = Not(rule)

    else:
        rule = MODE_MAP[part["mode"]]()
        rule.from_tuple(tuple(_load_rule_set(rule) for rule in part["rules"]))

    return rule


def load_from_json(raw_json: bytes) -> Group:
    rule_set = json.loads(raw_json)
    _ = rule_set["version"]
    return Group.from_tuple(tuple(_load_rule_set(rule) for rule in rule_set["rules"]))
