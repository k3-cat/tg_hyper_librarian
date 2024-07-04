__all__ = ["load_from_io", "load_from_io_full", "write_to_io", "write_to_io_full"]

from typing import TYPE_CHECKING

from .deserializer import load_from_io, load_from_io_full
from .serializer import write_to_io, write_to_io_full

if TYPE_CHECKING:
    from .c2lu import C2lu
    from .logical_group import LogicalGroup

    Tc2lu = C2lu | LogicalGroup
