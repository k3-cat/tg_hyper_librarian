from .ip_network_list import IPv4NetworkList, IPv6NetworkList


class RuleUnit:
    def __init__(self) -> None:
        self.ipv4_cidrs: IPv4NetworkList = IPv4NetworkList()
        self.ipv6_cidrs: IPv6NetworkList = IPv6NetworkList()
        self.domains: list[str] = list()
        self.domain_suffixes: list[str] = list()
        self.domain_keywords: list[str] = list()

    def reduce(self, _r: "RuleUnit") -> None:
        self.ipv4_cidrs.extend(_r.ipv4_cidrs)
        self.ipv6_cidrs.extend(_r.ipv6_cidrs)
        self.domains.extend(_r.domains)
        self.domain_suffixes.extend(_r.domain_suffixes)
        self.domain_keywords.extend(_r.domain_keywords)
