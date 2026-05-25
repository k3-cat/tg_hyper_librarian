from dataclasses import dataclass
from queue import Queue
from typing import TYPE_CHECKING, Sequence, overload

from bitarray import bitarray as bitarray_

if TYPE_CHECKING:
    from typing import Iterable, Iterator, Union

_WORD = 64
U64_ZERO = "0" * _WORD


class bitarray(bitarray_):
    @overload
    def __getitem__(self, i: int) -> int: ...
    @overload
    def __getitem__(self, i: Union[slice, bitarray_, Sequence]) -> bitarray: ...
    def __getitem__(self, i):  # pyright: ignore[reportInconsistentOverload]
        if not isinstance(i, int):
            return self.__class__(super().__getitem__(i))

        if (len(self) - (i + 1)) < 0:
            return 0

        return super().__getitem__(i)

    @overload
    def __setitem__(self, i: Union[int, slice, Sequence], v: int) -> None: ...
    @overload
    def __setitem__(self, i: Union[slice, bitarray_, Sequence], v: bitarray_) -> None: ...
    def __setitem__(self, i, v) -> None:
        min_size: int = 0
        if isinstance(i, int):
            min_size = i + 1

        elif isinstance(i, slice):
            min_size = i.stop

        if (diff := len(self) - min_size) < 0:
            # since `diff` is granteed to be non-zero, this should provides a safe celling
            self.extend(U64_ZERO * ((diff // -_WORD) + 1))

        super().__setitem__(i, v)


class _QElt:
    def __init__(self, start: int, end: int, col: int) -> None:
        self.start: int = start
        self.end: int = end
        self.col: int = col


def _find_ith_one(bits: bitarray, i: int) -> int:
    for j, bit in enumerate(bits):
        i -= bit

        if i <= 0:
            return j

    raise ValueError(f"there are only {i} of 1s")


@dataclass(frozen=True, kw_only=True)
class Succinct:
    leaf_map: bitarray
    label_map: bitarray
    labels: str

    @classmethod
    def from_iterable(cls, keys: Iterable[str]):
        leaf_map = bitarray(endian="big")
        label_map = bitarray(endian="big")
        labels = list()

        items = sorted(keys)
        queue: Queue[_QElt] = Queue()
        queue.put(_QElt(0, len(items), 0))

        i = 0
        lIdx = 0
        while not queue.empty():
            elt = queue.get()

            if elt.col == len(items[elt.start]):
                # a leaf node
                elt.start += 1
                leaf_map[i] = True

            j = elt.start
            while j < elt.end:
                frm = j
                while j < elt.end and items[j][elt.col] == items[frm][elt.col]:
                    j += 1

                queue.put(_QElt(frm, j, elt.col + 1))
                labels.append(items[frm][elt.col])
                label_map[lIdx] = False
                lIdx += 1

            label_map[lIdx] = True
            lIdx += 1
            i += 1

        return cls(leaf_map=leaf_map, label_map=label_map, labels="".join(labels))

    def keys(self, nodeId: int = 0, partial_label: list[str] | None = None) -> Iterator[str]:
        partial_label = partial_label or []
        bmIdx = _find_ith_one(self.label_map, nodeId) + 1 if nodeId != 0 else 0
        if self.leaf_map[nodeId]:
            yield "".join(partial_label)

        # across level
        # exit when no more lables in this level
        while not self.label_map[bmIdx]:
            partial_label_ = partial_label.copy()
            partial_label_.append(self.labels[bmIdx - nodeId])
            # go to next level
            yield from self.keys(
                self.label_map.count(False, 0, bmIdx + 1),
                partial_label_,
            )
            bmIdx += 1
