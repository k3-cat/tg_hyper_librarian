from io import BytesIO

from ..formats.c2luZy1ib3g import load_from_c2luZy1ib3g
from ..models.operators import Group
from .utils.http_client import get_content


def parse_c2luZy1ib3g(url: str) -> Group:
    s = BytesIO(get_content(url))
    result = load_from_c2luZy1ib3g(s)
    return result
