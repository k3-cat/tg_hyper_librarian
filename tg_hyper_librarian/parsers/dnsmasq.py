import re

from ..models import Group, RuleUnit
from .utils.http_client import get_content

PATTERN = re.compile(r"server=\/(.*)\/(.*)")


def parse_dnsmasq(url: str) -> Group:
    result = RuleUnit()
    res = get_content(url)
    for line in res.decode("utf-8").splitlines():
        if line.startswith("#"):
            continue
        domain = PATTERN.match(line)
        if not domain:
            continue
        result.add_domain_suffix(domain.group(1))

    return Group(result)
