import enum
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tg_utils import PatchedDto

if TYPE_CHECKING:
    from c2luZy1ib3g.models import LogicalC2lu, SimpleC2lu


C2LU_TYPE_ANNO = "c2lu_type"


class C2luType(enum.IntEnum):
    REGULAR = 0
    LOGICAL = 1


@dataclass(frozen=True, kw_only=True)
class C2luZy1(PatchedDto):
    c2luZ: list[SimpleC2lu | LogicalC2lu]

    def __len__(self):
        return self.c2luZ.__len__()

    def __iter__(self):
        return self.c2luZ.__iter__()
