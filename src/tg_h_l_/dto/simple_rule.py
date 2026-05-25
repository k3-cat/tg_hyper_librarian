from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import tg_utils as u
from tg_ip import collapse_addresses
from tg_utils import PatchedDto

if TYPE_CHECKING:
    from tg_ip import IPv4Network, IPv6Network


@dataclass(frozen=True, kw_only=True)
class SimpleRule(PatchedDto):
    domain: list[str] = field(default_factory=list)
    domain_suffix: list[str] = field(default_factory=list)
    domain_keyword: list[str] = field(default_factory=list)
    domain_regex: list[str] = field(default_factory=list)
    ipv4_cidrs: list[IPv4Network] = field(default_factory=list)
    ipv6_cidrs: list[IPv6Network] = field(default_factory=list)
    is_inverted: bool = False

    @property
    def has_ip_cidr(self) -> bool:
        return bool(self.ipv4_cidrs) or bool(self.ipv6_cidrs)

    def reduce(self):
        result = self.__class__(
            domain=list(sorted(self.domain)),
            domain_suffix=list(sorted(self.domain_suffix)),
            domain_keyword=list(sorted(self.domain_keyword)),
            domain_regex=list(sorted(self.domain_regex)),
            ipv4_cidrs=list(collapse_addresses(self.ipv4_cidrs)),
            ipv6_cidrs=list(collapse_addresses(self.ipv6_cidrs)),
            is_inverted=self.is_inverted,
        )

        result.freeze()

        return result


SIMPLE_RULE_TYPE_I_FIELDS = frozenset[str]((
    u.name(SimpleRule.ipv4_cidrs),
    u.name(SimpleRule.ipv6_cidrs),
    u.name(SimpleRule.is_inverted),
))  # fmt: off

SIMPLE_RULE_TYPE_II_FIELDS = SIMPLE_RULE_TYPE_I_FIELDS | frozenset[str]((
    u.name(SimpleRule.domain),
    u.name(SimpleRule.domain_suffix),
))  # fmt: off
