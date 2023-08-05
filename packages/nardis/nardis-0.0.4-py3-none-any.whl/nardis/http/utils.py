from typing import List, Tuple
from nardis.utils import decode_string
from urllib.parse import parse_qs as libparse_qs



def parse_cookie(cookie: str) -> dict:
    if cookie:
        return {
            y[0]: y[1]
            for y in [
                x.split("=") for x in cookie.split("; ")
            ]
        }
    return {}


def parse_headers(headers: List[Tuple[bytes, bytes]]):
    return {decode_string(k): decode_string(v) for (k, v) in headers}


def parse_qs(qs: bytes):
    return {
        decode_string(k): [*map(decode_string, v)]
        for k, v in libparse_qs(qs).items()
    }
