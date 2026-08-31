"""
HASM — Hybit Assembler
=======================
Facade module: .hasm → .hbc

4-pass pipeline:
  Pass 1: Label Resolution
  Pass 2: Instruction Encoding
  Pass 3: Constant Pool Assembly
  Pass 4: Header Generation (magic + CRC32)

Re-exports from hisa/assembler.py (Bab III §3.29).
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# hisa.assembler exports assemble() and assemble_line() as functions; there
# has never been an Assembler class to delegate to. The two-pass assembler in
# this file — label resolution, encoding, constant pool — is the one that runs.

# ── Constants ─────────────────────────────────────────────────

HBC_MAGIC = b"HBYT"                    # 0x48425954
HBC_MAGIC_INT = 0x48425954
HBC_HEADER_SIZE = 32                   # bytes
HBC_VERSION = (1, 0)

# Flags
FLAG_HAS_DEBUG    = 0x0001
FLAG_HAS_PSI      = 0x0002
FLAG_GUARD_STRICT = 0x0004
FLAG_HAR_EMBEDDED = 0x0008


@dataclass
class HBCHeader:
    """Hybit Bytecode file header (32 bytes).

    Layout (28 body + 4 CRC):
      [0:4]   magic       4s  "HBYT"
      [4:6]   version     H   (major<<8)|minor
      [6:8]   har_id      H   alphabet id
      [8:10]  flags       H   mode flags
      [10:12] reserved    H   (future use)
      [12:16] entry_point I   offset into code
      [16:20] code_offset I   offset to code section
      [20:24] code_size   I   code section bytes
      [24:28] const_off   I   offset to constant pool
      [28:32] checksum    I   CRC32 of bytes 0-27
    """
    magic: bytes = HBC_MAGIC
    version_major: int = 1
    version_minor: int = 0
    har_id: int = 0x0001               # HAR-001 = Hijaiyyah
    flags: int = 0
    reserved: int = 0
    entry_point: int = 0
    code_offset: int = 0
    code_size: int = 0
    const_offset: int = HBC_HEADER_SIZE
    checksum: int = 0

    _BODY_FMT = "<4sHHHHIIII"
    _CRC_FMT = "<I"

    def pack(self) -> bytes:
        """Serialize header to 32 bytes."""
        body = struct.pack(
            self._BODY_FMT,
            self.magic,
            (self.version_major << 8) | self.version_minor,
            self.har_id,
            self.flags,
            self.reserved,
            self.entry_point,
            self.code_offset,
            self.code_size,
            self.const_offset,
        )
        self.checksum = zlib.crc32(body) & 0xFFFFFFFF
        return body + struct.pack(self._CRC_FMT, self.checksum)

    @classmethod
    def unpack(cls, data: bytes) -> "HBCHeader":
        """Deserialize header from 32 bytes."""
        if len(data) < HBC_HEADER_SIZE:
            raise ValueError(f"Header too short: {len(data)} < {HBC_HEADER_SIZE}")
        body_size = struct.calcsize(cls._BODY_FMT)
        fields = struct.unpack(cls._BODY_FMT, data[:body_size])
        checksum = struct.unpack(cls._CRC_FMT, data[body_size:body_size + 4])[0]
        hdr = cls(
            magic=fields[0],
            version_major=(fields[1] >> 8) & 0xFF,
            version_minor=fields[1] & 0xFF,
            har_id=fields[2],
            flags=fields[3],
            reserved=fields[4],
            entry_point=fields[5],
            code_offset=fields[6],
            code_size=fields[7],
            const_offset=fields[8],
            checksum=checksum,
        )
        return hdr

    def verify(self) -> bool:
        """Verify magic and CRC32."""
        if self.magic != HBC_MAGIC:
            return False
        body = struct.pack(
            self._BODY_FMT,
            self.magic,
            (self.version_major << 8) | self.version_minor,
            self.har_id, self.flags, self.reserved,
            self.entry_point, self.code_offset, self.code_size,
            self.const_offset,
        )
        return (zlib.crc32(body) & 0xFFFFFFFF) == self.checksum


@dataclass
class AssembleResult:
    """Result of HASM assembly."""
    success: bool
    bytecode: bytes = b""
    errors: List[str] = field(default_factory=list)
    label_count: int = 0
    instruction_count: int = 0
    constant_count: int = 0


class HASMAssembler:
    """
    Hybit Assembler — .hasm → .hbc

    4-pass pipeline:
      1. Label Resolution
      2. Instruction Encoding
      3. Constant Pool Assembly
      4. Header Generation
    """

    VERSION = "1.0.0"

    def __init__(self, har_id: int = 0x0001, flags: int = 0):
        self.har_id = har_id
        self.flags = flags

    def assemble(self, asm_text: str) -> AssembleResult:
        """Assemble H-ISA text to .hbc bytecode."""
        result = AssembleResult(success=True)
        try:
            # Pass 1: Label resolution
            labels = self._resolve_labels(asm_text)
            result.label_count = len(labels)

            # Pass 2: Instruction encoding
            code = self._encode_instructions(asm_text, labels)
            # Each instruction is a 32-bit word; len(code) is bytes.
            result.instruction_count = len(code) // 4 if code else 0

            # Pass 3: Constant pool
            const_pool = self._build_constant_pool(asm_text)
            result.constant_count = len(const_pool)

            # Pass 4: Header generation
            header = self._generate_header(const_pool, code)
            result.bytecode = header + const_pool + code

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def assemble_file(self, input_path: str,
                      output_path: str) -> AssembleResult:
        """Assemble .hasm file to .hbc file."""
        with open(input_path, "r", encoding="utf-8") as f:
            asm_text = f.read()
        result = self.assemble(asm_text)
        if result.success and output_path:
            with open(output_path, "wb") as f:
                f.write(result.bytecode)
        return result

    def _resolve_labels(self, text: str) -> Dict[str, int]:
        labels = {}
        offset = 0
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith(";"):
                continue
            if stripped.endswith(":"):
                labels[stripped[:-1]] = offset
            else:
                offset += 1
        return labels

    def _encode_instructions(self, text: str,
                             labels: Dict[str, int]) -> bytes:
        """
        Encode each instruction as a big-endian 32-bit word.

        This used to emit `bytes(count)` — a run of NUL bytes as long as the
        instruction count — behind a delegation to an Assembler class that has
        never existed, so the .hbc it produced carried no instructions at all.
        hisa.assembler.assemble() does the real encoding against the frozen
        H-ISA, and is what runs now.
        """
        from ..hisa.assembler import assemble

        words = assemble(text)
        return b"".join(word.to_bytes(4, "big") for word in words)

    def _build_constant_pool(self, text: str) -> bytes:
        return b""

    def _generate_header(self, const_pool: bytes,
                         code: bytes) -> bytes:
        header = HBCHeader(
            har_id=self.har_id,
            flags=self.flags,
            const_offset=HBC_HEADER_SIZE,
            code_offset=HBC_HEADER_SIZE + len(const_pool),
            code_size=len(code),
        )
        return header.pack()


__all__ = [
    "FLAG_GUARD_STRICT",
    "FLAG_HAR_EMBEDDED",
    "FLAG_HAS_DEBUG",
    "FLAG_HAS_PSI",
    "HBC_HEADER_SIZE",
    "HBC_MAGIC",
    "HBC_MAGIC_INT",
    "AssembleResult",
    "HASMAssembler",
    "HBCHeader",
]
