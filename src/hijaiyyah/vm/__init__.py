"""
HVM — Hybit Virtual Machine
=============================
Facade module: execute .hbc bytecode

5 components (Bab III §3.30):
  1. Loader      — parse .hbc, verify header
  2. Interpreter — fetch-decode-execute loop
  3. Hybit Engine — native ops (HCADD, HPROJ, etc.)
  4. Guard System — G1–G4, T1–T2 per-operation
  5. HCHECK      — periodic runtime integrity

Re-exports from hisa/machine.py + hisa/hcheck.py + core/guards.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, List, Optional, Tuple

# ── Re-export existing implementations ────────────────────────

try:
    from hijaiyyah.hisa.machine import HISAMachine as _Machine
except ImportError:
    _Machine = None

# hisa.hcheck exports HCHECK, not HCheck, and its scan() takes raw v18
# vectors where this class works in HybitRegister objects. The delegation
# below asked for a .check() method that HCHECK does not have, so it could
# never have fired even with the name spelled correctly. The implementation
# in this file is the one that runs.

try:
    from hijaiyyah.core.guards import (
        GuardResult as _GuardResult,
    )
    from hijaiyyah.core.guards import (
        check_guards as _check_guards,
    )
except ImportError:
    _check_guards = None
    _GuardResult = None

try:
    from hijaiyyah.core.master_table import MASTER_TABLE
except ImportError:
    MASTER_TABLE = None

try:
    from hijaiyyah.assembler import HBC_MAGIC_INT, HBCHeader
except ImportError:
    HBCHeader = None
    HBC_MAGIC_INT = 0x48425954


# ── Register & flags ──────────────────────────────────────────

NUM_REGISTERS = 16
HYBIT_DIM = 18
STACK_MAX = 1024


class ExitCode(IntEnum):
    SUCCESS = 0
    GUARD_FAIL = 1
    IDENTITY_FAIL = 2
    CORRUPTION = 3
    RUNTIME_ERROR = 255


@dataclass
class HybitRegister:
    """One HVM register — holds a full 18D hybit vector."""
    value: List[int] = field(default_factory=lambda: [0] * HYBIT_DIM)
    has_hybit: bool = False

    def load(self, v18: List[int]):
        if len(v18) != HYBIT_DIM:
            raise ValueError(f"Expected {HYBIT_DIM}D, got {len(v18)}D")
        self.value = list(v18)
        self.has_hybit = True

    def clear(self):
        self.value = [0] * HYBIT_DIM
        self.has_hybit = False


@dataclass
class VMFlags:
    """HVM comparison/status flags."""
    zero: bool = False
    equal: bool = False
    guard_pass: bool = True
    guard_fail_id: str = ""
    guard_strict: bool = False


# ── Guard System ──────────────────────────────────────────────

@dataclass
class GuardStatus:
    passed: bool = True
    failed_guards: List[str] = field(default_factory=list)

    @property
    def failed(self) -> bool:
        return not self.passed


class GuardSystem:
    """
    Per-operation guard validation: G1–G4, T1–T2.
    O(1) per check — from Bab III §3.4.
    """

    def check(self, v18: List[int]) -> GuardStatus:
        """Validate a single hybit vector."""
        if _check_guards is not None:
            try:
                result = _check_guards(v18)
                if hasattr(result, 'passed'):
                    return GuardStatus(
                        passed=result.passed,
                        failed_guards=getattr(result, 'failed', [])
                    )
                return GuardStatus(passed=bool(result))
            except Exception:
                pass
        return self._check_direct(v18)

    def _check_direct(self, v: List[int]) -> GuardStatus:
        """Direct guard implementation."""
        if len(v) < HYBIT_DIM:
            return GuardStatus(False, ["DIMENSION"])

        fails = []
        # G1: A_N = N_a + N_b + N_d
        if v[14] != v[1] + v[2] + v[3]:
            fails.append("G1")
        # G2: A_K = K_p + K_x + K_s + K_a + K_c
        if v[15] != v[4] + v[5] + v[6] + v[7] + v[8]:
            fails.append("G2")
        # G3: A_Q = Q_p + Q_x + Q_s + Q_a + Q_c
        if v[16] != v[9] + v[10] + v[11] + v[12] + v[13]:
            fails.append("G3")
        # G4: ρ = Θ̂ − (Q_x + Q_s + Q_a + 4·Q_c) ≥ 0
        U = v[10] + v[11] + v[12] + 4 * v[13]
        if v[0] < U:
            fails.append("G4")
        # T1: K_s > 0 ⇒ Q_c ≥ 1
        if v[6] > 0 and v[13] < 1:
            fails.append("T1")
        # T2: K_c > 0 ⇒ Q_c ≥ 1
        if v[8] > 0 and v[13] < 1:
            fails.append("T2")

        return GuardStatus(
            passed=len(fails) == 0,
            failed_guards=fails,
        )


# ── HCHECK — Runtime Integrity Monitor ───────────────────────

@dataclass
class HCheckResult:
    passed: bool = True
    failures: List[str] = field(default_factory=list)


class HCheck:
    """
    Runtime integrity monitor — periodic state scan.
    Different from Guard: Guard = per-operation, HCHECK = periodic.
    Bab III §3.31.
    """

    def __init__(self):
        self._guard = GuardSystem()

    def scan(self, registers: List[HybitRegister],
             stack: Optional[List] = None) -> HCheckResult:
        """Scan all registers and stack for corruption."""
        failures = []
        for i, reg in enumerate(registers):
            if reg.has_hybit:
                status = self._guard.check(reg.value)
                if not status.passed:
                    failures.append(
                        f"R{i}: {status.failed_guards}"
                    )

        if stack:
            for i, entry in enumerate(stack):
                if isinstance(entry, list) and len(entry) == HYBIT_DIM:
                    status = self._guard.check(entry)
                    if not status.passed:
                        failures.append(
                            f"Stack[{i}]: {status.failed_guards}"
                        )

        return HCheckResult(
            passed=len(failures) == 0,
            failures=failures,
        )


# ── Hybit Engine ──────────────────────────────────────────────

class HybitEngine:
    """Native hybit operations: HCADD, HPROJ, HDCMP, etc."""

    def __init__(self, guard: GuardSystem):
        self.guard = guard

    def cadd(self, a: List[int], b: List[int]) -> List[int]:
        """HCADD: component-wise addition."""
        return [a[i] + b[i] for i in range(HYBIT_DIM)]

    def proj(self, v: List[int], layer: str) -> Any:
        """HPROJ: project to subspace Θ/N/K/Q."""
        mapping = {
            "THETA": (0, 1),
            "N": (1, 4),
            "K": (4, 9),
            "Q": (9, 14),
        }
        if layer.upper() not in mapping:
            raise ValueError(f"Unknown layer: {layer}")
        lo, hi = mapping[layer.upper()]
        return v[lo:hi]

    def decompose(self, v: List[int]) -> Tuple[int, int]:
        """HDCMP: decompose into (U, ρ)."""
        theta = v[0]
        U = v[10] + v[11] + v[12] + 4 * v[13]
        rho = theta - U
        return U, rho

    def norm2(self, v: List[int]) -> int:
        """HNRM2: squared norm of v₁₄."""
        return sum(x * x for x in v[:14])

    def dist(self, a: List[int], b: List[int]) -> float:
        """HDIST: Euclidean distance."""
        return sum((a[i] - b[i]) ** 2 for i in range(14)) ** 0.5


# ── HVM — Main Virtual Machine ───────────────────────────────

class HVM:
    """
    Hybit Virtual Machine — executes .hbc bytecode.

    5 components:
      Loader, Interpreter, HybitEngine, GuardSystem, HCheck

    Bab III §3.30.
    """

    VERSION = "1.0.0"

    def __init__(self, har_path: Optional[str] = None):
        self.registers = [HybitRegister() for _ in range(NUM_REGISTERS)]
        self.stack: List[Any] = []
        self.flags = VMFlags()
        self.guard = GuardSystem()
        self.hcheck = HCheck()
        self.engine = HybitEngine(self.guard)
        self.pc = 0
        self.running = False
        self.exit_code = ExitCode.SUCCESS
        self._machine = self._try_init_machine()

    @staticmethod
    def _try_init_machine():
        if _Machine is None:
            return None
        try:
            return _Machine()
        except Exception:
            return None

    def load_hybit(self, reg_idx: int, v18: List[int]):
        """HLOAD: load hybit into register."""
        self.registers[reg_idx].load(v18)

    def cadd(self, dst: int, src1: int, src2: int):
        """HCADD: codex addition with optional guard."""
        a = self.registers[src1].value
        b = self.registers[src2].value
        result = self.engine.cadd(a, b)
        if self.flags.guard_strict:
            status = self.guard.check(result)
            if not status.passed:
                self.flags.guard_pass = False
                self.flags.guard_fail_id = str(status.failed_guards)
                return
        self.registers[dst].load(result)

    def guard_check(self, reg_idx: int) -> GuardStatus:
        """HGRD: explicit guard check."""
        status = self.guard.check(self.registers[reg_idx].value)
        self.flags.guard_pass = status.passed
        return status

    def proj(self, dst: int, src: int, layer: str):
        """HPROJ: projection."""
        result = self.engine.proj(self.registers[src].value, layer)
        # Store as partial vector
        self.registers[dst].value = (
            list(result) + [0] * (HYBIT_DIM - len(result))
        )
        self.registers[dst].has_hybit = True

    def run_hcheck(self) -> HCheckResult:
        """Run periodic integrity scan."""
        return self.hcheck.scan(self.registers, self.stack)

    def reset(self):
        """Reset VM state."""
        for reg in self.registers:
            reg.clear()
        self.stack.clear()
        self.flags = VMFlags()
        self.pc = 0
        self.running = False
        self.exit_code = ExitCode.SUCCESS


__all__ = [
    "HVM",
    "HYBIT_DIM",
    "NUM_REGISTERS",
    "STACK_MAX",
    "ExitCode",
    "GuardStatus",
    "GuardSystem",
    "HCheck",
    "HCheckResult",
    "HybitEngine",
    "HybitRegister",
    "VMFlags",
]
