import tempfile

import maxminddb

from ..models import Group, RuleUnit
from .utils.http_client import get_content


def parse_maxmind(url: str, country_code: str) -> Group:
    result = RuleUnit()
    with tempfile.TemporaryFile(delete_on_close=False) as fp:  # type: ignore
        res = get_content(url)
        fp.write(res)
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

    return Group(result)
