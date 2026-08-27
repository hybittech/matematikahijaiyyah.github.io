"""
Register file for the H-ISA machine.

Bab III §3.30 specification:
  - 16 H-registers (R0–R15), each holding one 18D hybit vector
  - General purpose registers (GPR) for scalar values
  - Status flags for guard pass, zero, overflow
  - Stack for subroutine support (CALL/RET)
  - Program counter

Total register file: 16 × 18 × 2 = 576 bytes.
"""

from dataclasses import dataclass, field
from typing import List

HREG_COUNT: int = 16
GPR_COUNT: int = 18
STACK_SIZE: int = 1024


@dataclass
class StatusFlags:
    guard_pass: bool = False
    zero: bool = False
    overflow: bool = False


@dataclass
class RegisterFile:
    gpr: List[int] = field(default_factory=lambda: [0] * GPR_COUNT)
    hreg: List[List[int]] = field(
        default_factory=lambda: [[0] * 18 for _ in range(HREG_COUNT)]
    )
    sr: StatusFlags = field(default_factory=StatusFlags)
    pc: int = 0
    stack: List[int] = field(default_factory=list)

    def push(self, value: int) -> None:
        """Push value onto the stack."""
        if len(self.stack) >= STACK_SIZE:
            raise OverflowError("Stack overflow: exceeded 1024 entries")
        self.stack.append(value)

    def pop(self) -> int:
        """Pop value from the stack."""
        if not self.stack:
            raise IndexError("Stack underflow: empty stack")
        return self.stack.pop()

