from typing import TYPE_CHECKING, Iterator

from .rule_unit import RuleUnit

if TYPE_CHECKING:
    from . import TRule


class BasicLogic:
    def __init__(self, *rules: "TRule"):
        self.rule_units = rules

    @classmethod
    def from_tuple(cls, val: tuple["TRule", ...]):
        logic = cls()
        logic.rule_units = val
        return logic

    def __iter__(self) -> Iterator["TRule"]:
        return self.rule_units.__iter__()

    def __getitem__(self, k: int) -> "TRule":
        return self.rule_units[k]


class And(BasicLogic):
    pass


class Or(BasicLogic):
    pass


class Not:
    def __init__(self, unit: RuleUnit) -> None:
        self.unit = unit
