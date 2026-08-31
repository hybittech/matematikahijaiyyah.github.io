"""
Opcode definitions and instruction word encoding.

Bab III §3.24–3.25: H-ISA Instruction Set Architecture.

Single source of truth for the encoding: rtl/hcpu_pkg.vh.

These two halves used to disagree outright. The software side numbered HLOAD
0x01 while the RTL numbered it 0x40 — and 0x01 is the RTL's HALT, so the first
instruction of any compiled program would have stopped the processor. Of the
thirteen mnemonics both sides defined, only four agreed. They were not two
implementations of one ISA; they were two ISAs sharing a name.

The RTL encoding wins, for two reasons. It is grouped by function, so the top
nibble carries meaning. And it is the half that is verified in hardware and
destined for silicon, where a wrong number cannot be patched.

The block map is docs/HISA_SPEC.md §6.1, which the RTL already follows almost
everywhere:

    0x0_  system and control            0x60–0x6F  guards and audit
    0x1_  integer arithmetic            0x70–0x7F  crypto
    0x2_  compare and control flow      0x80–0x8F  vector math
    0x3_  memory and stack              0x90–0x9F  string operations
    0x40–0x5F  codex operations         0xA0–0xAF  I/O and debug
                                        0xB0–0xFF  reserved / error halt

Three places where the RTL departs from that document, and the RTL wins:

    0x06, 0x07   HNRM2, HDIST   the spec puts POP and CALL here
    0x32, 0x33   PUSH, POP      the spec puts LOADR and LEA here
    0x50, 0x51   HPACK, HCRC    the spec puts CAN and CAK here

Opcodes the HCPU does not implement are marked "software only" below. They run
under the HVM and the HISA machine, and sit in gaps both the RTL and the spec
leave free, so promoting one to hardware later never forces a renumbering.

tests/test_hisa/test_isa_parity.py holds this file and hcpu_pkg.vh together.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class OpCode(IntEnum):
    # ── System (0x0_) ────────────────────────────────────────────
    NOP = 0x00      # No operation
    HALT = 0x01     # Terminate
    MOV = 0x03      # Copy GPR
    MOVI = 0x04     # Load immediate into GPR

    # Hybit scalars that return to a GPR. In the 0x0_ block rather than 0x4_
    # because their result is an integer, not a hybit.
    HNRM2 = 0x06    # Squared norm: ‖v₁₄‖² → GPR
    HDIST = 0x07    # Squared Euclidean distance → GPR

    # ── Integer arithmetic (0x1_) ────────────────────────────────
    ADD = 0x10      # GPR addition
    ADDI = 0x11     # GPR + immediate
    SUB = 0x12      # GPR subtraction
    MUL = 0x14      # GPR multiplication

    # ── Compare and control flow (0x2_) ──────────────────────────
    CMP = 0x20      # Compare two GPRs, set flags
    CMPI = 0x21     # Compare GPR with immediate
    JMP = 0x22      # Unconditional jump
    JEQ = 0x23      # Jump if equal
    JNE = 0x24      # Jump if not equal
    JGD = 0x29      # Jump if GUARD flag set
    JNGD = 0x2A     # Jump if GUARD flag clear
    # 0x2B–0x2F is the spec's reserved tail of this block.
    JGP = 0x2B      # Jump if guard pass          (software only)
    JGF = 0x2C      # Jump if guard fail          (software only)
    JNP = 0x2D      # Jump if not pass            (software only)
    # The spec puts CALL/RET at 0x07/0x08, which the RTL uses for HDIST and
    # for the reserved slot after it. They move here instead.
    CALL = 0x2E     # Call subroutine             (software only)
    RET = 0x2F      # Return from subroutine      (software only)

    # ── Memory and stack (0x3_) ──────────────────────────────────
    LOAD = 0x30     # GPR ← MEM[base + offset]
    STORE = 0x31    # MEM[base + offset] ← GPR
    PUSH = 0x32     # Push GPR to stack
    POP = 0x33      # Pop stack into GPR

    # ── Codex operations (0x40–0x5F) ─────────────────────────────
    HLOAD = 0x40    # Load hybit from the sealed ROM by letter index
    HCADD = 0x42    # Codex addition: dst ← src1 + src2
    CSUB = 0x43     # Component-wise subtract     (software only)
    VMOV = 0x46     # Copy H-register             (software only)
    # The spec's C-prefixed scalar extractors. These read a hybit and return an
    # integer, so they share the codex block rather than vector math.
    VCMP = 0x48     # Compare two hybits          (software only)
    VDOT = 0x49     # Inner product → GPR         (software only)
    VNORM = 0x4A    # Squared norm → GPR          (software only)
    VDIST = 0x4B    # Squared distance → GPR      (software only)
    VRHO = 0x4C     # Turning residue ρ → GPR     (software only)

    HPACK = 0x50    # Nibble-pack a hybit into words
    HCRC = 0x51     # CRC32 over a packed frame
    # 0x55–0x5F is the spec's reserved tail for future codex operations.
    HEXMT = 0x55    # Build 5×5 exomatrix         (software only)
    HDCMP = 0x56    # Decompose into (U, ρ)       (software only)
    HSER = 0x57     # Serialize to HISAB frame    (software only)
    HDES = 0x58     # Deserialize a HISAB frame   (software only)
    VSCL = 0x59     # Scalar multiply             (software only)

    # ── Guards and audit (0x60–0x6F) ─────────────────────────────
    HGRD = 0x60     # Guard check G1–G4, T1–T2 → GUARD flag
    HCHK = 0x68     # Runtime integrity check     (software only)

    # ── Crypto (0x70–0x7F) — software only ───────────────────────
    CHASH = 0x70    # Compute hash
    CSIGN = 0x72    # Sign / verify

    # ── Vector math (0x80–0x8F) — software only ──────────────────
    HPROJ = 0x80    # Project onto layer given by IMM
    VPROJ_T = 0x88  # Project to Θ
    VPROJ_N = 0x89  # Project to N
    VPROJ_K = 0x8A  # Project to K
    VPROJ_Q = 0x8B  # Project to Q

    # ── I/O and debug (0xA0–0xAF) ────────────────────────────────
    PRINT = 0xA0    # Print value from GPR
    PRINTH = 0xA1   # Print hybit with detail     (software only)

    # ── Error ────────────────────────────────────────────────────
    HALT_ERR = 0xFF  # Halt on an unimplemented or faulting instruction

    # ── Aliases ──────────────────────────────────────────────────
    # Same value as the member above, so Python treats these as alternate
    # spellings rather than separate opcodes. Kept for source compatibility.
    # The spec's names for opcodes this file reached first.
    CLOAD = 0x40    # → HLOAD
    CADD = 0x42     # → HCADD
    VCHK = 0x60     # → HGRD
    EMIT = 0xA0     # → PRINT

    # This file's names for opcodes the spec reached first. Same operation,
    # different prefix convention; both spellings assemble.
    CMOV = 0x46     # → VMOV
    CEQ = 0x48      # → VCMP
    CDOT = 0x49     # → VDOT
    CNORM = 0x4A    # → VNORM
    CDIST = 0x4B    # → VDIST
    CRHO = 0x4C     # → VRHO
    VPROJ = 0x80    # → HPROJ
    EMITC = 0xA1    # → PRINTH

    # Ordinary synonyms.
    IADD = 0x10     # → ADD
    ISUB = 0x12     # → SUB
    IMUL = 0x14     # → MUL
    ICMP = 0x20     # → CMP
    PRINTI = 0xA0   # → PRINT   (printing an integer is what PRINT does)


# Opcodes the HCPU RTL implements. Anything outside this set runs only under
# the HVM and the HISA machine, and must not appear in a program intended for
# hardware. Kept as data so tests can check it against hcpu_pkg.vh directly.
RTL_IMPLEMENTED: frozenset[OpCode] = frozenset({
    OpCode.NOP, OpCode.HALT, OpCode.MOV, OpCode.MOVI,
    OpCode.HNRM2, OpCode.HDIST,
    OpCode.ADD, OpCode.ADDI, OpCode.SUB, OpCode.MUL,
    OpCode.CMP, OpCode.CMPI, OpCode.JMP, OpCode.JEQ, OpCode.JNE,
    OpCode.JGD, OpCode.JNGD,
    OpCode.LOAD, OpCode.STORE, OpCode.PUSH, OpCode.POP,
    OpCode.HLOAD, OpCode.HCADD,
    OpCode.HPACK, OpCode.HCRC,
    OpCode.HGRD,
    OpCode.PRINT,
    OpCode.HALT_ERR,
})


def is_rtl_implemented(op: int) -> bool:
    """True if the HCPU can execute this opcode; False for software-only ones."""
    try:
        return OpCode(op) in RTL_IMPLEMENTED
    except ValueError:
        return False


# ── Layer IDs for HPROJ ──────────────────────────────────────────

LAYER_THETA: int = 0
LAYER_N: int = 1
LAYER_K: int = 2
LAYER_Q: int = 3


@dataclass
class InstructionWord:
    """
    32-bit instruction word, laid out exactly as the RTL reads it:

        [31:24] opcode   [23:20] dst   [19:16] src1   [15:12] src2   [11:0] imm

    Matches `enc = {op, dst, s1, s2, imm}` in rtl/tb/tb_hcpu_top.v.
    """

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
        except ValueError:
            return f"UNKNOWN(0x{self.opcode:02X})"
        mark = "" if op in RTL_IMPLEMENTED else "  ; software only"
        return (
            f"{op.name} dst=H{self.dst} src1=H{self.src1} "
            f"src2=H{self.src2} imm={self.imm}{mark}"
        )
