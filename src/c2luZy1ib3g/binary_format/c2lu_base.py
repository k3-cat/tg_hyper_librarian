from dataclasses import fields
from typing import TYPE_CHECKING, NamedTuple

from c2luZy1ib3g.binary_format.serde_options import field_2_serde_pair
from c2luZy1ib3g.models import C2LU_ITEMTYPE_ANNO, SIMPLE_C2LU_TYPE_I_FIELDS, SimpleC2lu
from c2luZy1ib3g.serdes import dump_uint, load_uint

if TYPE_CHECKING:
    from c2luZy1ib3g.binary_format.serde_options import SerDePair
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite


__all__ = ["load_simple_c2lu", "dump_simple_c2lu"]


class _FieldMeta(NamedTuple):
    name: str
    serde: SerDePair


__ITEM_TYPE_FIELD_META_MAP: dict[SimpleC2lu.ItemType, _FieldMeta] = {
    field.metadata[C2LU_ITEMTYPE_ANNO]: _FieldMeta(field.name, field_2_serde_pair(field))
    for field in fields(SimpleC2lu)
    if field.name not in SIMPLE_C2LU_TYPE_I_FIELDS
}


async def load_simple_c2lu(fp: SupportsAsyncRead[bytes]) -> SimpleC2lu:
    result = SimpleC2lu()
    while True:
        item_type = SimpleC2lu.ItemType(await load_uint(fp))
        if item_type == SimpleC2lu.ItemType.FINAL:
            result.__setattr__("is_inverted", (await fp.read(1))[0] != 0)

            break

        field = __ITEM_TYPE_FIELD_META_MAP[item_type]
        result.__setattr__(
            field.name,
            await field.serde.deserializer(fp),
        )

    result.freeze()

    return result


async def dump_simple_c2lu(fp: SupportsAsyncWrite[bytes], c2lu: SimpleC2lu):
    for item_type, field in __ITEM_TYPE_FIELD_META_MAP.items():
        if field_val := c2lu.__getattribute__(field.name):
            await dump_uint(fp, item_type)
            await field.serde.serializer(fp, field_val)

    await dump_uint(fp, SimpleC2lu.ItemType.FINAL)
    await dump_uint(fp, 0x01 if c2lu.is_inverted else 0x00)
