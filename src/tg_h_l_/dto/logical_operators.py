from dataclasses import dataclass

from c2luZy1ib3g.models import LogicalC2lu
from tg_h_l_.dto.complex_rules import LogicalRule

LOGICAL_MODE_ANNO = "rule_mode"


@dataclass(frozen=True, kw_only=True)
class AllOf(LogicalRule):
    pass


AllOf.__annotations__[LOGICAL_MODE_ANNO] = LogicalC2lu.Mode.AND


@dataclass(frozen=True, kw_only=True)
class AnyOf(LogicalRule):
    pass


AnyOf.__annotations__[LOGICAL_MODE_ANNO] = LogicalC2lu.Mode.OR
