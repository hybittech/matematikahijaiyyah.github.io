"""
HISAB Protocol — Frame types, constants, and data structures.

Implements §4.5–4.9 of:
  - Magic bytes, version, frame types
  - HisabFrame dataclass
  - Guard status bitmask
  - Canonical byte/nibble order
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import IntEnum
from typing import Tuple

# ── Magic & Version (§4.5.2, §4.5.3) ────────────────────────────

MAGIC = b"\x48\x42"  # "HB" — Hybit
VERSION = 0x01        # HISAB v1.0

# ── Frame Types (§4.5.4) ────────────────────────────────────────

class FrameType(IntEnum):
    """HISAB frame type codes."""
    LETTER  = 0x01  # Single hybit (nibble-packed 9 bytes)
    STRING  = 0x02  # Aggregated codex (word-packed 36 bytes)
    MATRIX  = 0x03  # Exomatrix 5×5 (25 bytes)
    DELTA   = 0x04  # Difference of two hybits (36 bytes signed)
    PATH    = 0x05  # Cumulative path Sₖ (variable)
    TABLE   = 0x06  # Full Master Table (252 bytes)


# ── Payload sizes (§4.6–4.8) ────────────────────────────────────

PAYLOAD_SIZES = {
    FrameType.LETTER: 9,
    FrameType.STRING: 39,   # 3 byte ext header + 36 byte payload
    FrameType.MATRIX: 26,   # 25 byte cells + 1 byte relation flags
    FrameType.TABLE:  252,
}

HEADER_SIZE = 4       # magic(2) + version(1) + type(1)
GUARD_SIZE = 1        # guard status bitmask
DIGEST_SIZE = 4       # CRC32

# ── Guard Status Bitmask (§4.5.1) ───────────────────────────────

GUARD_G1_BIT = 0  # ρ ≥ 0
GUARD_G2_BIT = 1  # A_N = Na + Nb + Nd
GUARD_G3_BIT = 2  # A_K = Kp + Kx + Ks + Ka + Kc
GUARD_G4_BIT = 3  # A_Q = Qp + Qx + Qs + Qa + Qc
GUARD_T1_BIT = 4  # Ks > 0 ⇒ Qc ≥ 1
GUARD_T2_BIT = 5  # Kc > 0 ⇒ Qc ≥ 1

ALL_GUARDS_PASS = 0x3F  # bits 0–5 all set


# ── HisabFrame (§4.5.1) ────────────────────────────────────────

@dataclass(frozen=True)
class HisabFrame:
    """
    HISAB Frame — the canonical interchange unit.

    Fields:
      frame_type:    FrameType enum
      payload:       raw payload bytes
      guard_status:  bitmask byte (bits 0–5 = G1–G4, T1, T2)
      digest:        CRC32 of header + payload + guard_status
    """
    frame_type: FrameType
    payload: bytes
    guard_status: int
    digest: int

    def to_bytes(self) -> bytes:
        """Serialize to canonical HISAB byte sequence."""
        header = MAGIC + bytes([VERSION, self.frame_type])
        guard = bytes([self.guard_status])
        crc = struct.pack("<I", self.digest)
        return header + self.payload + guard + crc

    @property
    def total_size(self) -> int:
        return HEADER_SIZE + len(self.payload) + GUARD_SIZE + DIGEST_SIZE

    def hex_dump(self, sep: str = " ") -> str:
        """Pretty hex dump of the full frame."""
        return sep.join(f"{b:02X}" for b in self.to_bytes())


# ── Component ordering for nibble-packing (§4.6.1) ──────────────
# Index into v18: pairs of (high_nibble_idx, low_nibble_idx) per byte

NIBBLE_PAIRS: Tuple[Tuple[int, int], ...] = (
    (0,  1),   # B0: Θ̂ | Na
    (2,  3),   # B1: Nb | Nd
    (4,  5),   # B2: Kp | Kx
    (6,  7),   # B3: Ks | Ka
    (8,  9),   # B4: Kc | Qp
    (10, 11),  # B5: Qx | Qs
    (12, 13),  # B6: Qa | Qc
    (14, 15),  # B7: A_N | A_K
    (16, 17),  # B8: A_Q | H*
)
