from typing import BinaryIO

from ..models import RuleSet, RuleUnit


def parse_hosts(sp: BinaryIO) -> RuleSet:
    result = RuleUnit()
    res = sp.read()
    for line in res.decode("utf-8").splitlines():
        if line[0] in ["#", "@", ":"]:
            continue
        line_info = line.split(" ")
        if len(line_info) < 2 or line_info[0] != "0.0.0.0":
            continue
        result.domain_suffixes.append(line_info[1])

    return RuleSet(result)
