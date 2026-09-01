"""
HISAB Validation — 3-level validation pipeline (§4.11–4.15).

Level 1 — Structural: magic, version, type, payload length, CRC32
Level 2 — Guard: G1–G4, T1–T2 on deserialized payload
Level 3 — Semantic: range check, Master Table cross-ref, guard consistency
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from ..core.guards import compute_U
from .digest import compute_digest
from .protocol import (
    DIGEST_SIZE,
    GUARD_SIZE,
    HEADER_SIZE,
    MAGIC,
    PAYLOAD_SIZES,
    VERSION,
    FrameType,
)
from .serialize import _compute_guard_status, _nibble_unpack

# ── Validation result ───────────────────────────────────────────

@dataclass(frozen=True)
class ValidationResult:
    """Result of a single validation check."""
    level: str       # "STRUCT", "GUARD", "SEMANTIC"
    code: str        # e.g. "S1_MAGIC", "G4_RHO_NEG"
    passed: bool
    detail: str = ""


@dataclass
class ValidationReport:
    """Complete 3-level validation report for a frame."""
    results: List[ValidationResult]

    @property
    def all_pass(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def failed(self) -> List[ValidationResult]:
        return [r for r in self.results if not r.passed]

    @property
    def level1_pass(self) -> bool:
        return all(r.passed for r in self.results if r.level == "STRUCT")

    @property
    def level2_pass(self) -> bool:
        return all(r.passed for r in self.results if r.level == "GUARD")

    @property
    def level3_pass(self) -> bool:
        return all(r.passed for r in self.results if r.level == "SEMANTIC")


# ── Level 1: Structural Validation (§4.12) ──────────────────────

# What a successful structural pass hands to the semantic level.
StructuralParse = Optional[Tuple[FrameType, bytes, int]]


def _validate_structural(data: bytes) -> Tuple[List[ValidationResult], StructuralParse]:
    """
    Level 1: structural checks S1–S5.

    Returns:
        (results, parsed) where parsed = (frame_type, payload, guard_byte) or None on failure.
    """
    results: List[ValidationResult] = []

    # S1: Magic bytes
    if len(data) < 2 or data[0:2] != MAGIC:
        got = data[0:2].hex() if len(data) >= 2 else "<too short>"
        results.append(ValidationResult("STRUCT", "S1_MAGIC", False,
                                        f"Expected 0x4842, got 0x{got}"))
        return results, None
    results.append(ValidationResult("STRUCT", "S1_MAGIC", True, "Magic = 'HB' ✓"))

    # S2: Version
    if len(data) < 3 or data[2] > VERSION:
        ver = data[2] if len(data) >= 3 else -1
        results.append(ValidationResult("STRUCT", "S2_VERSION", False,
                                        f"Unknown version: {ver}"))
        return results, None
    results.append(ValidationResult("STRUCT", "S2_VERSION", True,
                                    f"Version = {data[2]} ✓"))

    # S3: Type
    ftype_raw = data[3] if len(data) >= 4 else -1
    try:
        ftype = FrameType(ftype_raw)
    except ValueError:
        results.append(ValidationResult("STRUCT", "S3_TYPE", False,
                                        f"Invalid type: 0x{ftype_raw:02X}"))
        return results, None
    results.append(ValidationResult("STRUCT", "S3_TYPE", True,
                                    f"Type = {ftype.name} (0x{ftype_raw:02X}) ✓"))

    # S4: Payload length
    expected_payload = PAYLOAD_SIZES.get(ftype)
    actual_total = len(data)
    if expected_payload is not None:
        expected_total = HEADER_SIZE + expected_payload + GUARD_SIZE + DIGEST_SIZE
        if actual_total != expected_total:
            results.append(ValidationResult("STRUCT", "S4_LENGTH", False,
                                            f"Expected {expected_total} bytes, got {actual_total}"))
            return results, None
    results.append(ValidationResult("STRUCT", "S4_LENGTH", True,
                                    f"Length = {actual_total} bytes ✓"))

    # Extract payload and guard
    payload = data[HEADER_SIZE:-GUARD_SIZE - DIGEST_SIZE]
    guard_byte = data[-(GUARD_SIZE + DIGEST_SIZE)]

    # S5: CRC32
    digest_data = data[:-(DIGEST_SIZE)]
    stored_crc = struct.unpack("<I", data[-(DIGEST_SIZE):])[0]
    computed_crc = compute_digest(digest_data)
    if stored_crc != computed_crc:
        results.append(ValidationResult(
            "STRUCT", "S5_CRC32", False,
            f"CRC mismatch: stored=0x{stored_crc:08X}, computed=0x{computed_crc:08X}",
        ))
        return results, None
    results.append(ValidationResult("STRUCT", "S5_CRC32", True,
                                    f"CRC32 = 0x{computed_crc:08X} ✓"))

    return results, (ftype, payload, guard_byte)


# ── Level 2: Guard Validation (§4.13) ───────────────────────────

def _validate_guard(v: Sequence[int]) -> List[ValidationResult]:
    """Level 2: guard checks G1–G4, T1–T2 on deserialized v18."""
    results: List[ValidationResult] = []

    U = compute_U(v)
    rho = v[0] - U

    # G1: ρ ≥ 0
    if rho >= 0:
        results.append(ValidationResult("GUARD", "G1_RHO", True,
                                        f"ρ = {v[0]} − {U} = {rho} ≥ 0 ✓"))
    else:
        results.append(ValidationResult("GUARD", "G1_RHO_NEG", False,
                                        f"ρ = {v[0]} − {U} = {rho} < 0"))

    # G2: A_N = Na + Nb + Nd
    sum_n = v[1] + v[2] + v[3]
    if v[14] == sum_n:
        results.append(ValidationResult("GUARD", "G2_AN", True,
                                        f"A_N = {v[14]} = {v[1]}+{v[2]}+{v[3]} ✓"))
    else:
        results.append(ValidationResult("GUARD", "G2_AN", False,
                                        f"A_N = {v[14]} ≠ {v[1]}+{v[2]}+{v[3]} = {sum_n}"))

    # G3: A_K = Kp + Kx + Ks + Ka + Kc
    sum_k = v[4] + v[5] + v[6] + v[7] + v[8]
    if v[15] == sum_k:
        results.append(ValidationResult("GUARD", "G3_AK", True,
                                        f"A_K = {v[15]} = ΣK = {sum_k} ✓"))
    else:
        results.append(ValidationResult("GUARD", "G3_AK", False,
                                        f"A_K = {v[15]} ≠ ΣK = {sum_k}"))

    # G4: A_Q = Qp + Qx + Qs + Qa + Qc
    sum_q = v[9] + v[10] + v[11] + v[12] + v[13]
    if v[16] == sum_q:
        results.append(ValidationResult("GUARD", "G4_AQ", True,
                                        f"A_Q = {v[16]} = ΣQ = {sum_q} ✓"))
    else:
        results.append(ValidationResult("GUARD", "G4_AQ", False,
                                        f"A_Q = {v[16]} ≠ ΣQ = {sum_q}"))

    # T1: Ks > 0 ⇒ Qc ≥ 1
    if v[6] == 0 or v[13] >= 1:
        results.append(ValidationResult("GUARD", "T1", True,
                                        f"T1: Ks={v[6]}, Qc={v[13]} ✓"))
    else:
        results.append(ValidationResult("GUARD", "T1", False,
                                        f"T1: Ks={v[6]}>0 but Qc={v[13]}<1"))

    # T2: Kc > 0 ⇒ Qc ≥ 1
    if v[8] == 0 or v[13] >= 1:
        results.append(ValidationResult("GUARD", "T2", True,
                                        f"T2: Kc={v[8]}, Qc={v[13]} ✓"))
    else:
        results.append(ValidationResult("GUARD", "T2", False,
                                        f"T2: Kc={v[8]}>0 but Qc={v[13]}<1"))

    return results


# ── Level 3: Semantic Validation (§4.14) ─────────────────────────

def _validate_semantic(
    v: Sequence[int],
    ftype: FrameType,
    guard_byte: int,
    master_vectors: Optional[List[Tuple[int, ...]]] = None,
) -> List[ValidationResult]:
    """Level 3: semantic checks M1–M3."""
    results: List[ValidationResult] = []

    # M1: Range check per component
    max_ranges = [8, 3, 1, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 5, 5, 1]
    range_ok = True
    for i, val in enumerate(v):
        if ftype == FrameType.LETTER and val > max_ranges[i]:
            results.append(ValidationResult("SEMANTIC", "M1_RANGE", False,
                                            f"v[{i}] = {val} > max {max_ranges[i]}"))
            range_ok = False
            break
    if range_ok:
        results.append(ValidationResult("SEMANTIC", "M1_RANGE", True,
                                        "All components within range ✓"))

    # M2: Cross-reference Master Table (LETTER only)
    if ftype == FrameType.LETTER and master_vectors is not None:
        found = tuple(v) in [mv for mv in master_vectors]
        if found:
            results.append(ValidationResult("SEMANTIC", "M2_TABLE", True,
                                            "Vector found in Master Table ✓"))
        else:
            results.append(ValidationResult("SEMANTIC", "M2_TABLE", False,
                                            "Vector not found in Master Table"))

    # M3: Guard status consistency
    recomputed = _compute_guard_status(v)
    if guard_byte == recomputed:
        results.append(ValidationResult("SEMANTIC", "M3_GUARD_STATUS", True,
                                        f"Guard status byte 0x{guard_byte:02X} consistent ✓"))
    else:
        results.append(ValidationResult("SEMANTIC", "M3_GUARD_STATUS", False,
                                        f"Guard status mismatch: stored=0x{guard_byte:02X}, "
                                        f"computed=0x{recomputed:02X}"))

    return results


# ── Full validation pipeline (§4.11) ────────────────────────────

def validate_frame(
    data: bytes,
    master_vectors: Optional[List[Tuple[int, ...]]] = None,
) -> ValidationReport:
    """
    Run full 3-level HISAB validation pipeline on raw frame bytes.

    Args:
        data:            Raw HISAB frame bytes.
        master_vectors:  List of valid v18 tuples for M2 cross-reference.

    Returns:
        ValidationReport with results from all levels.
    """
    all_results: List[ValidationResult] = []

    # Level 1: Structural
    struct_results, parsed = _validate_structural(data)
    all_results.extend(struct_results)

    if parsed is None:
        return ValidationReport(results=all_results)

    ftype, payload, guard_byte = parsed

    # Deserialize payload to v18
    if ftype == FrameType.LETTER:
        v = _nibble_unpack(payload)
    elif ftype == FrameType.STRING:
        import struct as _struct
        components: List[int] = []
        for i in range(18):
            offset = 3 + i * 2  # skip 3-byte ext header
            components.append(_struct.unpack("<H", payload[offset:offset + 2])[0])
        v = tuple(components)
    else:
        return ValidationReport(results=all_results)

    # Level 2: Guard
    guard_results = _validate_guard(v)
    all_results.extend(guard_results)

    # Level 3: Semantic
    semantic_results = _validate_semantic(v, ftype, guard_byte, master_vectors)
    all_results.extend(semantic_results)

    return ValidationReport(results=all_results)
