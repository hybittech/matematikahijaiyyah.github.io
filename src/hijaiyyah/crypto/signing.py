"""
HMAC-SHA256 signing and verification.

Vectors are signed over the canonical encoding from hashing.py rather than
`bytes(v[0:18])`, which could not represent a component outside 0..255.
"""

from __future__ import annotations

import hashlib
import hmac
from typing import List

from .hashing import encode_vector


def sign_bytes(data: bytes, key: bytes) -> bytes:
    """Sign arbitrary bytes with HMAC-SHA256."""
    return hmac.new(key, data, hashlib.sha256).digest()


def verify_bytes(data: bytes, key: bytes, sig: bytes) -> bool:
    """Verify a signature over arbitrary bytes, in constant time."""
    return hmac.compare_digest(sign_bytes(data, key), sig)


def sign(v: List[int], key: bytes) -> bytes:
    """Sign a hybit vector with HMAC-SHA256."""
    return sign_bytes(encode_vector(v), key)


def verify(v: List[int], key: bytes, sig: bytes) -> bool:
    """Verify a hybit vector's signature, in constant time."""
    return hmac.compare_digest(sign(v, key), sig)
