import math
from ipaddress import IPv4Network, IPv6Network
from typing import BinaryIO

from ..models.rule_set import RuleSet
from ..models.rule_unit import RuleUnit


def parse_apnic(sp: BinaryIO, country_code: str) -> RuleSet:
    result = RuleUnit()
    res = sp.read()
    for line in res.decode("utf-8").splitlines():
        if line.startswith("#"):
            continue
        line_info = line.split("|")
        if len(line_info) < 5 or line_info[1] != country_code:
            continue
        if line_info[2] == "ipv4":
            result.ipv4_cidrs.append(IPv4Network(f"{line_info[3]}/{32 - int(math.log2(int(line_info[4])))}"))
        elif line_info[2] == "ipv6":
            result.ipv6_cidrs.append(IPv6Network(f"{line_info[3]}/{line_info[4]}"))
        else:
            # asn
            pass

    return RuleSet(result)
