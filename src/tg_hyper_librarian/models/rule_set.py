from typing import Iterable, Iterator

from .complex_rule import TRule
from .rule_unit import RuleUnit


class RuleSet:
    def __init__(self, *rules: TRule):
        self.rules = list(rules)

    @classmethod
    def from_collection(cls, iter: Iterable[TRule]):
        rule_set = cls()
        rule_set.rules = list(iter)
        return rule_set

    def extend(self, iter: Iterable[TRule]):
        self.rules.extend(iter)

    def reduce_all(self):
        main = RuleUnit()
        result: list[TRule] = [main]
        for rule in self.rules:
            if isinstance(rule, RuleUnit):
                main.reduce(rule)
            else:
                result.append(rule)
        self.rules = result

    def __iter__(self) -> Iterator[TRule]:
        return self.rules.__iter__()

    def __getitem__(self, k: int) -> TRule:
        return self.rules[k]
