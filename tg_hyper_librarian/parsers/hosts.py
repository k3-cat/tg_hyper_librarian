from ..models import Group, RuleUnit
from .utils.http_client import get_content


def parse_hosts(url: str) -> Group:
    result = RuleUnit()
    res = get_content(url)
    for line in res.decode("utf-8").splitlines():
        if line[0] in ["#", "@", ":"]:
            continue
        line_info = line.split(" ")
        if len(line_info) < 2 or line_info[0] != "0.0.0.0":
            continue
        result.add_domain_suffix(line_info[1])

    return Group(result)
