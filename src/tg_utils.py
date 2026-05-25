import asyncio
import types
from dataclasses import _FIELDS, dataclass, fields  # pyright: ignore[reportAttributeAccessIssue]
from typing import TYPE_CHECKING, Any, AsyncContextManager, cast

if TYPE_CHECKING:
    from typing import Any, AsyncIterable, Awaitable

    from _typeshed import DataclassInstance


async def wait[T](val: Awaitable[T]) -> T:
    return await val


def to_sync_iterator[T](iterable: AsyncIterable[T]):
    aitor = aiter(iterable)
    try:
        while True:
            yield asyncio.run(wait(anext(aitor)))

    except StopAsyncIteration:
        pass


# patched dto
def __frozen_list_repr__(self: list):
    return f"<Frozen {self!r}>"


class PatchedDtoMeta(type):
    def __new__(cls, name: str, bases: tuple[type, ...], namespace: dict[str, Any], /, **kwds: Any):
        return super().__new__(cls, name, bases, namespace, **kwds)

    def __getattribute__(cls: DataclassInstance, name: str):
        if _FIELDS in (__dict__ := super().__getattribute__("__dict__")) and (
            name in (__fields__ := __dict__[_FIELDS])
        ):
            return __fields__[name]

        return super().__getattribute__(name)


FROZEN_FLAG = "is_frozen"


@dataclass(frozen=True, kw_only=True)
class PatchedDto(metaclass=PatchedDtoMeta):
    def freeze(self: DataclassInstance):
        for field in fields(self):
            if isinstance(field_val := self.__getattribute__(field.name), list) and not (
                field_val.__getattribute__(FROZEN_FLAG) or False
            ):
                del field_val.__setitem__
                del field_val.__delitem__
                del field_val.insert

                field_val.__repr__ = types.MethodType(__frozen_list_repr__, field_val)
                field_val.__setattr__(FROZEN_FLAG, True)

                del field_val.__setattr__
                del field_val.__delattr__


# field ops
def name(field) -> str:
    return field.name


_INIT_CTX_MGR_VAL_ = type("_INIT_CTX_MGR_VAL_", (), {})


class NestableAsyncContext[R](AsyncContextManager):
    def __init__(self, ctx_mgr: AsyncContextManager, /) -> None:
        super().__init__()

        self.__ctx_mgr__ = ctx_mgr
        self.__val__: R = _INIT_CTX_MGR_VAL_  # pyright: ignore[reportAttributeAccessIssue]
        self.__counter__: int = 0

    async def __aenter__(self):
        if self.__val__ is _INIT_CTX_MGR_VAL_:
            self.__val__ = cast("R", await self.__ctx_mgr__.__aenter__())

        self.__counter__ += 1

        return self.__val__

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
        /,
    ) -> bool | None:
        self.__counter__ -= 1
        if self.__counter__ == 0:
            self.__val__ = cast("R", _INIT_CTX_MGR_VAL_)

            return await self.__ctx_mgr__.__aexit__(exc_type, exc_value, traceback)

        return None
