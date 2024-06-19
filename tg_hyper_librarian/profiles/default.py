import json
from pathlib import Path

from ..formats.json import dump_to_json
from ..models import Group, RuleUnit
from ..parsers.apnic import parse_apnic
from ..parsers.dnsmasq import parse_dnsmasq
from ..parsers.maxmind import parse_maxmind

DNSMASQ_CHINA_COMMON = [
    "https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/master/apple.china.conf",
    "https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/master/google.china.conf",
]

DNSMASQ_CHAINA_LIST = (
    "https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/master/accelerated-domains.china.conf"
)

APNIC_DB = "https://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest"

MAXMIND_DB = "https://raw.githubusercontent.com/Dreamacro/maxmind-geoip/release/Country.mmdb"

# VOKINS_YHOSTS = "https://raw.githubusercontent.com/VeleSila/yhosts/master/hosts"

# ADGUARD_FILTER = "https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt"


EXTRA_COMMON_RULES = [
    {"ip_cidr": ["8.8.8.8", "8.8.4.4", "1.1.1.1"], "network": "udp"},
    {
        "domain_regex": [
            "^time(.euro)?.apple.com$",
            "^time([1-5])?.facebook.com$",
            "^time([1-4])?.google.com$",
            "^((((ut1-wwv)|(ntp\\-(b|d|wwv))|(time(\\-(([a-e]\\-(g|b))|([a-e]\\-wwv)))?)).nist.gov)|((ntp-c|ut1-time)|(utcnist(2|3)?)).colorado.edu)$",
            "^ntp[0-7].ntp-servers.net$",
        ]
    },
    {
        "domain": [
            "adl.windows.com",
            "tsfe.trafficshaping.dsp.mp.microsoft.com",
            "arc.msn.com",
            "ris.api.iris.microsoft.com",
            "asset.msn.com",
            "browser.events.data.msn.com",
            "img-s-msn-com.akamaized.net",
            "prod.otel.kaizen.nvidia.com",
            "clock.isc.org",
            "ntp.fiord.ru",
            "ntp.nat.ms",
            "ntp.nic.cz",
            "ntp.nict.jp",
            "ntp.ripe.net",
            "ntp.se",
            "ntp.ufe.cz",
            "pool.ntp.org",
            "time.cloudflare.com",
            "time.nrc.ca",
            "time.windows.com",
        ],
        "domain_suffix": [
            ".weather.microsoft.com",
            ".prod.do.dsp.mp.microsoft.com",
            ".delivery.mp.microsoft.com",
            ".windowsupdate.com",
            ".update.microsoft.com",
            ".download.microsoft.com",
            ".windowsupdate.microsoft.com",
            ".telemetry.microsoft.com",
            ".events.data.microsoft.com",
            ".download.nvidia.com",
            ".gfe.nvidia.com",
        ],
    },
]


def generate_at(root_dir: Path):
    cn_result = RuleUnit()
    cn_result.reduce(parse_dnsmasq(DNSMASQ_CHAINA_LIST)[0])
    cn_result.reduce(parse_apnic(APNIC_DB, "CN")[0])
    cn_result.reduce(parse_maxmind(MAXMIND_DB, "CN")[0])
    with open(root_dir / "cn.json", "wb") as fp:
        fp.write(dump_to_json(Group(cn_result)))

    common = RuleUnit()
    for url in DNSMASQ_CHINA_COMMON:
        common.reduce(parse_dnsmasq(url)[0])
    with (root_dir / "common.json").open("wb") as fp:
        fp.write(dump_to_json(Group(common)))
    with (root_dir / "common.json").open("r+", encoding="utf-8") as fp:
        rule_obj = json.load(fp)
        rule_obj["rules"].extend(EXTRA_COMMON_RULES)
        fp.seek(0)
        json.dump(rule_obj, fp, indent=2)
