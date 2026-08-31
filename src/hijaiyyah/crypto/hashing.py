"""
SHA-256 and canonical digests for hybit vectors.

The vector encoding used to be `bytes(v[0:18])`, one byte per component. That
raises ValueError the moment a component leaves 0..255, which is not an exotic
case: a string integral of about 110 letters already carries Θ̂ = 210, and any
difference vector can be negative. Components are now encoded as signed 32-bit
big-endian words, which covers everything the algebra can produce and keeps the
digest stable regardless of magnitude.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List

V18_DIM = 18
_WORD = 4  # bytes per component
_MIN = -(2 ** 31)
_MAX = 2 ** 31 - 1


class VectorRangeError(ValueError):
    """A component does not fit the canonical 32-bit encoding."""


def encode_vector(v: List[int]) -> bytes:
    """
    Canonical byte encoding of a hybit vector: 18 signed 32-bit big-endian
    words. Shorter vectors are rejected rather than silently zero-padded.
    """
    if len(v) < V18_DIM:
        raise VectorRangeError(
            f"vector has {len(v)} components, expected at least {V18_DIM}"
        )

    out = bytearray()
    for i, component in enumerate(v[:V18_DIM]):
        if not isinstance(component, int):
            raise VectorRangeError(
                f"component {i} is {type(component).__name__}, expected int"
            )
        if not _MIN <= component <= _MAX:
            raise VectorRangeError(
                f"component {i} = {component} does not fit a signed 32-bit word"
            )
        out += component.to_bytes(_WORD, "big", signed=True)
    return bytes(out)


def sha256_bytes(data: bytes) -> str:
    """SHA-256 hex digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_vector(v: List[int]) -> str:
    """SHA-256 of a hybit vector, over its canonical encoding."""
    return hashlib.sha256(encode_vector(v)).hexdigest()


def canonical_digest(obj: Dict[str, Any]) -> str:
    """SHA-256 of a canonicalized JSON object (sorted keys, no whitespace)."""
    encoded = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
