import logging
from typing import TYPE_CHECKING

from tg_h_l_.dto import AllOf, RulePack, SimpleRule
from tg_h_l_.formates._base import ReadableFormat

if TYPE_CHECKING:
    from tg_aio._buffered_base import AsyncBufferedReader


class AdGuard(ReadableFormat[str]):
    async def load(self, fp: AsyncBufferedReader[str]):
        positive_rule = SimpleRule()
        negative_rule = SimpleRule(is_inverted=True)

        inner_rule = AllOf(rules=[positive_rule, negative_rule])
        inner_rule.freeze()

        result = RulePack(rules=[inner_rule])
        result.freeze()

        async for line in fp.readlines():
            line = line.strip()
            # line_.startswith("!") or line_.startswith("#") or line_.startswith("@@")
            if (not line) or (line[0] in {"!", "#"}) or ("*" in line) or ("?" in line):
                continue

            if line.endswith("$important"):
                line = line[:-10]

            # unblock
            if line.startswith("@@||"):
                if line.endswith("^|"):
                    negative_rule.domain_suffix.append(line[4:-2])
                elif line.endswith("^"):
                    negative_rule.domain_suffix.append(line[4:-1])
                else:
                    logging.warning(line)

            elif line.startswith("@@|"):
                if line.endswith("^|"):
                    negative_rule.domain.append(line[3:-2])
                elif line.endswith("^"):
                    negative_rule.domain.append(line[3:-1])
                else:
                    logging.warning(line)

            elif line.startswith("@@"):
                if line.endswith("^|"):
                    negative_rule.domain_suffix.append(line[2:-2])
                elif line.endswith("^"):
                    negative_rule.domain_suffix.append(line[2:-1])
                else:
                    logging.warning(line)

            # block
            elif line.startswith("://"):
                if line.endswith("^"):
                    positive_rule.domain.append(line[3:-1])
                else:
                    logging.warning(line)

            elif line.startswith("||"):
                if line.endswith("^"):
                    positive_rule.domain_suffix.append(line[2:-1])
                else:
                    positive_rule.domain_keyword.append(line[2:])

            elif line.startswith("|"):
                if line.endswith("^"):
                    positive_rule.domain.append(line[1:-1])
                else:
                    positive_rule.domain_keyword.append(line[1:])

            else:
                if line.endswith("^"):
                    positive_rule.domain_suffix.append(line)

        positive_rule.freeze()
        negative_rule.freeze()

        yield result
