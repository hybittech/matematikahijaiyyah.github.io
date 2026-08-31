#!/usr/bin/env python3
"""
asm2hex.py — H-ISA Assembly to Hex Converter (v2.0)

Reads .hasm assembly files and generates instruction hex for
$readmemh loading into testbench or FPGA instruction memory.

Features:
  - Label support (forward and backward references)
  - Branch offsets computed automatically (PC-relative)
  - Register names: R0-R17, H0-H15
  - Immediate formats: decimal, hex (0x..), hash (#..)
  - Comment support (;)

Each instruction is output as 8 hex digits (32 bits).

Usage:
    python asm2hex.py input.hasm > program.hex
    python asm2hex.py input.hasm --verbose

(c) 2026 HMCL
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ── Opcode table (matching hcpu_pkg.vh) ──────────────────────────
# Opcode values come from the frozen H-ISA, not a fourth copy of the table.
# This file used to carry its own — it agreed with the RTL, but four hand-kept
# copies of one encoding is how HLOAD came to mean 0x40 in hardware and 0x01 in
# software. Only what the HCPU can execute is assembled here; a software-only
# opcode in a program bound for the FPGA would raise HALT_ERR on the board.
_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from hijaiyyah.hisa.opcodes import RTL_IMPLEMENTED  # noqa: E402

OPCODES = {op.name: int(op) for op in RTL_IMPLEMENTED}


def parse_reg(s: str) -> int:
    """Parse register name to 4-bit index and enforce strict bounds."""
    s = s.strip().upper()
    if s.startswith("R"):
        idx = int(s[1:])
        if idx > 17:
            raise ValueError(f"Register index out of bounds: {s} (Max R17)")
        return idx & 0xF
    elif s.startswith("H"):
        idx = int(s[1:])
        if idx > 15:
            raise ValueError(f"H-Register index out of bounds: {s} (Max H15)")
        return idx & 0xF
    elif s == "_" or s == "":
        return 0
    else:
        idx = int(s)
        if idx > 17:
             raise ValueError(f"Register index out of bounds: {s}")
        return idx & 0xF


def parse_imm(s: str, labels: dict, current_addr: int, is_branch: bool = False) -> int:
    """Parse immediate value (decimal, hex, hash, or label).
    
    For branch instructions, label references are converted to
    PC-relative offsets.
    """
    s = s.strip()
    
    # Check if it's a label reference
    if s in labels:
        if is_branch:
            # PC-relative: offset from current instruction
            offset = labels[s] - current_addr
            return offset & 0xFFF
        else:
            # Absolute address
            return labels[s] & 0xFFF
    
    if s.startswith("0x") or s.startswith("0X"):
        val = int(s, 16)
    elif s.startswith("#"):
        val = int(s[1:])
    elif s.startswith("-"):
        val = int(s)
    else:
        val = int(s)

    # Validate 12-bit signed range (-2048 to 2047)
    if val < -2048 or val > 2047:
        if not (0 <= val <= 4095): # Also allow unsigned 12-bit representation
            raise ValueError(f"Immediate value {val} out of 12-bit range (-2048 to 4095).")

    return val & 0xFFF


def encode(op: int, dst: int = 0, s1: int = 0, s2: int = 0, imm: int = 0) -> int:
    """Encode instruction word: [OP:8][DST:4][S1:4][S2:4][IMM:12]."""
    return ((op & 0xFF) << 24) | ((dst & 0xF) << 20) | \
           ((s1 & 0xF) << 16) | ((s2 & 0xF) << 12) | (imm & 0xFFF)


def assemble_line(line: str, labels: dict, addr: int) -> int | None:
    """Assemble one line of H-ISA assembly into 32-bit instruction."""
    # Strip comments
    line = line.split(";")[0].strip()
    if not line or line.endswith(":"):
        return None

    parts = re.split(r"[,\s]+", line)
    mnemonic = parts[0].upper()

    if mnemonic not in OPCODES:
        raise ValueError(f"Unknown mnemonic: {mnemonic} at address {addr}")

    op = OPCODES[mnemonic]

    if mnemonic in ("NOP", "HALT"):
        return encode(op)

    elif mnemonic in ("MOV",):
        dst = parse_reg(parts[1])
        s1  = parse_reg(parts[2])
        return encode(op, dst, s1)

    elif mnemonic in ("ADD", "SUB", "MUL"):
        dst = parse_reg(parts[1])
        s1  = parse_reg(parts[2])
        s2  = parse_reg(parts[3]) if len(parts) > 3 else 0
        return encode(op, dst, s1, s2)

    elif mnemonic == "CMP":
        s1 = parse_reg(parts[1])
        s2 = parse_reg(parts[2])
        return encode(op, 0, s1, s2)

    elif mnemonic in ("MOVI",):
        dst = parse_reg(parts[1])
        imm = parse_imm(parts[2], labels, addr)
        return encode(op, dst, 0, 0, imm)

    elif mnemonic in ("ADDI",):
        dst = parse_reg(parts[1])
        s1  = parse_reg(parts[2])
        imm = parse_imm(parts[3], labels, addr)
        return encode(op, dst, s1, 0, imm)

    elif mnemonic in ("CMPI",):
        s1  = parse_reg(parts[1])
        imm = parse_imm(parts[2], labels, addr)
        return encode(op, 0, s1, 0, imm)

    elif mnemonic == "JMP":
        imm = parse_imm(parts[1], labels, addr, is_branch=False)
        return encode(op, 0, 0, 0, imm)

    elif mnemonic in ("JEQ", "JNE", "JGD", "JNGD"):
        imm = parse_imm(parts[1], labels, addr, is_branch=True)
        return encode(op, 0, 0, 0, imm)

    elif mnemonic == "PUSH":
        s1 = parse_reg(parts[1])
        return encode(op, 0, s1)

    elif mnemonic == "POP":
        dst = parse_reg(parts[1])
        return encode(op, dst)

    elif mnemonic == "LOAD":
        dst = parse_reg(parts[1])
        s1  = parse_reg(parts[2])  # base register
        imm = parse_imm(parts[3], labels, addr) if len(parts) > 3 else 0
        return encode(op, dst, s1, 0, imm)

    elif mnemonic == "STORE":
        s1  = parse_reg(parts[1])  # data register
        s2  = parse_reg(parts[2])  # base register
        imm = parse_imm(parts[3], labels, addr) if len(parts) > 3 else 0
        return encode(op, 0, s1, s2, imm)

    elif mnemonic == "HLOAD":
        dst = parse_reg(parts[1])
        # IMM can be a register for dynamic indexing or a number
        try:
            imm = parse_imm(parts[2], labels, addr)
        except ValueError:
            # Treat as register-indirect: store reg index in S1
            s1 = parse_reg(parts[2])
            return encode(op, dst, s1, 0, 0)
        return encode(op, dst, 0, 0, imm)

    elif mnemonic == "HCADD":
        dst = parse_reg(parts[1])
        s1  = parse_reg(parts[2])
        s2  = parse_reg(parts[3])
        return encode(op, dst, s1, s2)

    elif mnemonic == "HGRD":
        s1 = parse_reg(parts[1])
        return encode(op, 0, s1)

    elif mnemonic in ("HNRM2",):
        dst = parse_reg(parts[1])
        s1  = parse_reg(parts[2])
        return encode(op, dst, s1)

    elif mnemonic in ("HDIST",):
        dst = parse_reg(parts[1])
        s1  = parse_reg(parts[2])
        s2  = parse_reg(parts[3])
        return encode(op, dst, s1, s2)

    elif mnemonic == "PRINT":
        s1 = parse_reg(parts[1])
        return encode(op, 0, s1)

    return encode(op)


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("-")]

    if len(args) < 1:
        print("Usage: asm2hex.py input.hasm [--verbose] > program.hex", file=sys.stderr)
        sys.exit(1)

    src = Path(args[0])
    raw_lines = src.read_text(encoding="utf-8").splitlines()

    # Pass 1: collect labels and build clean line list
    labels = {}
    addr = 0
    source_lines = []  # (original_line, is_instruction, addr)

    for line in raw_lines:
        stripped = line.split(";")[0].strip()
        if stripped.endswith(":"):
            label_name = stripped[:-1].strip()
            labels[label_name] = addr
            source_lines.append((line, False, addr))
        elif stripped and not stripped.startswith(";"):
            source_lines.append((line, True, addr))
            addr += 1
        else:
            source_lines.append((line, False, addr))

    if verbose:
        print(f"; Labels: {labels}", file=sys.stderr)
        print(f"; Total instructions: {addr}", file=sys.stderr)

    # Pass 2: assemble
    instructions = []
    source_map = []  # Track source line for each instruction
    for original_line, is_instr, a in source_lines:
        if not is_instr:
            continue
        word = assemble_line(original_line, labels, a)
        if word is not None:
            instructions.append(word)
            source_map.append(original_line.strip())

    # Output hex
    for i, word in enumerate(instructions):
        src_comment = source_map[i] if i < len(source_map) else ""
        # Clean up the comment
        src_clean = src_comment.split(";")[0].strip()
        print(f"{word:08X}  // addr {i:4d}: {src_clean}")

    if verbose:
        print(f"; Assembled {len(instructions)} instructions", file=sys.stderr)


if __name__ == "__main__":
    main()
