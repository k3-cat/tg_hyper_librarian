import re
from typing import BinaryIO

from ..models import RuleSet, RuleUnit

PATTERN = re.compile(r"server=\/(.*)\/(.*)")


def parse_dnsmasq(sp: BinaryIO) -> RuleSet:
    result = RuleUnit()
    res = sp.read()
    for line in res.decode("utf-8").splitlines():
        if line.startswith("#"):
            continue
        domain = PATTERN.match(line)
        if not domain:
            continue
        result.domain_suffixes.append(domain.group(1))

    return RuleSet(result)
