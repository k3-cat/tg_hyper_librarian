from collections.abc import Callable
from enum import Enum
from typing import BinaryIO

from ._common import read_uint, read_uvarint, write_uint, write_uvarint
from .c2lu import C2lu


class LogicalGroup:
    class Mode(Enum):
        AND = 0
        OR = 1

    def __init__(self) -> None:
        self.invert = False
        self.mode: LogicalGroup.Mode
        self.c2luZy1: list["Tc2lu"]

    @classmethod
    def read_from(cls, sp: BinaryIO, _load_c2lu: Callable[[BinaryIO], "Tc2lu"]):
        c2lu = cls()
        c2lu.mode = LogicalGroup.Mode(read_uint(sp))
        length = read_uvarint(sp)
        c2lu.c2luZy1 = [_load_c2lu(sp) for _ in range(length)]

        return c2lu

    def write_to(self, sp: BinaryIO, _write_c2lu: Callable[[BinaryIO, "Tc2lu"], None]):
        write_uint(sp, self.mode.value)
        write_uvarint(sp, len(self.c2luZy1))
        for c2lu in self.c2luZy1:
            _write_c2lu(sp, c2lu)


Tc2lu = C2lu | LogicalGroup
