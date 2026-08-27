"""
Opcode definitions and instruction word encoding.

Bab III §3.24–3.25: H-ISA Instruction Set Architecture.
Opcode space: 256 possible. 44 distinct opcode values are defined here
(47 names, of which 3 are legacy aliases). The HCPU RTL implements a
28-opcode subset — see rtl/hcpu_pkg.vh.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class OpCode(IntEnum):
    # ── Hybit Operations ─────────────────────────────────────────
    HLOAD = 0x01    # Load hybit from HAR/memory
    HCADD = 0x02    # Codex addition: dst ← src1 + src2
    HGRD = 0x03     # Guard check G1–G4, T1–T2
    HPROJ = 0x04    # Projection: Θ/N/K/Q
    HDCMP = 0x05    # Decompose: (U, ρ) ← Θ̂
    HNRM2 = 0x06    # Squared norm: ‖v₁₄‖²
    HDIST = 0x07    # Squared Euclidean distance
    HEXMT = 0x08    # Build 5×5 exomatrix
    HSER = 0x09     # Serialize to HISAB Frame
    HDES = 0x0A     # Deserialize from HISAB Frame
    HCHK = 0x0B     # Runtime integrity check

    # ── Legacy aliases (backward compat with existing tests) ─────
    CLOAD = 0x01    # alias for HLOAD
    CADD = 0x02     # alias for HCADD
    VCHK = 0x03     # alias for HGRD
    CSUB = 0x0C     # Component-wise subtract (14D Delta)
    VMOV = 0x0D     # Copy H-register

    # ── I/O Operations ───────────────────────────────────────────
    PRINT = 0x0E    # Print hybit (formatted)
    HALT = 0x0F     # Terminate with exit code
    PRINTI = 0x40   # Print integer from GPR
    PRINTH = 0x41   # Print hybit with full detail

    # ── Projection aliases ───────────────────────────────────────
    VPROJ_T = 0x10  # Project to theta
    VPROJ_N = 0x11  # Project to N
    VPROJ_K = 0x12  # Project to K
    VPROJ_Q = 0x13  # Project to Q

    # ── Integer Operations ───────────────────────────────────────
    IADD = 0x14     # Integer addition
    ISUB = 0x15     # Integer subtraction
    IMUL = 0x16     # Integer multiplication
    ICMP = 0x17     # Compare, set flags

    # ── Legacy scalar ops (backward compat) ──────────────────────
    VDIST = 0x18    # alias for HDIST via GPR output
    VRHO = 0x19     # Compute turning residue → GPR
    VNORM = 0x1A    # Squared norm → GPR
    VDOT = 0x1B     # Inner product → GPR
    VSCL = 0x1C     # Scalar multiply
    VCMP = 0x1D     # Vector compare
    CHASH = 0x1E    # Compute hash
    CSIGN = 0x1F    # Sign/verify

    # ── Control Flow ─────────────────────────────────────────────
    JMP = 0x20      # Unconditional jump
    JGP = 0x21      # Jump if guard pass
    JGF = 0x22      # Jump if guard fail
    JNP = 0x23      # Jump if not pass (guard)
    JEQ = 0x24      # Jump if equal
    JNE = 0x25      # Jump if not equal
    HALT_ERR = 0x26 # Halt with error code

    # ── Subroutine ───────────────────────────────────────────────
    CALL = 0x30     # Call subroutine (push PC, jump)
    RET = 0x31      # Return (pop PC)

    # ── Memory ───────────────────────────────────────────────────
    PUSH = 0x32     # Push to stack
    POP = 0x33      # Pop from stack


# ── Layer IDs for HPROJ ──────────────────────────────────────────

LAYER_THETA: int = 0
LAYER_N: int = 1
LAYER_K: int = 2
LAYER_Q: int = 3


@dataclass
class InstructionWord:
    raw: int

    @property
    def opcode(self) -> int:
        return (self.raw >> 24) & 0xFF

    @property
    def dst(self) -> int:
        return (self.raw >> 20) & 0xF

    @property
    def src1(self) -> int:
        return (self.raw >> 16) & 0xF

    @property
    def src2(self) -> int:
        return (self.raw >> 12) & 0xF

    @property
    def imm(self) -> int:
        return self.raw & 0xFFF

    def disassemble(self) -> str:
        try:
            op = OpCode(self.opcode)
            return f"{op.name} dst=H{self.dst} src1=H{self.src1} src2=H{self.src2} imm={self.imm}"
        except ValueError:
            return f"UNKNOWN(0x{self.opcode:02X})"

