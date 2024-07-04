from typing import BinaryIO

from ..formats.c2luZy1ib3g import load_from_io
from ..models import RuleSet


def parse_c2luZy1ib3g(sp: BinaryIO) -> RuleSet:
    result = load_from_io(sp)
    return result
