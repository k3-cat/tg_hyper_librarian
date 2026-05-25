from annotationlib import ForwardRef
from dataclasses import Field
from types import GenericAlias
from typing import (
    TYPE_CHECKING,
    NamedTuple,
    Type,
    _GenericAlias,  # pyright: ignore[reportAttributeAccessIssue]
    get_args,
)

import asyncstdlib as a

from c2luZy1ib3g.binary_format.enum_like_types import load_network_type
from c2luZy1ib3g.serdes import (
    dump_string_list,
    dump_succinct,
    dump_uint,
    dump_uint16_list,
    load_string_list,
    load_succinct,
    load_uint16_list,
)

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable

    from c2luZy1ib3g.models.simple_c2lu import SimpleC2lu
    from succinct import Succinct
    from tg_aio.protocols import SupportsAsyncRead, SupportsAsyncWrite
    from tg_ip import IPCidrList


class SerDePair(NamedTuple):
    deserializer: Callable[[SupportsAsyncRead[bytes]], Awaitable[Any]]
    serializer: Callable[[SupportsAsyncWrite[bytes], Any], Awaitable[Any]]


def _type2str(t: Any):
    if isinstance(t, _GenericAlias):
        t = get_args(t)[0]

    if isinstance(t, GenericAlias):
        return str(t)

    if isinstance(t, ForwardRef):
        return t.__forward_arg__

    if isinstance(t, dict):
        args = get_args(t)
        return f"dict[{_type2str(args[0])}, {_type2str(args[1])}]"

    return t


SER_DE_MAP = {
    bool: SerDePair(a.sync(lambda _: True), a.sync(lambda _, __: None)),
    "list[int]": SerDePair(load_uint16_list, dump_uint16_list),
    "list[str]": SerDePair(load_string_list, dump_string_list),
    _type2str(Type["Succinct | None"]): SerDePair(load_succinct, dump_succinct),
    _type2str(Type["SimpleC2lu.NetworkType | None"]): SerDePair(load_network_type, dump_uint),
}


def field_2_serde_pair(field: Field) -> SerDePair:
    type_str = _type2str(field.type)

    return SER_DE_MAP[type_str]
