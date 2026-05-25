from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

from tg_h_l_.dto.simple_rule import SimpleRule
from tg_utils import PatchedDto

if TYPE_CHECKING:
    from typing import Any, Iterable, Self

    from tg_h_l_.dto.logical_operators import LogicalRule


LOGICAL_MODE_ANNO = "rule_mode"


@dataclass(frozen=True, kw_only=True)
class ComplexRuleBase(PatchedDto):
    unsupported_rules: list[dict[str, Any]] = field(default_factory=list)
    rules: list[SimpleRule | LogicalRule] = field(default_factory=list)
    is_inverted: bool = False

    @classmethod
    def from_items(cls, items: Iterable[SimpleRule | LogicalRule | dict]) -> Self:
        result = cls()
        for item in items:
            if isinstance(item, dict):
                result.unsupported_rules.append(item)
            else:
                result.rules.append(item)

        result.freeze()

        return result

    def reduce(self) -> Self:
        result = replace(self, rules=[])

        positive_rule = SimpleRule()
        negative_rule = SimpleRule(is_inverted=True)
        logical_rules = list[LogicalRule]()

        for rule in self.rules:
            if isinstance(rule, SimpleRule):
                inner_rule = positive_rule if not rule.is_inverted else negative_rule

                inner_rule.domain.extend(rule.domain)
                inner_rule.domain_suffix.extend(rule.domain_suffix)
                inner_rule.domain_keyword.extend(rule.domain_keyword)
                inner_rule.domain_regex.extend(rule.domain_regex)
                inner_rule.ipv4_cidrs.extend(rule.ipv4_cidrs)
                inner_rule.ipv6_cidrs.extend(rule.ipv6_cidrs)

            else:
                logical_rules.append(rule)

        if positive_rule:
            result.rules.append(positive_rule.reduce())

        if negative_rule:
            result.rules.append(negative_rule.reduce())

        result.rules.extend(logical_rules)

        result.freeze()

        return result


@dataclass(frozen=True, kw_only=True)
class RulePack(ComplexRuleBase):
    pass


@dataclass(frozen=True, kw_only=True)
class LogicalRule(ComplexRuleBase):
    pass
