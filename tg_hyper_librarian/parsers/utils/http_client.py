import ssl
import urllib
import urllib.error
import urllib.request


def get_content(url: str) -> bytes:
    ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    with urllib.request.urlopen(url, context=ctx) as res:
        try:
            return res.read()
        except urllib.error.HTTPError as ex:
            print(f"Failed at:{url} ({ex.code}){ex.reason} {ex.read().decode("utf-8")}")
            raise ex
