from queue import Queue
from typing import BinaryIO, Iterator

from bitarray import bitarray

from ._common import read_uint, read_uvarint, write_uint, write_uvarint


class QElt:
    def __init__(self, start: int, end: int, col: int) -> None:
        self.start: int = start
        self.end: int = end
        self.col: int = col


def _set_bit(bits: bitarray, i: int, value: bool):
    while i >= len(bits):
        if not value:
            return
        bits.extend([0] * 64)

    bits[i] = value


def _find_ith_one(bits: bitarray, i: int) -> int:
    for j in range(len(bits)):
        if bits[j]:
            i -= 1
        if i <= 0:
            return j

    raise ValueError(f"only {i} of 1s")


class Succinct:
    def __init__(self, leaf_map: bitarray, label_map: bitarray, labels: str) -> None:
        self._leaf_map = leaf_map
        self._label_map = label_map
        self._labels = labels

    @classmethod
    def from_list(cls, keys: list[str]):
        leaf_map = bitarray(endian="big")
        label_map = bitarray(endian="big")
        labels = list()

        queue: Queue[QElt] = Queue()
        queue.put(QElt(0, len(keys), 0))

        i = 0
        lIdx = 0
        while not queue.empty():
            elt = queue.get()

            if elt.col == len(keys[elt.start]):
                # a leaf node
                elt.start += 1
                _set_bit(leaf_map, i, True)

            j = elt.start
            while j < elt.end:
                frm = j
                while j < elt.end and keys[j][elt.col] == keys[frm][elt.col]:
                    j += 1

                queue.put(QElt(frm, j, elt.col + 1))
                labels.append(keys[frm][elt.col])
                _set_bit(label_map, lIdx, False)
                lIdx += 1

            _set_bit(label_map, lIdx, True)
            lIdx += 1
            i += 1

        return cls(leaf_map, label_map, "".join(labels))

    def keys(self, nodeId: int, partial_label: list[str]) -> Iterator[str]:
        bmIdx = _find_ith_one(self._label_map, nodeId) + 1 if nodeId != 0 else 0
        if self._leaf_map[nodeId]:
            yield "".join(partial_label)

        # across level
        # exit when no more lables in this level
        while not self._label_map[bmIdx]:
            partial_label_ = partial_label.copy()
            partial_label_.append(self._labels[bmIdx - nodeId])
            # go to next level
            yield from self.keys(
                self._label_map.count(False, 0, bmIdx + 1),
                partial_label_,
            )
            bmIdx += 1

    def to_list(self) -> list[str]:
        return list(self.keys(0, list()))

    @classmethod
    def read_from(cls, s: BinaryIO):
        _ = read_uint(s)  # version

        leaf_map_len = read_uvarint(s)
        leaf_map = bitarray()
        leaf_map.frombytes(s.read(leaf_map_len * 8))

        label_map_len = read_uvarint(s)
        label_map = bitarray()
        label_map.frombytes(s.read(label_map_len * 8))

        labels_len = read_uvarint(s)
        labels = s.read(labels_len).decode("utf-8")

        return cls(leaf_map, label_map, labels)

    def write_to(self, s: BinaryIO):
        write_uint(s, 1)  # version
        write_uvarint(s, int(len(self._leaf_map) / 64 + 0.5))
        s.write(self._leaf_map.tobytes())
        write_uvarint(s, int(len(self._label_map) / 64 + 0.5))
        s.write(self._label_map.tobytes())
        write_uvarint(s, len(self._labels))
        s.write(self._labels.encode("utf-8"))
