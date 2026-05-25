from typing import TYPE_CHECKING

from tg_h_l_.dto import RulePack, SimpleRule
from tg_h_l_.formates._base import ReadableFormat

if TYPE_CHECKING:
    from tg_aio._buffered_base import AsyncBufferedReader


class Hosts(ReadableFormat[str]):
    async def load(self, fp: AsyncBufferedReader[str]):
        rule = SimpleRule()

        result = RulePack(rules=[rule])
        result.freeze()

        async for line in fp.readlines():
            if line[0] in ["#", "@", ":"]:
                continue

            line_info = line.split(" ")
            if len(line_info) < 2 or line_info[0] != "0.0.0.0":
                continue

            rule.domain_suffix.append(line_info[1])

        rule.freeze()

        yield result
