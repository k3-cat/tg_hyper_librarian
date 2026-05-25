from typing import TYPE_CHECKING

from c2luZy1ib3g.models import SimpleC2lu
from c2luZy1ib3g.serdes.uint import load_uint

if TYPE_CHECKING:
    from tg_aio.protocols import SupportsAsyncRead


async def load_network_type(fp: SupportsAsyncRead[bytes]):
    code = await load_uint(fp)

    return SimpleC2lu.NetworkType(code)
