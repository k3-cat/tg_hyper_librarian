from enum import Enum
from typing import BinaryIO

MAGIC = b"\x53\x52\x53"


class RuleType(Enum):
    REGULAR = 0
    LOGIC = 1


MAX_VARINT_LEN64 = 10
_OVERFLOW_ERROR = OverflowError(f"integer > {MAX_VARINT_LEN64} bytes")


def read_uvarint(sp: BinaryIO) -> int:
    x = 0
    sig = 0
    for i in range(MAX_VARINT_LEN64):
        chunk = sp.read(1)
        if not chunk:
            raise EOFError()
        byte = chunk[0]
        if byte < 0x80:
            if i == MAX_VARINT_LEN64 - 1 and byte > 1:
                raise _OVERFLOW_ERROR
            return x | (byte << sig)
        x |= (byte & 0x7F) << sig
        sig += 7

    raise _OVERFLOW_ERROR


def write_uvarint(sp: BinaryIO, x: int) -> int:
    i = 0
    while x >= 0x80:
        write_uint(sp, (x % 0xFF) | 0x80)
        x >>= 7
        i += 1
    write_uint(sp, x)
    return i + 1


def read_vstring(sp: BinaryIO) -> str:
    length = read_uvarint(sp)
    return sp.read(length).decode("utf-8")


def write_vstring(sp: BinaryIO, string: str) -> int:
    write_uvarint(sp, len(string))
    return sp.write(string.encode("utf-8"))


def read_uint(sp: BinaryIO, length: int = 1) -> int:
    return int.from_bytes(sp.read(length), byteorder="big", signed=False)


def write_uint(sp: BinaryIO, x: int, length: int = 1) -> int:
    return sp.write(x.to_bytes(length, byteorder="big", signed=False))
