import re
from typing import TYPE_CHECKING

from tg_h_l_.dto import RulePack, SimpleRule
from tg_h_l_.formates._base import ReadableFormat

if TYPE_CHECKING:
    from tg_aio._buffered_base import AsyncBufferedReader

PATTERN = re.compile(r"server=\/(.*)\/(.*)")


class Dnsmasq(ReadableFormat[str]):
    async def load(self, fp: AsyncBufferedReader[str]):
        rule = SimpleRule()

        result = RulePack(rules=[rule])
        result.freeze()

        async for line in fp.readlines():
            if line.startswith("#"):
                continue

            domain = PATTERN.match(line)
            if not domain:
                continue

            rule.domain_suffix.append(domain.group(1))

        rule.freeze()

        yield result
