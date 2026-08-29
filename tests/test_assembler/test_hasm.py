"""Tests for HASM — Hybit Assembler (facade)."""

from hijaiyyah.assembler import (
    FLAG_GUARD_STRICT,
    HBC_HEADER_SIZE,
    HBC_MAGIC,
    HBC_MAGIC_INT,
    AssembleResult,
    HASMAssembler,
    HBCHeader,
)


class TestHASMImport:

    def test_import_assembler(self):
        assert HASMAssembler is not None

    def test_import_result(self):
        assert AssembleResult is not None

    def test_import_header(self):
        assert HBCHeader is not None

    def test_magic_constant(self):
        assert HBC_MAGIC == b"HBYT"
        assert HBC_MAGIC_INT == 0x48425954

    def test_header_size(self):
        assert HBC_HEADER_SIZE == 32


class TestHBCHeader:
    """Test .hbc binary header."""

    def test_pack_unpack_roundtrip(self):
        hdr = HBCHeader(har_id=0x0001, flags=FLAG_GUARD_STRICT)
        packed = hdr.pack()
        assert len(packed) == HBC_HEADER_SIZE

        restored = HBCHeader.unpack(packed)
        assert restored.magic == HBC_MAGIC
        assert restored.har_id == 0x0001
        assert restored.flags == FLAG_GUARD_STRICT

    def test_verify_valid(self):
        hdr = HBCHeader()
        packed = hdr.pack()
        restored = HBCHeader.unpack(packed)
        assert restored.verify() is True

    def test_verify_corrupted(self):
        hdr = HBCHeader()
        packed = bytearray(hdr.pack())
        packed[5] ^= 0xFF  # corrupt a byte
        restored = HBCHeader.unpack(bytes(packed))
        assert restored.verify() is False

    def test_magic_bytes(self):
        hdr = HBCHeader()
        packed = hdr.pack()
        assert packed[:4] == HBC_MAGIC

    def test_default_har(self):
        hdr = HBCHeader()
        assert hdr.har_id == 0x0001  # HAR-001 Hijaiyyah

    def test_flags(self):
        hdr = HBCHeader(flags=FLAG_GUARD_STRICT)
        assert hdr.flags & FLAG_GUARD_STRICT


class TestHASMAssembler:
    """Test assembler pipeline."""

    def test_init(self):
        asm = HASMAssembler()
        assert asm.VERSION == "1.0.0"
        assert asm.har_id == 0x0001

    def test_assemble_empty(self):
        asm = HASMAssembler()
        result = asm.assemble("")
        assert isinstance(result, AssembleResult)
        assert result.success is True

    def test_assemble_with_labels(self):
        asm_text = """; test
main:
    HALT 0
"""
        asm = HASMAssembler()
        result = asm.assemble(asm_text)
        assert result.success is True
        assert result.label_count >= 1

    def test_assemble_result_has_bytecode(self):
        asm = HASMAssembler()
        result = asm.assemble("HALT 0")
        assert isinstance(result.bytecode, bytes)
        assert len(result.bytecode) >= HBC_HEADER_SIZE

    def test_result_bytecode_starts_with_magic(self):
        asm = HASMAssembler()
        result = asm.assemble("HALT 0")
        if result.bytecode:
            assert result.bytecode[:4] == HBC_MAGIC
