from typing import TYPE_CHECKING

from .rule_unit import RuleUnit

if TYPE_CHECKING:
    from . import TRule


class BasicLogic:
    def __init__(self, *rules: "TRule"):
        self.sub_rules = rules

    @classmethod
    def from_tuple(cls, val: tuple["TRule", ...]):
        logic = cls()
        logic.sub_rules = val
        return logic

    def __iter__(self):
        return self.sub_rules.__iter__()

    def __getitem__(self, k: int) -> "TRule":
        return self.sub_rules[k]


class And(BasicLogic):
    pass


class Or(BasicLogic):
    pass


class Not:
    def __init__(self, unit: RuleUnit) -> None:
        self.unit = unit


class Group:
    def __init__(self, *rules: "TRule"):
        self.rules = rules

    @classmethod
    def from_tuple(cls, val: tuple["TRule", ...]):
        group = cls()
        group.rules = val
        return group

    def __iter__(self):
        return self.rules.__iter__()

    def __getitem__(self, k: int) -> "TRule":
        return self.rules[k]
