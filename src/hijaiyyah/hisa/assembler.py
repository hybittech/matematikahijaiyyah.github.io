"""H-ISA assembler: mnemonic text → binary instruction words."""

from __future__ import annotations

from typing import Dict, List

from .opcodes import OpCode

# Opcode name → integer mapping
_OP_MAP: Dict[str, int] = {}
for _name, _val in OpCode.__members__.items():
    _OP_MAP[_name.lower()] = _val.value


def assemble_line(line: str) -> int:
    """
    Assemble one line of H-ISA assembly into a 32-bit instruction word.

    Format: OPCODE [DST] [SRC1] [SRC2] [IMM]
    All fields default to 0 if omitted.
    Lines starting with ; are comments.
    """
    line = line.strip()

    # Skip empty lines and comments
    if not line or line.startswith(";"):
        return -1  # sentinel for "skip"

    # Strip inline comments
    if ";" in line:
        line = line[: line.index(";")].strip()

    parts = line.split()
    if not parts:
        return -1

    mnemonic = parts[0].lower()
    op = _OP_MAP.get(mnemonic, 0)

    dst = int(parts[1]) if len(parts) > 1 else 0
    s1 = int(parts[2]) if len(parts) > 2 else 0
    s2 = int(parts[3]) if len(parts) > 3 else 0
    imm = int(parts[4]) if len(parts) > 4 else 0

    return (
        (op << 24) | ((dst & 0xF) << 20) | ((s1 & 0xF) << 16) | ((s2 & 0xF) << 12) | (imm & 0xFFF)
    )


def assemble(source: str) -> List[int]:
    """
    Assemble a multi-line H-ISA program.
    Returns list of 32-bit instruction words.
    """
    result: List[int] = []
    for line in source.strip().split("\n"):
        word = assemble_line(line)
        if word >= 0:  # skip comments and empty lines
            result.append(word)
    return result
