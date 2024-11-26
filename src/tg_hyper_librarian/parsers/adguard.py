from typing import BinaryIO

from ..models.complex_rule import And, Not, RuleUnit
from ..models.rule_set import RuleSet


def parse_adguard(sp: BinaryIO) -> RuleSet:
    result = RuleUnit()
    anti_result = RuleUnit()
    res = sp.read()
    for line_ in res.decode("utf-8").splitlines():
        line = line_.strip()
        # line_.startswith("!") or line_.startswith("#") or line_.startswith("@@")
        if (not line) or (line[0] in {"!", "#"}) or ("*" in line) or ("?" in line):
            continue
        if line.endswith("$important"):
            line = line[:-10]

        # unblock
        if line.startswith("@@||"):
            if line.endswith("^|"):
                anti_result.domain_suffixes.append(line[4:-2])
            elif line.endswith("^"):
                anti_result.domain_suffixes.append(line[4:-1])
            else:
                print("Warning: " + line)
        elif line.startswith("@@|"):
            if line.endswith("^|"):
                anti_result.domains.append(line[3:-2])
            elif line.endswith("^"):
                anti_result.domains.append(line[3:-1])
            else:
                print("Warning: " + line)
        elif line.startswith("@@"):
            if line.endswith("^|"):
                anti_result.domain_suffixes.append(line[2:-2])
            elif line.endswith("^"):
                anti_result.domain_suffixes.append(line[2:-1])
            else:
                print("Warning: " + line)
        # block
        elif line.startswith("://"):
            if line.endswith("^"):
                result.domains.append(line[3:-1])
            else:
                print("Warning: " + line)
        elif line.startswith("||"):
            if line.endswith("^"):
                result.domain_suffixes.append(line[2:-1])
            else:
                result.domain_keywords.append(line[2:])
        elif line.startswith("|"):
            if line.endswith("^"):
                result.domains.append(line[1:-1])
            else:
                result.domain_keywords.append(line[1:])
        else:
            if line.endswith("^"):
                result.domain_suffixes.append(line)

    return RuleSet(And(result, Not(anti_result)))
