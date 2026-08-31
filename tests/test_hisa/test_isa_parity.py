"""
H-ISA parity: src/hijaiyyah/hisa/opcodes.py against rtl/hcpu_pkg.vh.

These two halves had drifted into separate instruction sets sharing one name.
Of the thirteen mnemonics both defined, only four agreed on a value. The
software side numbered HLOAD 0x01, which the RTL reads as HALT — so the first
instruction of any compiled program would have stopped the processor, and no
test anywhere would have noticed.

Nothing about that is recoverable once a design is in silicon, so this module
is the gate. It parses the Verilog header directly rather than trusting a
transcribed copy: the RTL is the source of truth for the encoding, and any
change to it must be mirrored here or the suite goes red.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

import pytest

from hijaiyyah.hisa.opcodes import RTL_IMPLEMENTED, InstructionWord, OpCode

ROOT = Path(__file__).resolve().parents[2]
PKG_VH = ROOT / "rtl" / "hcpu_pkg.vh"
SPEC_MD = ROOT / "docs" / "HISA_SPEC.md"

_OP_DEFINE = re.compile(r"`define\s+OP_([A-Z0-9_]+)\s+8'h([0-9A-Fa-f]+)")
# Opcode table rows: | 0xNN | `MNEMONIC` | ...
_SPEC_ROW = re.compile(r"^\|\s*0x([0-9A-F]{2})\s*\|\s*`([A-Z0-9_]+)`", re.M)


def _rtl_opcodes() -> Dict[str, int]:
    text = PKG_VH.read_text(encoding="utf-8")
    return {m.group(1): int(m.group(2), 16) for m in _OP_DEFINE.finditer(text)}


def _spec_opcodes() -> Dict[str, int]:
    text = SPEC_MD.read_text(encoding="utf-8")
    return {m.group(2): int(m.group(1), 16) for m in _SPEC_ROW.finditer(text)}


RTL_OPCODES = _rtl_opcodes()
SPEC_OPCODES = _spec_opcodes()


# ── The parse itself ─────────────────────────────────────────────

def test_rtl_header_was_actually_parsed() -> None:
    """A regex that quietly matched nothing would make every test below pass."""
    assert PKG_VH.exists(), f"missing {PKG_VH}"
    assert len(RTL_OPCODES) >= 25, (
        f"only {len(RTL_OPCODES)} opcodes parsed from hcpu_pkg.vh — "
        "the `define format probably changed"
    )


def test_rtl_opcode_values_are_unique() -> None:
    seen: Dict[int, str] = {}
    for name, value in RTL_OPCODES.items():
        assert value not in seen, (
            f"RTL assigns 0x{value:02X} to both {seen[value]} and {name}"
        )
        seen[value] = name


# ── Encoding parity ──────────────────────────────────────────────

@pytest.mark.parametrize("name", sorted(RTL_OPCODES), ids=sorted(RTL_OPCODES))
def test_rtl_opcode_exists_in_python(name: str) -> None:
    assert name in OpCode.__members__, (
        f"rtl/hcpu_pkg.vh defines OP_{name} but hisa/opcodes.py does not"
    )


@pytest.mark.parametrize("name", sorted(RTL_OPCODES), ids=sorted(RTL_OPCODES))
def test_rtl_opcode_value_matches(name: str) -> None:
    rtl_value = RTL_OPCODES[name]
    py_value = int(OpCode[name])
    assert py_value == rtl_value, (
        f"{name}: RTL=0x{rtl_value:02X} but Python=0x{py_value:02X}. "
        "The RTL is the source of truth — update hisa/opcodes.py."
    )


def test_rtl_implemented_set_is_exactly_the_rtl_header() -> None:
    """RTL_IMPLEMENTED is what callers consult before targeting hardware."""
    declared = {op.name for op in RTL_IMPLEMENTED}
    actual = set(RTL_OPCODES)
    assert declared == actual, (
        f"claimed but not in RTL: {sorted(declared - actual)}; "
        f"in RTL but not claimed: {sorted(actual - declared)}"
    )


# ── Software-only opcodes must not collide with hardware ─────────

def test_software_only_opcodes_avoid_rtl_encodings() -> None:
    """
    A software-only opcode sharing a value with an RTL one is the exact bug
    this module exists to prevent: the program runs under the HVM and does
    something entirely different on the HCPU.
    """
    rtl_values = set(RTL_OPCODES.values())
    collisions = [
        (op.name, op.value)
        for op in OpCode
        if op not in RTL_IMPLEMENTED and op.value in rtl_values
    ]
    assert not collisions, (
        "software-only opcodes reusing an RTL encoding: "
        + ", ".join(f"{n}=0x{v:02X}" for n, v in collisions)
    )


def test_every_opcode_value_is_a_byte() -> None:
    for op in OpCode:
        assert 0 <= op.value <= 0xFF, f"{op.name}=0x{op.value:X} does not fit a byte"


def test_aliases_resolve_to_a_real_opcode() -> None:
    """Aliases are alternate spellings, so each must land on a canonical member."""
    canonical = {op.value for op in OpCode}
    for name, member in OpCode.__members__.items():
        assert member.value in canonical, f"alias {name} points nowhere"


# ── Instruction word layout ──────────────────────────────────────

def test_instruction_layout_matches_the_rtl_encoder() -> None:
    """
    The testbench builds words as {op, dst, s1, s2, imm} = 8+4+4+4+12 bits.
    InstructionWord must take them apart the same way, or a program assembled
    in Python decodes into different registers on the HCPU.
    """
    op, dst, s1, s2, imm = 0x42, 0xA, 0x5, 0x3, 0xABC
    raw = (op << 24) | (dst << 20) | (s1 << 16) | (s2 << 12) | imm

    word = InstructionWord(raw)
    assert word.opcode == op
    assert word.dst == dst
    assert word.src1 == s1
    assert word.src2 == s2
    assert word.imm == imm
    assert raw <= 0xFFFFFFFF


# ── The written specification, as the third copy ─────────────────

def test_spec_table_was_actually_parsed() -> None:
    assert SPEC_MD.exists(), f"missing {SPEC_MD}"
    assert len(SPEC_OPCODES) >= 60, (
        f"only {len(SPEC_OPCODES)} opcodes parsed from HISA_SPEC.md — "
        "the table format probably changed"
    )


@pytest.mark.parametrize(
    "name", sorted(set(SPEC_OPCODES) & set(OpCode.__members__)),
    ids=sorted(set(SPEC_OPCODES) & set(OpCode.__members__)),
)
def test_spec_opcode_value_matches(name: str) -> None:
    """
    The spec was a third encoding of its own — it numbered PUSH 0x05 where the
    RTL numbers it 0x32. Any mnemonic present in both must now agree.
    """
    spec_value = SPEC_OPCODES[name]
    py_value = int(OpCode[name])
    assert py_value == spec_value, (
        f"{name}: HISA_SPEC.md=0x{spec_value:02X} but Python=0x{py_value:02X}"
    )


@pytest.mark.parametrize("name", sorted(RTL_OPCODES), ids=sorted(RTL_OPCODES))
def test_spec_documents_every_rtl_opcode(name: str) -> None:
    """Hardware the spec does not mention is hardware nobody can target."""
    assert name in SPEC_OPCODES, (
        f"OP_{name} exists in the RTL but is absent from HISA_SPEC.md §6.2"
    )


def test_spec_opcode_values_are_unique_or_declared_aliases() -> None:
    """
    Two spec rows may share a value only when Python also treats the names as
    aliases — HLOAD/CLOAD, HGRD/VCHK, PRINT/EMIT. Anything else is one opcode
    accidentally documented twice.
    """
    seen: Dict[int, str] = {}
    for name, value in SPEC_OPCODES.items():
        prior = seen.get(value)
        if prior is None:
            seen[value] = name
            continue
        both_known = name in OpCode.__members__ and prior in OpCode.__members__
        assert both_known and int(OpCode[name]) == int(OpCode[prior]), (
            f"HISA_SPEC.md assigns 0x{value:02X} to both {prior} and {name}, "
            "but hisa/opcodes.py does not declare them as aliases"
        )


def test_hload_is_not_halt() -> None:
    """
    The specific collision that made this module necessary: HLOAD used to be
    0x01, which the RTL decodes as HALT.
    """
    assert OpCode.HLOAD != OpCode.HALT
    assert int(OpCode.HLOAD) == RTL_OPCODES["HLOAD"]
    assert int(OpCode.HALT) == RTL_OPCODES["HALT"]


def test_disassembler_flags_software_only_instructions() -> None:
    hardware = InstructionWord(int(OpCode.HLOAD) << 24).disassemble()
    software = InstructionWord(int(OpCode.HPROJ) << 24).disassemble()
    assert "software only" not in hardware
    assert "software only" in software
