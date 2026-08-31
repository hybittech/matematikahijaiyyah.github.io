"""
HISAB Digest — CRC32 integrity computation (§4.10).

Two-level integrity:
  Level 1 (Transport): CRC32 detects bit corruption
  Level 2 (Geometric): Guard checks detect structural inconsistency
"""

from __future__ import annotations

import struct
import zlib


def compute_digest(data: bytes) -> int:
    """
    Compute HISAB CRC32 digest over header + payload + guard_status.

    Returns unsigned 32-bit integer.
    """
    return zlib.crc32(data) & 0xFFFFFFFF


def pack_digest(digest: int) -> bytes:
    """Pack digest as 4 bytes little-endian."""
    return struct.pack("<I", digest)


def verify_digest(frame_bytes: bytes) -> bool:
    """
    Verify CRC32 digest of a complete HISAB frame.

    The last 4 bytes are the stored digest; everything before
    (header + payload + guard_status) is the data to hash.
    """
    if len(frame_bytes) < 9:  # minimum: 4 header + 0 payload + 1 guard + 4 crc
        return False
    data = frame_bytes[:-4]
    stored = struct.unpack("<I", frame_bytes[-4:])[0]
    return bool(compute_digest(data) == stored)
