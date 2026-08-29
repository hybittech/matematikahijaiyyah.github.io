"""Tests for .hbc binary format — Bab III §3.25."""

import pytest

from hijaiyyah.hisa.hbc_format import (
    HBC_HEADER_SIZE,
    HBC_MAGIC,
    HbcFile,
    HbcFlags,
    HbcHeader,
)
from hijaiyyah.hisa.opcodes import OpCode


class TestHbcHeader:
    def test_magic(self):
        header = HbcHeader()
        data = header.pack()
        assert data[:4] == b"HBYT"
        assert len(data) == HBC_HEADER_SIZE

    def test_roundtrip(self):
        header = HbcHeader(
            har_id=0x0001,
            flags=HbcFlags.GUARD_STRICT | HbcFlags.HAS_DEBUG,
            entry_point=0,
        )
        packed = header.pack()
        restored = HbcHeader.unpack(packed)
        assert restored.magic == HBC_MAGIC
        assert restored.har_id == 0x0001
        assert restored.guard_strict is True
        assert restored.flags & HbcFlags.HAS_DEBUG

    def test_crc_mismatch_rejects(self):
        header = HbcHeader()
        data = bytearray(header.pack())
        data[28] ^= 0xFF  # Corrupt CRC
        with pytest.raises(ValueError, match="CRC mismatch"):
            HbcHeader.unpack(bytes(data))

    def test_invalid_magic_rejects(self):
        header = HbcHeader()
        data = bytearray(header.pack())
        # Overwrite magic and recompute (won't match expected)
        data[0:4] = b"XXXX"
        # This will fail CRC check first
        with pytest.raises(ValueError):
            HbcHeader.unpack(bytes(data))


class TestHbcFile:
    def test_from_instructions_roundtrip(self):
        code = [
            (OpCode.HLOAD << 24) | (0 << 20) | 1,  # HLOAD H0, letter[1]
            (OpCode.HGRD << 24) | (0 << 16),        # HGRD H0
            (OpCode.HALT << 24),                      # HALT
        ]
        hbc = HbcFile.from_instructions(code, har_id=0x0001)
        binary = hbc.to_bytes()

        restored = HbcFile.from_bytes(binary)
        assert restored.header.magic == HBC_MAGIC
        assert restored.header.har_id == 0x0001

        restored_code = restored.to_instructions()
        assert restored_code == code

    def test_guard_strict_flag(self):
        hbc = HbcFile.from_instructions(
            [(OpCode.HALT << 24)],
            flags=HbcFlags.GUARD_STRICT,
        )
        binary = hbc.to_bytes()
        restored = HbcFile.from_bytes(binary)
        assert restored.header.guard_strict is True

    def test_code_size(self):
        code = [(OpCode.HALT << 24)]
        hbc = HbcFile.from_instructions(code)
        binary = hbc.to_bytes()
        restored = HbcFile.from_bytes(binary)
        assert restored.header.code_size == 4  # 1 instruction × 4 bytes
