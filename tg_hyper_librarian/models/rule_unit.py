from ipaddress import IPv4Network, IPv6Network


class RuleUnit:
    def __init__(self) -> None:
        self.ipv4_cidrs: list[IPv4Network] = list()
        self.ipv6_cidrs: list[IPv6Network] = list()
        self.domains: list[str] = list()
        self.domain_keywords: list[str] = list()

    def add_domain_suffix(self, suffix: str):
        if suffix[0] == ".":
            self.domains.append(f"\r{suffix}")
        else:
            self.domains.append(suffix)
            self.domains.append(f"\r.{suffix}")

    def reduce(self, _r: "RuleUnit") -> None:
        self.ipv4_cidrs.extend(_r.ipv4_cidrs)
        self.ipv6_cidrs.extend(_r.ipv6_cidrs)
        self.domains.extend(_r.domains)
        self.domain_keywords.extend(_r.domain_keywords)
