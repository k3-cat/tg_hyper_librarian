from typing import TYPE_CHECKING

from c2luZy1ib3g.serdes.uint import dump_uint, load_uint
from c2luZy1ib3g.serdes.uvarint import dump_uvarint, load_uvarint
from succinct import Succinct, bitarray

if TYPE_CHECKING:
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite


async def load_succinct(fp: SupportsAsyncRead[bytes]):
    _ = load_uint(fp)  # version

    leaf_map_len = await load_uvarint(fp)
    leaf_map = bitarray()
    leaf_map.frombytes(await fp.read(leaf_map_len * 8))

    label_map_len = await load_uvarint(fp)
    label_map = bitarray()
    label_map.frombytes(await fp.read(label_map_len * 8))

    labels_len = await load_uvarint(fp)
    labels = (await fp.read(labels_len)).decode("utf-8")

    return Succinct(leaf_map=leaf_map, label_map=label_map, labels=labels)


async def dump_succinct(fp: SupportsAsyncWrite[bytes], succinct: Succinct):
    await dump_uint(fp, 1)  # version

    await dump_uvarint(fp, int(len(succinct.leaf_map) / 64 + 0.5))
    await fp.write(succinct.leaf_map.tobytes())

    await dump_uvarint(fp, int(len(succinct.label_map) / 64 + 0.5))
    await fp.write(succinct.label_map.tobytes())

    await dump_uvarint(fp, len(succinct.labels))
    await fp.write(succinct.labels.encode("utf-8"))
