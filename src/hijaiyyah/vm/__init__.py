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

from hijaiyyah.assembler import HBC_MAGIC_INT, HBCHeader

# hisa.hcheck exports HCHECK, not HCheck, and its scan() takes raw v18
# vectors where this class works in HybitRegister objects. The delegation
# below asked for a .check() method that HCHECK does not have, so it could
# never have fired even with the name spelled correctly. The implementation
# in this file is the one that runs.
# core.guards exports guard_check, full_guard_check and guard_detail — there
# has never been a check_guards or a GuardResult. The guarded import failed
# silently, so GuardSystem fell back to its own copy of G1-G4 and T1-T2.
from hijaiyyah.core.guards import full_guard_check
from hijaiyyah.core.master_table import MASTER_TABLE

# ── Re-export existing implementations ────────────────────────
# First-party and always importable — the try/except that used to wrap this
# guarded against nothing, and assigning None to a class name is what mypy
# was objecting to. tests/test_integrity/test_no_dead_delegation.py keeps
# every remaining guarded import honest.
from hijaiyyah.hisa.machine import HISAMachine as _Machine

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
        """
        Validate a single hybit vector.

        Delegates to core.guards.full_guard_check, which is the definition the
        RTL, the JavaScript engine and the language all diff against. This
        class used to carry its own transcription of G1-G4 and T1-T2 because
        the import above was reaching for a name that does not exist.
        """
        if len(v18) < HYBIT_DIM:
            return GuardStatus(False, ["DIMENSION"])

        results = full_guard_check(v18)
        return GuardStatus(
            passed=results["all_pass"],
            failed_guards=[
                name
                for name in ("G1", "G2", "G3", "G4", "T1", "T2")
                if not results[name]
            ],
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
        return float(sum((a[i] - b[i]) ** 2 for i in range(14)) ** 0.5)


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
