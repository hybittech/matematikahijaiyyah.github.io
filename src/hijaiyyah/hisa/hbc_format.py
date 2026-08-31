"""
.hbc — Hybit Bytecode format.

Bab III §3.25: Binary executable format for HVM.

Header (32 bytes):
  Magic(4B) | Version(2B) | HAR-ID(2B) | Flags(2B) |
  Entry(4B) | ConstOff(4B) | CodeOff(4B) | CodeSz(4B) |
  DataOff(4B) | DataSz(4B) | CRC32(4B) = 32B

Flags:
  bit 0: HAS_DEBUG    — debug info available
  bit 1: HAS_PSI      — source Ψ-augmented
  bit 2: GUARD_STRICT — every HCADD wajib guard check
  bit 3: HAR_EMBEDDED — HAR data embedded in .hbc
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass, field
from enum import IntFlag
from typing import List, Optional

# Magic number: "HBYT"
HBC_MAGIC = b"HBYT"
HBC_HEADER_SIZE = 32


class HbcFlags(IntFlag):
    """Flags field — architectural design decisions (§3.25)."""
    NONE = 0
    HAS_DEBUG = 1 << 0
    HAS_PSI = 1 << 1
    GUARD_STRICT = 1 << 2
    HAR_EMBEDDED = 1 << 3


@dataclass
class HbcHeader:
    """32-byte .hbc file header.

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
    har_id: int = 0x0001       # HAR-001 = Hijaiyyah
    flags: int = 0
    reserved: int = 0
    entry_point: int = 0
    code_offset: int = 0
    code_size: int = 0
    const_offset: int = HBC_HEADER_SIZE
    checksum: int = 0

    _BODY_FMT = "<4sHHHHIIII"
    _CRC_FMT = "<I"

    @property
    def version(self) -> int:
        return (self.version_major << 8) | self.version_minor

    @property
    def guard_strict(self) -> bool:
        return bool(self.flags & HbcFlags.GUARD_STRICT)

    def pack(self) -> bytes:
        """Serialize header to 32 bytes."""
        body = struct.pack(
            self._BODY_FMT,
            self.magic,
            self.version,
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
    def unpack(cls, data: bytes) -> "HbcHeader":
        """Deserialize header from 32 bytes."""
        if len(data) < HBC_HEADER_SIZE:
            raise ValueError(f"Header too short: {len(data)} < {HBC_HEADER_SIZE}")

        body_size = struct.calcsize(cls._BODY_FMT)
        header_data = data[:body_size]
        stored_crc = struct.unpack_from(cls._CRC_FMT, data, body_size)[0]

        computed_crc = zlib.crc32(header_data) & 0xFFFFFFFF
        if computed_crc != stored_crc:
            raise ValueError(
                f"Header CRC mismatch: stored=0x{stored_crc:08X}, "
                f"computed=0x{computed_crc:08X}"
            )

        fields = struct.unpack(cls._BODY_FMT, header_data)
        if fields[0] != HBC_MAGIC:
            raise ValueError(
                f"Invalid magic: {fields[0]!r}, expected {HBC_MAGIC!r}"
            )

        return cls(
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
            checksum=stored_crc,
        )


@dataclass
class HbcFile:
    """Complete .hbc file representation."""
    header: HbcHeader = field(default_factory=HbcHeader)
    constants: bytes = b""
    code: bytes = b""
    data: bytes = b""

    def to_bytes(self) -> bytes:
        """Serialize to .hbc binary format."""
        # Compute offsets
        const_off = HBC_HEADER_SIZE
        code_off = const_off + len(self.constants)

        self.header.const_offset = const_off
        self.header.code_offset = code_off
        self.header.code_size = len(self.code)

        header_bytes = self.header.pack()
        return header_bytes + self.constants + self.code + self.data

    @classmethod
    def from_bytes(cls, data: bytes) -> HbcFile:
        """Deserialize from .hbc binary format."""
        header = HbcHeader.unpack(data[:HBC_HEADER_SIZE])

        constants = data[header.const_offset:header.code_offset]
        code = data[header.code_offset:header.code_offset + header.code_size]
        # data section follows code (we don't have lengths for it now, but we'll take the rest)
        file_data = data[header.code_offset + header.code_size:]

        return cls(
            header=header,
            constants=constants,
            code=code,
            data=file_data,
        )

    @classmethod
    def from_instructions(
        cls,
        instructions: List[int],
        *,
        har_id: int = 0x0001,
        flags: int = 0,
        constants: Optional[bytes] = None,
    ) -> HbcFile:
        """Create .hbc from a list of 32-bit instruction words."""
        code_bytes = b"".join(struct.pack("<I", iw) for iw in instructions)

        header = HbcHeader(
            har_id=har_id,
            flags=flags,
            entry_point=0,
        )

        return cls(
            header=header,
            constants=constants or b"",
            code=code_bytes,
        )

    def to_instructions(self) -> List[int]:
        """Extract instruction words from code section."""
        count = len(self.code) // 4
        return [
            struct.unpack_from("<I", self.code, i * 4)[0]
            for i in range(count)
        ]


def write_hbc(path: str, hbc: HbcFile) -> None:
    """Write .hbc file to disk."""
    with open(path, "wb") as f:
        f.write(hbc.to_bytes())


def read_hbc(path: str) -> HbcFile:
    """Read .hbc file from disk."""
    with open(path, "rb") as f:
        data = f.read()
    return HbcFile.from_bytes(data)
