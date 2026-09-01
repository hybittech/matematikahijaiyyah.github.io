"""Tests for the HISAB protocol."""

import struct

import pytest

from hijaiyyah.core.master_table import MASTER_TABLE
from hijaiyyah.hisab.digest import compute_digest, verify_digest
from hijaiyyah.hisab.protocol import (
    ALL_GUARDS_PASS,
    MAGIC,
    VERSION,
    FrameType,
)
from hijaiyyah.hisab.serialize import (
    deserialize_letter_payload,
    deserialize_string_payload,
    serialize_letter,
    serialize_string,
)
from hijaiyyah.hisab.validate import validate_frame


@pytest.fixture
def all_entries():
    return MASTER_TABLE.all_entries()


@pytest.fixture
def master_vectors(all_entries):
    return [tuple(e.vector) for e in all_entries]


@pytest.fixture
def ba():
    return MASTER_TABLE.get_by_char("ب")


@pytest.fixture
def haa():
    return MASTER_TABLE.get_by_char("هـ")


# ── Theorem 4.23.1: Round-Trip Fidelity ─────────────────────────

class TestRoundTripFidelity:
    """D(S(h*)) = h* for all h* ∈ V."""

    def test_all_28_letters(self, all_entries):
        for entry in all_entries:
            v18 = tuple(entry.vector)
            frame = serialize_letter(v18)
            recovered = deserialize_letter_payload(frame.payload)
            assert recovered == v18, (
                f"Round-trip failed for {entry.char} ({entry.name}): "
                f"original={list(v18)}, recovered={list(recovered)}"
            )

    def test_ba_specifically(self, ba):
        v18 = tuple(ba.vector)
        frame = serialize_letter(v18)
        recovered = deserialize_letter_payload(frame.payload)
        assert recovered == v18

    def test_haa_specifically(self, haa):
        v18 = tuple(haa.vector)
        frame = serialize_letter(v18)
        recovered = deserialize_letter_payload(frame.payload)
        assert recovered == v18


# ── Corollary 4.23.1: Injectivity ───────────────────────────────

class TestInjectivity:
    """h₁* ≠ h₂* ⟹ S(h₁*) ≠ S(h₂*)."""

    def test_all_28_unique_frames(self, all_entries):
        frames = set()
        for entry in all_entries:
            frame = serialize_letter(entry.vector)
            raw = frame.to_bytes()
            assert raw not in frames, f"Collision for {entry.char}"
            frames.add(raw)
        assert len(frames) == 28


# ── Theorem 4.24.1: Guard Preservation ──────────────────────────

class TestGuardPreservation:
    """h* ∈ V ⟹ G(S(h*)) = PASS."""

    def test_all_28_guard_pass(self, all_entries):
        for entry in all_entries:
            frame = serialize_letter(entry.vector)
            assert frame.guard_status == ALL_GUARDS_PASS, (
                f"Guard failed for {entry.char}: 0x{frame.guard_status:02X}"
            )


# ── Structural Validation (§4.12) ───────────────────────────────

class TestStructuralValidation:
    def test_rejects_bad_magic(self, ba, master_vectors):
        frame = serialize_letter(ba.vector)
        raw = bytearray(frame.to_bytes())
        raw[0] = 0x00
        raw[1] = 0x00
        report = validate_frame(bytes(raw), master_vectors)
        assert not report.all_pass
        assert any(r.code == "S1_MAGIC" and not r.passed for r in report.results)

    def test_rejects_bad_version(self, ba, master_vectors):
        frame = serialize_letter(ba.vector)
        raw = bytearray(frame.to_bytes())
        raw[2] = 0xFF
        report = validate_frame(bytes(raw), master_vectors)
        assert not report.all_pass
        assert any(r.code == "S2_VERSION" and not r.passed for r in report.results)

    def test_rejects_bad_type(self, ba, master_vectors):
        frame = serialize_letter(ba.vector)
        raw = bytearray(frame.to_bytes())
        raw[3] = 0xFE
        report = validate_frame(bytes(raw), master_vectors)
        assert not report.all_pass

    def test_rejects_bad_crc(self, ba, master_vectors):
        frame = serialize_letter(ba.vector)
        raw = bytearray(frame.to_bytes())
        raw[-1] ^= 0xFF  # corrupt CRC
        report = validate_frame(bytes(raw), master_vectors)
        assert not report.all_pass
        assert any(r.code == "S5_CRC32" and not r.passed for r in report.results)


# ── Guard Validation (§4.13) ────────────────────────────────────

class TestGuardValidation:
    def test_valid_frame_passes_all(self, ba, master_vectors):
        frame = serialize_letter(ba.vector)
        report = validate_frame(frame.to_bytes(), master_vectors)
        assert report.all_pass

    def test_corrupted_payload_detected(self, haa, master_vectors):
        """§4.33: Corruption of Qc in هـ triggers multiple failures."""
        frame = serialize_letter(haa.vector)
        raw = bytearray(frame.to_bytes())
        # Corrupt byte B6 (Qa|Qc) in payload: index 4+6 = 10
        raw[10] = 0x03  # Qa=0, Qc=3 instead of Qa=0, Qc=2
        # Recompute CRC to bypass Level 1 and test Level 2
        data = bytes(raw[:-(4)])  # header + payload + guard
        new_crc = compute_digest(data)
        struct.pack_into("<I", raw, len(raw) - 4, new_crc)
        # But guard status byte is now stale → should trigger M3
        report = validate_frame(bytes(raw), master_vectors)
        assert not report.all_pass


# ── STRING Frame ────────────────────────────────────────────────

class TestStringFrame:
    def test_bsm_round_trip(self):
        """Round-trip for string 'بسم'."""
        table = MASTER_TABLE
        ba = table.get_by_char("ب")
        sin = table.get_by_char("س")
        mim = table.get_by_char("م")
        assert ba is not None and sin is not None and mim is not None

        cod = tuple(
            ba.vector[i] + sin.vector[i] + mim.vector[i] for i in range(18)
        )
        frame = serialize_string(cod, 3)
        assert frame.frame_type == FrameType.STRING
        assert frame.guard_status == ALL_GUARDS_PASS

        n, recovered = deserialize_string_payload(frame.payload)
        assert n == 3
        assert recovered == cod

    def test_string_guard_preservation(self):
        """Guard constraints preserved on aggregation (Theorem 3.9.1)."""
        table = MASTER_TABLE
        entries = table.all_entries()
        for i in range(len(entries) - 1):
            cod = tuple(
                entries[i].vector[k] + entries[i + 1].vector[k] for k in range(18)
            )
            frame = serialize_string(cod, 2)
            assert frame.guard_status == ALL_GUARDS_PASS


# ── Digest ──────────────────────────────────────────────────────

class TestDigest:
    def test_verify_valid_frame(self, ba):
        frame = serialize_letter(ba.vector)
        assert verify_digest(frame.to_bytes())

    def test_reject_corrupted_frame(self, ba):
        frame = serialize_letter(ba.vector)
        raw = bytearray(frame.to_bytes())
        raw[5] ^= 0xFF
        assert not verify_digest(bytes(raw))


# ── LETTER Frame encoding specifics (§4.6) ──────────────────────

class TestLetterEncoding:
    def test_ba_hex(self, ba):
        """§4.6.1: ب encodes to known hex values."""
        frame = serialize_letter(ba.vector)
        raw = frame.to_bytes()
        assert raw[0:2] == MAGIC
        assert raw[2] == VERSION
        assert raw[3] == FrameType.LETTER
        # Payload bytes for ب: 20 01 01 00 01 00 00 11 10
        assert raw[4] == 0x20
        assert raw[5] == 0x01
        assert raw[6] == 0x01
        assert raw[7] == 0x00
        assert raw[8] == 0x01
        assert raw[9] == 0x00
        assert raw[10] == 0x00
        assert raw[11] == 0x11
        assert raw[12] == 0x10

    def test_haa_hex(self, haa):
        """§4.6: هـ encodes to known hex values."""
        frame = serialize_letter(haa.vector)
        raw = frame.to_bytes()
        assert raw[4] == 0x80  # Θ̂=8, Na=0
        assert raw[5] == 0x00  # Nb=0, Nd=0
        assert raw[10] == 0x02  # Qa=0, Qc=2
        assert raw[11] == 0x01  # A_N=0, A_K=1
        assert raw[12] == 0x20  # A_Q=2, H*=0
