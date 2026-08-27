"""HMAC-SHA256 signing and verification for hybit vectors."""

from __future__ import annotations

import hashlib
import hmac
from typing import List


def sign(v: List[int], key: bytes) -> bytes:
    """Sign hybit vector with HMAC-SHA256."""
    raw = bytes(v[0:18])  # type: ignore[index]
    return hmac.new(key, raw, hashlib.sha256).digest()


def verify(v: List[int], key: bytes, sig: bytes) -> bool:
    """Verify HMAC-SHA256 signature of hybit vector."""
    return hmac.compare_digest(sign(v, key), sig)
