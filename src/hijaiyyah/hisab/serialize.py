"""
HISAB Serialization — Canonical encoding per §4.6–4.8.

Implements:
  - LETTER Frame: nibble-packed 9 bytes (§4.6.1)
  - STRING Frame: word-packed 36 bytes + 3-byte ext header (§4.7.1)
  - MATRIX Frame: 25 bytes row-major + 1 relation flag byte (§4.8.1)
  - Deserialization for all frame types
"""

from __future__ import annotations

import struct
from typing import List, Optional, Sequence, Tuple, Union

from ..core.guards import compute_U
from .digest import compute_digest
from .protocol import (
    GUARD_G1_BIT,
    GUARD_G2_BIT,
    GUARD_G3_BIT,
    GUARD_G4_BIT,
    GUARD_T1_BIT,
    GUARD_T2_BIT,
    MAGIC,
    NIBBLE_PAIRS,
    VERSION,
    FrameType,
    HisabFrame,
)

# ── Guard status computation ────────────────────────────────────

def _compute_guard_status(v: Sequence[int]) -> int:
    """
    Compute guard status bitmask for a v18 vector.
    Bits 0–5: G1, G2, G3, G4, T1, T2 (§4.13).
    """
    status = 0

    # G1: ρ = Θ̂ − U ≥ 0
    U = compute_U(v)
    rho = v[0] - U
    if rho >= 0:
        status |= (1 << GUARD_G1_BIT)

    # G2: A_N = Na + Nb + Nd
    if v[14] == v[1] + v[2] + v[3]:
        status |= (1 << GUARD_G2_BIT)

    # G3: A_K = Kp + Kx + Ks + Ka + Kc
    if v[15] == v[4] + v[5] + v[6] + v[7] + v[8]:
        status |= (1 << GUARD_G3_BIT)

    # G4: A_Q = Qp + Qx + Qs + Qa + Qc
    if v[16] == v[9] + v[10] + v[11] + v[12] + v[13]:
        status |= (1 << GUARD_G4_BIT)

    # T1: Ks > 0 ⇒ Qc ≥ 1
    if v[6] == 0 or v[13] >= 1:
        status |= (1 << GUARD_T1_BIT)

    # T2: Kc > 0 ⇒ Qc ≥ 1
    if v[8] == 0 or v[13] >= 1:
        status |= (1 << GUARD_T2_BIT)

    return status


# ── LETTER Frame serialization (§4.6.1) ─────────────────────────

def _nibble_pack(v: Sequence[int]) -> bytes:
    """Pack 18 components into 9 bytes using nibble-packing."""
    result = bytearray(9)
    for i, (hi_idx, lo_idx) in enumerate(NIBBLE_PAIRS):
        result[i] = ((v[hi_idx] & 0x0F) << 4) | (v[lo_idx] & 0x0F)
    return bytes(result)


def _nibble_unpack(data: bytes) -> Tuple[int, ...]:
    """Unpack 9 nibble-packed bytes into 18 components."""
    result: List[int] = []
    for i, (_, _) in enumerate(NIBBLE_PAIRS):
        result.append((data[i] >> 4) & 0x0F)
        result.append(data[i] & 0x0F)
    return tuple(result)


def serialize_letter(v18: Sequence[int]) -> HisabFrame:
    """
    Serialize a single hybit v18 vector into a HISAB LETTER Frame.

    Args:
        v18: 18-element sequence of non-negative integers.

    Returns:
        HisabFrame with type=LETTER, nibble-packed payload.
    """
    if len(v18) != 18:
        raise ValueError(f"Expected 18 components, got {len(v18)}")

    payload = _nibble_pack(v18)
    guard_status = _compute_guard_status(v18)

    header = MAGIC + bytes([VERSION, FrameType.LETTER])
    digest_data = header + payload + bytes([guard_status])
    digest = compute_digest(digest_data)

    return HisabFrame(
        frame_type=FrameType.LETTER,
        payload=payload,
        guard_status=guard_status,
        digest=digest,
    )


# ── STRING Frame serialization (§4.7.1) ─────────────────────────

def serialize_string(cod18: Sequence[int], n: int, *, letter_list: bool = False) -> HisabFrame:
    """
    Serialize an aggregated codex vector into a HISAB STRING Frame.

    Args:
        cod18:       18-element aggregated codex vector.
        n:           Number of letters in the original string.
        letter_list: Whether the frame includes a letter list.

    Returns:
        HisabFrame with type=STRING, word-packed payload.
    """
    if len(cod18) != 18:
        raise ValueError(f"Expected 18 components, got {len(cod18)}")

    # Extended header: n (2 bytes LE) + letter_list flag (1 byte)
    ext_header = struct.pack("<H", n) + bytes([0x01 if letter_list else 0x00])

    # Word-packed: 18 × 2 bytes (unsigned 16-bit LE)
    word_data = b"".join(struct.pack("<H", c & 0xFFFF) for c in cod18)

    payload = ext_header + word_data
    guard_status = _compute_guard_status(cod18)

    header = MAGIC + bytes([VERSION, FrameType.STRING])
    digest_data = header + payload + bytes([guard_status])
    digest = compute_digest(digest_data)

    return HisabFrame(
        frame_type=FrameType.STRING,
        payload=payload,
        guard_status=guard_status,
        digest=digest,
    )


# ── MATRIX Frame serialization (§4.8.1) ─────────────────────────

def serialize_matrix(matrix: Sequence[Sequence[int]], v18: Sequence[int]) -> HisabFrame:
    """
    Serialize a 5×5 exomatrix into a HISAB MATRIX Frame.

    Args:
        matrix: 5×5 list of lists (row-major).
        v18:    Original v18 vector (for guard computation).

    Returns:
        HisabFrame with type=MATRIX.
    """
    # 25 bytes: row-major cell values
    cells = bytearray()
    for row in matrix:
        for val in row:
            cells.append(val & 0xFF)

    # Relation-flag byte (§4.8.2): R1–R5
    U = compute_U(v18)
    rho = v18[0] - U
    a_n = v18[1] + v18[2] + v18[3]
    a_k = v18[4] + v18[5] + v18[6] + v18[7] + v18[8]
    a_q = v18[9] + v18[10] + v18[11] + v18[12] + v18[13]

    rel_flags = 0
    if v18[0] == U + rho:
        rel_flags |= (1 << 0)  # R1
    if v18[14] == a_n:
        rel_flags |= (1 << 1)  # R2
    if v18[15] == a_k:
        rel_flags |= (1 << 2)  # R3
    if v18[16] == a_q:
        rel_flags |= (1 << 3)  # R4
    if U == compute_U(v18):
        rel_flags |= (1 << 4)  # R5

    payload = bytes(cells) + bytes([rel_flags])
    guard_status = _compute_guard_status(v18)

    header = MAGIC + bytes([VERSION, FrameType.MATRIX])
    digest_data = header + payload + bytes([guard_status])
    digest = compute_digest(digest_data)

    return HisabFrame(
        frame_type=FrameType.MATRIX,
        payload=payload,
        guard_status=guard_status,
        digest=digest,
    )


# ── Deserialization ─────────────────────────────────────────────

def deserialize_letter_payload(payload: bytes) -> Tuple[int, ...]:
    """Deserialize LETTER payload (9 nibble-packed bytes) → 18-tuple."""
    if len(payload) != 9:
        raise ValueError(f"LETTER payload must be 9 bytes, got {len(payload)}")
    return _nibble_unpack(payload)


def deserialize_string_payload(payload: bytes) -> Tuple[int, Tuple[int, ...]]:
    """
    Deserialize STRING payload → (n, 18-tuple).

    Returns:
        (n, cod18) where n = number of letters, cod18 = aggregated vector.
    """
    if len(payload) < 39:
        raise ValueError(f"STRING payload must be ≥39 bytes, got {len(payload)}")
    n = struct.unpack("<H", payload[0:2])[0]
    # Skip letter_list flag at byte 2
    components: List[int] = []
    for i in range(18):
        offset = 3 + i * 2
        components.append(struct.unpack("<H", payload[offset:offset + 2])[0])
    return n, tuple(components)


# A decoded payload is either a bare 18-component vector or an indexed one.
FramePayload = Union[Tuple[int, ...], Tuple[int, Tuple[int, ...]]]


def deserialize_frame(data: bytes) -> Optional[Tuple[FrameType, FramePayload]]:
    """
    Deserialize a complete HISAB frame from raw bytes.

    Returns:
        (frame_type, deserialized_data) or None on structural failure.
        For LETTER: data is Tuple[int, ...] (18 components)
        For STRING: data is (n, Tuple[int, ...])
    """
    if len(data) < 9:
        return None
    if data[0:2] != MAGIC:
        return None
    if data[2] != VERSION:
        return None

    ftype_raw = data[3]
    try:
        ftype = FrameType(ftype_raw)
    except ValueError:
        return None

    # Extract payload (between header and guard+digest)
    payload = data[4:-5]  # skip header(4), guard(1)+digest(4) at end
    guard_byte = data[-5]  # noqa: F841

    if ftype == FrameType.LETTER:
        if len(payload) != 9:
            return None
        return ftype, _nibble_unpack(payload)

    if ftype == FrameType.STRING:
        if len(payload) < 39:
            return None
        n = struct.unpack("<H", payload[0:2])[0]
        components: List[int] = []
        for i in range(18):
            offset = 3 + i * 2
            components.append(struct.unpack("<H", payload[offset:offset + 2])[0])
        return ftype, (n, tuple(components))

    return None
