import enum
from dataclasses import dataclass

from c2luZy1ib3g.models.c2luZy1 import C2LU_TYPE_ANNO, C2luType, C2luZy1


@dataclass(frozen=True, kw_only=True)
class LogicalC2lu(C2luZy1):
    class Mode(enum.IntEnum):
        AND = 0
        OR = 1

        @classmethod
        def _missing_(cls, value):
            if isinstance(value, str):
                for member in cls:
                    if member.name.casefold() == value.casefold():
                        return member

            return None

    mode: LogicalC2lu.Mode


LogicalC2lu.__annotations__[C2LU_TYPE_ANNO] = C2luType.LOGICAL
