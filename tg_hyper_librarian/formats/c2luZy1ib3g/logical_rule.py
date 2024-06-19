from collections.abc import Callable
from enum import Enum
from io import IOBase
from typing import TYPE_CHECKING

from ._common import read_uint, read_uvarint, write_uint, write_uvarint

if TYPE_CHECKING:
    from . import Tc2lu


class LogicalRule:
    class Mode(Enum):
        AND = 0
        OR = 1

    def __init__(self) -> None:
        self.invert = False
        self.mode: LogicalRule.Mode
        self.c2luZy1: list["Tc2lu"]

    @classmethod
    def read_from(cls, s: IOBase, _load_c2lu: Callable[[IOBase], "Tc2lu"]):
        c2lu = cls()
        c2lu.mode = LogicalRule.Mode(read_uint(s))
        length = read_uvarint(s)
        c2lu.c2luZy1 = [_load_c2lu(s) for _ in range(length)]

        return c2lu

    def write_to(self, s: IOBase, _write_c2lu: Callable[[IOBase, "Tc2lu"], None]):
        write_uint(s, self.mode.value)
        write_uvarint(s, len(self.c2luZy1))
        for c2lu in self.c2luZy1:
            _write_c2lu(s, c2lu)
