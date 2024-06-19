__all__ = ["load_from_c2luZy1ib3g", "load_from_c2luZy1ib3g_full", "write_to_c2luZy1ib3g", "write_to_c2luZy1ib3g_full"]

from typing import TYPE_CHECKING

from .deserializer import load_from_c2luZy1ib3g, load_from_c2luZy1ib3g_full
from .serializer import write_to_c2luZy1ib3g, write_to_c2luZy1ib3g_full

if TYPE_CHECKING:
    from .logical_rule import LogicalRule
    from .regular_rule import RegularRule

    Tc2lu = RegularRule | LogicalRule
