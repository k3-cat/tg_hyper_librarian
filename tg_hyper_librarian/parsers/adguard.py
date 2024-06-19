from ..models import And, Group, Not, RuleUnit
from .utils.http_client import get_content


def parse_adguard(url: str) -> Group:
    result = RuleUnit()
    anti_result = RuleUnit()
    res = get_content(url)
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
                anti_result.add_domain_suffix(line[4:-2])
            elif line.endswith("^"):
                anti_result.add_domain_suffix(line[4:-1])
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
                anti_result.add_domain_suffix(line[2:-2])
            elif line.endswith("^"):
                anti_result.add_domain_suffix(line[2:-1])
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
                result.add_domain_suffix(line[2:-1])
            else:
                result.domain_keywords.append(line[2:])
        elif line.startswith("|"):
            if line.endswith("^"):
                result.domains.append(line[1:-1])
            else:
                result.domain_keywords.append(line[1:])
        else:
            if line.endswith("^"):
                result.add_domain_suffix(line)

    return Group(And(result, Not(anti_result)))
