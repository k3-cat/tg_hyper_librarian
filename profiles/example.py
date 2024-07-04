import json
from pathlib import Path

from providers.http import Http
from tg_hyper_librarian.formats import c2lu_json, c2luZy1ib3g
from tg_hyper_librarian.models import RuleSet
from tg_hyper_librarian.parsers.apnic import parse_apnic
from tg_hyper_librarian.parsers.c2luZy1ib3g import parse_c2luZy1ib3g
from tg_hyper_librarian.parsers.dnsmasq import parse_dnsmasq
from tg_hyper_librarian.parsers.maxmind import parse_maxmind

DNSMASQ_COMMON_LIST = [
    "https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/master/apple.china.conf",
    "https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/master/google.china.conf",
]

NTP_RULE_SET = "https://raw.githubusercontent.com/SagerNet/sing-geosite/rule-set/geosite-category-ntp.srs"

DNSMASQ_CHAINA_LIST = [
    "https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/master/accelerated-domains.china.conf",
]

CN_RULE_SET_LIST = [
    "https://raw.githubusercontent.com/SagerNet/sing-geosite/rule-set/geosite-geolocation-cn.srs",
    "https://raw.githubusercontent.com/SagerNet/sing-geoip/rule-set/geoip-cn.srs",
]

APNIC_DB = "https://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest"

MAXMIND_DB = "https://raw.githubusercontent.com/Dreamacro/maxmind-geoip/release/Country.mmdb"

# VOKINS_YHOSTS = "https://raw.githubusercontent.com/VeleSila/yhosts/master/hosts"

# ADGUARD_FILTER = "https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt"


EXTRA_COMMON_RULES = [
    {"ip_cidr": ["8.8.8.8", "8.8.4.4", "1.1.1.1"], "network": "udp"},
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
        ],
        "domain_suffix": [
            "weather.microsoft.com",
            "prod.do.dsp.mp.microsoft.com",
            "delivery.mp.microsoft.com",
            "windowsupdate.com",
            "update.microsoft.com",
            "download.microsoft.com",
            "windowsupdate.microsoft.com",
            "telemetry.microsoft.com",
            "events.data.microsoft.com",
            "download.nvidia.com",
            "gfe.nvidia.com",
        ],
    },
]


DIR = Path(__file__).parent / "rulesets"

if __name__ == "__main__":
    http = Http(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
        }
    )

    # - - - CN - - - - - -
    cn = RuleSet()
    for url in CN_RULE_SET_LIST:
        with http.fetch(url) as fp:
            cn.extend(parse_c2luZy1ib3g(fp))
    for url in DNSMASQ_CHAINA_LIST:
        with http.fetch(url) as fp:
            cn.extend(parse_dnsmasq(fp))
    with http.fetch(APNIC_DB) as fp:
        cn.extend(parse_apnic(fp, "CN"))
    with http.fetch(MAXMIND_DB) as fp:
        cn.extend(parse_maxmind(fp, "CN"))

    cn.reduce_all()
    with (DIR / "cn.json").open("+bw") as fp:
        c2lu_json.write_to_io(fp, cn)
    with (DIR / "cn.srs").open("+bw") as fp:
        c2luZy1ib3g.write_to_io(fp, cn)

    # - - - Common - - - - - -
    common = RuleSet()
    with http.fetch(NTP_RULE_SET) as fp:
        common.extend(parse_c2luZy1ib3g(fp))
    for url in DNSMASQ_COMMON_LIST:
        with http.fetch(url) as fp:
            common.extend(parse_dnsmasq(fp))

    common.reduce_all()
    with (DIR / "common.json").open("+bw") as fp:
        c2lu_json.write_to_io(fp, common)
    with (DIR / "common.srs").open("+bw") as fp:
        c2luZy1ib3g.write_to_io(fp, common)

    with (DIR / "common.json").open("r+", encoding="utf-8") as fp:
        rule_obj = json.load(fp)
        rule_obj["rules"].extend(EXTRA_COMMON_RULES)
        fp.seek(0)
        json.dump(rule_obj, fp, indent=2)
