from .constants import ENCODING


def encode_string(s: str, charset=ENCODING) -> bytes:
    """Encodes a unicode string to bytes"""
    return s.encode(charset)


def decode_string(b: bytes, charset=ENCODING) -> str:
    """Decodes bytes to a unicode string"""
    return b.decode(charset)
