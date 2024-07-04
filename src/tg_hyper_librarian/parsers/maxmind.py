from tempfile import TemporaryFile
from typing import BinaryIO

import maxminddb

from ..models import RuleSet, RuleUnit


def parse_maxmind(sp: BinaryIO, country_code: str) -> RuleSet:
    result = RuleUnit()
    with TemporaryFile(delete_on_close=False) as fp:  # type: ignore
        fp.write(sp.read())
        fp.close()

        with maxminddb.open_database(fp.name) as reader:
            for cidr, record in reader:
                key = "country"
                if key not in record:  # type: ignore
                    key = "registered_country"
                    if key not in record:  # type: ignore
                        continue
                if record[key]["iso_code"] != country_code:  # type: ignore
                    continue
                if cidr.version == 4:
                    result.ipv4_cidrs.append(cidr)
                elif cidr.version == 6:
                    result.ipv6_cidrs.append(cidr)
                else:
                    print("Unknown ip version", cidr)

    return RuleSet(result)
