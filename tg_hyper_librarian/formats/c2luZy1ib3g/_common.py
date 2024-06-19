from enum import Enum
from io import IOBase

MAGIC = b"\x53\x52\x53"


class RuleType(Enum):
    REGULAR = 0
    LOGIC = 1


MAX_VARINT_LEN64 = 10


def read_uvarint(s: IOBase) -> int:
    x = 0
    sig = 0
    for i in range(MAX_VARINT_LEN64):
        chunk = s.read(1)
        if not chunk:
            raise EOFError()
        byte = chunk[0]
        if byte < 0x80:
            if i == MAX_VARINT_LEN64 - 1 and byte > 1:
                return x
            break
        x |= (byte & 0x7F) << sig
        sig += 7

    else:
        raise OverflowError(f"integer > {MAX_VARINT_LEN64} bytes")

    return x | (byte << sig)


def write_uvarint(s: IOBase, x: int):
    # TODO
    pass


def read_vstring(s: IOBase) -> str:
    length = read_uvarint(s)
    return s.read(length).decode("utf-8")


def write_vstring(s: IOBase, string: str) -> int:
    write_uvarint(s, len(string))
    return s.write(string.encode("utf-8"))


def read_uint(s: IOBase, length: int = 1) -> int:
    return int.from_bytes(s.read(length), byteorder="big", signed=False)


def write_uint(s: IOBase, x: int, length: int = 1) -> int:
    return s.write(x.to_bytes(length, byteorder="big", signed=False))
