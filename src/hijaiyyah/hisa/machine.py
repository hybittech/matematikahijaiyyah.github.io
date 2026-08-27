"""
H-ISA Machine: fetch-decode-execute cycle.

Bab III §3.30: HVM — Hybit Virtual Machine
  - 16 H-registers (R0–R15), each holding one 18D hybit
  - Hybit Engine: native operations (HCADD, HGRD, HPROJ, HDCMP, HEXMT)
  - Guard System: per-operation validation G1–G4, T1–T2
  - HCHECK: periodic integrity monitor
  - GUARD_STRICT mode: every HCADD auto-checks guard
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ..core.exomatrix import build_exomatrix
from ..core.guards import compute_U, full_guard_check, guard_check
from ..core.master_table import MasterTable
from .opcodes import InstructionWord, OpCode
from .registers import HREG_COUNT, RegisterFile


@dataclass
class TraceEntry:
    """One line in the execution trace."""

    cycle: int
    description: str


class HISAMachine:
    """
    H-ISA Virtual Machine (HVM).

    Bab III §3.30 — 5 components:
      1. Loader: parse bytecode, setup memory
      2. Interpreter: fetch-decode-execute loop
      3. Hybit Engine: native hybit operations
      4. Guard System: per-operation G1–G4, T1–T2
      5. HCHECK: periodic integrity monitor
    """

    def __init__(
        self,
        table: MasterTable,
        *,
        guard_strict: bool = False,
        hcheck_interval: int = 100,
    ) -> None:
        self.table = table
        self.regs = RegisterFile()
        self.code: List[int] = []
        self.trace: List[TraceEntry] = []
        self.cycle: int = 0
        self._halted: bool = False
        self._exit_code: int = 0

        # Bab III §3.25 flags
        self.guard_strict = guard_strict
        self.hcheck_interval = hcheck_interval

    def load_program(self, code: List[int]) -> None:
        """Load bytecode into code memory."""
        self.code = list(code)
        self.regs.pc = 0
        self._halted = False
        self._exit_code = 0

    def step(self) -> Optional[TraceEntry]:
        """Execute one instruction. Returns trace entry or None if done."""
        if self._halted or self.regs.pc >= len(self.code):
            return None

        # HCHECK periodic scan (§3.31)
        if self.hcheck_interval > 0 and self.cycle % self.hcheck_interval == 0 and self.cycle > 0:
            corruption = self._hcheck_scan()
            if corruption:
                entry = TraceEntry(self.cycle, f"HCHECK CORRUPTION: {corruption}")
                self.trace.append(entry)
                self._halted = True
                return entry

        raw = self.code[self.regs.pc]
        iw = InstructionWord(raw)
        self.regs.pc += 1
        self.cycle += 1

        desc = self._execute(iw)
        entry = TraceEntry(self.cycle, desc)
        self.trace.append(entry)
        return entry

    def run(self) -> List[TraceEntry]:
        """Run until HALT or end of code. Returns all trace entries."""
        result: List[TraceEntry] = []
        while True:
            entry = self.step()
            if entry is None:
                break
            result.append(entry)
        return result

    def _execute(self, iw: InstructionWord) -> str:
        """Execute a decoded instruction. Returns description string."""
        op = iw.opcode
        dst = iw.dst % HREG_COUNT
        s1 = iw.src1 % HREG_COUNT
        s2 = iw.src2 % HREG_COUNT
        imm = iw.imm

        entries = self.table.all_entries()

        # ── HLOAD (CLOAD): load letter into H-register ──────────
        if op == OpCode.HLOAD:
            if imm < len(entries):
                entry = entries[imm]
                self.regs.hreg[dst] = list(entry.vector)
                return f"HLOAD H{dst} ← {entry.char} ({entry.name}) [idx={imm}]"
            return f"HLOAD H{dst} ← INVALID INDEX {imm}"

        # ── HCADD (CADD): H[dst] = H[s1] + H[s2] ──────────────
        if op == OpCode.HCADD:
            a = self.regs.hreg[s1]
            b = self.regs.hreg[s2]
            result = [a[i] + b[i] for i in range(18)]

            # GUARD_STRICT mode (§3.25 bit 2)
            if self.guard_strict:
                if not guard_check(result):
                    self.regs.sr.guard_pass = False
                    return f"HCADD H{dst} = H{s1} + H{s2} → GUARD_FAIL (strict mode)"
                self.regs.sr.guard_pass = True

            self.regs.hreg[dst] = result
            return f"HCADD H{dst} = H{s1} + H{s2}"

        # ── HGRD (VCHK): guard check ────────────────────────────
        if op == OpCode.HGRD:
            h = self.regs.hreg[s1]
            ok = guard_check(h)
            self.regs.sr.guard_pass = ok
            return f"HGRD H{s1} → {'PASS ✓' if ok else 'FAIL ✗'}"

        # ── HPROJ: projection to layer ──────────────────────────
        if op == OpCode.HPROJ:
            h = self.regs.hreg[s1]
            layer = imm & 0x3
            r = [0] * 18
            if layer == 0:  # THETA
                r[0] = h[0]
                label = "Θ"
            elif layer == 1:  # N
                r[1], r[2], r[3] = h[1], h[2], h[3]
                label = "N"
            elif layer == 2:  # K
                for k in range(4, 9):
                    r[k] = h[k]
                label = "K"
            else:  # Q
                for k in range(9, 14):
                    r[k] = h[k]
                label = "Q"
            self.regs.hreg[dst] = r
            return f"HPROJ H{dst} = Π_{label}(H{s1})"

        # ── HDCMP: decompose Θ̂ → (U, ρ) ────────────────────────
        if op == OpCode.HDCMP:
            h = self.regs.hreg[s1]
            U = compute_U(h)
            rho = h[0] - U
            self.regs.gpr[0] = U
            self.regs.gpr[1] = rho
            return f"HDCMP H{s1}: U={U}, ρ={rho} → GPR[0],GPR[1]"

        # ── HNRM2: squared norm ─────────────────────────────────
        if op == OpCode.HNRM2:
            h = self.regs.hreg[s1]
            n2 = sum(x * x for x in h[:14])
            self.regs.gpr[0] = n2
            return f"HNRM2 GPR[0] = ‖H{s1}‖² = {n2}"

        # ── HDIST: squared Euclidean distance ───────────────────
        if op == OpCode.HDIST:
            a = self.regs.hreg[s1]
            b = self.regs.hreg[s2]
            d2 = sum((a[i] - b[i]) ** 2 for i in range(14))
            self.regs.gpr[0] = d2
            return f"HDIST GPR[0] = ‖H{s1} - H{s2}‖² = {d2}"

        # ── HEXMT: build exomatrix ──────────────────────────────
        if op == OpCode.HEXMT:
            h = self.regs.hreg[s1]
            exo = build_exomatrix(h)
            # Store exomatrix rows in consecutive registers dst..dst+4
            for row_idx in range(5):
                reg_idx = (dst + row_idx) % HREG_COUNT
                r = [0] * 18
                for col_idx in range(5):
                    r[col_idx] = exo[row_idx][col_idx]
                self.regs.hreg[reg_idx] = r
            return f"HEXMT H{dst}..H{(dst+4)%HREG_COUNT} ← Exo(H{s1})"

        # ── HCHK: runtime integrity check ───────────────────────
        if op == OpCode.HCHK:
            h = self.regs.hreg[s1]
            detail = full_guard_check(h)
            if detail["all_pass"]:
                return f"HCHK H{s1} → INTEGRITY OK"
            failed = [k for k, v in detail.items() if k != "all_pass" and not v]
            return f"HCHK H{s1} → INTEGRITY FAIL: {failed}"

        # ── CSUB: H[dst] = H[s1] - H[s2] (14D) ────────────────
        if op == OpCode.CSUB:
            a = self.regs.hreg[s1]
            b = self.regs.hreg[s2]
            self.regs.hreg[dst] = [a[i] - b[i] for i in range(14)] + [0] * 4
            return f"CSUB H{dst} = H{s1} - H{s2} (14D)"

        # ── VMOV: copy register ─────────────────────────────────
        if op == OpCode.VMOV:
            self.regs.hreg[dst] = list(self.regs.hreg[s1])
            return f"VMOV H{dst} = H{s1}"

        # ── PRINT: output register ──────────────────────────────
        if op == OpCode.PRINT:
            h = self.regs.hreg[dst]
            return f"PRINT H{dst} = ({', '.join(str(x) for x in h)})"

        # ── HALT: stop execution ────────────────────────────────
        if op == OpCode.HALT:
            self._halted = True
            self._exit_code = imm
            return f"HALT — execution stopped (code={imm})"

        # ── Legacy VPROJ_T / VPROJ_N / VPROJ_K / VPROJ_Q ───────
        if op == OpCode.VPROJ_T:
            h = self.regs.hreg[s1]
            self.regs.hreg[dst] = [h[0]] + [0] * 17
            return f"VPROJ_T H{dst} = Π_Θ(H{s1})"

        if op == OpCode.VPROJ_N:
            h = self.regs.hreg[s1]
            r = [0] * 18
            r[1], r[2], r[3] = h[1], h[2], h[3]
            self.regs.hreg[dst] = r
            return f"VPROJ_N H{dst} = Π_N(H{s1})"

        if op == OpCode.VPROJ_K:
            h = self.regs.hreg[s1]
            r = [0] * 18
            for k in range(4, 9):
                r[k] = h[k]
            self.regs.hreg[dst] = r
            return f"VPROJ_K H{dst} = Π_K(H{s1})"

        if op == OpCode.VPROJ_Q:
            h = self.regs.hreg[s1]
            r = [0] * 18
            for k in range(9, 14):
                r[k] = h[k]
            self.regs.hreg[dst] = r
            return f"VPROJ_Q H{dst} = Π_Q(H{s1})"

        # ── Integer ops ─────────────────────────────────────────
        if op == OpCode.IADD:
            self.regs.gpr[dst % 18] = self.regs.gpr[s1 % 18] + self.regs.gpr[s2 % 18]
            return f"IADD GPR[{dst%18}] = GPR[{s1%18}] + GPR[{s2%18}]"

        if op == OpCode.ISUB:
            self.regs.gpr[dst % 18] = self.regs.gpr[s1 % 18] - self.regs.gpr[s2 % 18]
            return f"ISUB GPR[{dst%18}] = GPR[{s1%18}] - GPR[{s2%18}]"

        if op == OpCode.IMUL:
            self.regs.gpr[dst % 18] = self.regs.gpr[s1 % 18] * self.regs.gpr[s2 % 18]
            return f"IMUL GPR[{dst%18}] = GPR[{s1%18}] * GPR[{s2%18}]"

        if op == OpCode.ICMP:
            a_val = self.regs.gpr[s1 % 18]
            b_val = self.regs.gpr[s2 % 18]
            self.regs.sr.zero = (a_val == b_val)
            return f"ICMP GPR[{s1%18}]={a_val} vs GPR[{s2%18}]={b_val}"

        # ── Legacy scalar ops ───────────────────────────────────
        if op == OpCode.VDIST:
            a = self.regs.hreg[s1]
            b = self.regs.hreg[s2]
            d2 = sum((a[i] - b[i]) ** 2 for i in range(14))
            self.regs.gpr[0] = d2
            return f"VDIST GPR[0] = ‖H{s1} - H{s2}‖² = {d2}"

        if op == OpCode.VRHO:
            h = self.regs.hreg[s1]
            U = compute_U(h)
            rho = h[0] - U
            self.regs.gpr[0] = rho
            return f"VRHO GPR[0] = ρ(H{s1}) = Θ̂({h[0]}) - U({U}) = {rho}"

        if op == OpCode.VNORM:
            h = self.regs.hreg[s1]
            n2 = sum(x * x for x in h[:14])
            self.regs.gpr[0] = n2
            return f"VNORM GPR[0] = ‖H{s1}‖² = {n2}"

        if op == OpCode.VDOT:
            a = self.regs.hreg[s1]
            b = self.regs.hreg[s2]
            ip = sum(a[i] * b[i] for i in range(14))
            self.regs.gpr[0] = ip
            return f"VDOT GPR[0] = ⟨H{s1}, H{s2}⟩ = {ip}"

        # ── Control Flow ────────────────────────────────────────
        if op == OpCode.JMP:
            self.regs.pc = imm
            return f"JMP → {imm}"

        if op == OpCode.JGP:
            if self.regs.sr.guard_pass:
                self.regs.pc = imm
                return f"JGP → {imm} (guard PASS)"
            return "JGP — no jump (guard FAIL)"

        if op == OpCode.JGF:
            if not self.regs.sr.guard_pass:
                self.regs.pc = imm
                return f"JGF → {imm} (guard FAIL)"
            return "JGF — no jump (guard PASS)"

        if op == OpCode.JNP:
            if not self.regs.sr.guard_pass:
                self.regs.pc = imm
                return f"JNP → {imm} (not pass)"
            return "JNP — no jump (pass)"

        if op == OpCode.JEQ:
            if self.regs.sr.zero:
                self.regs.pc = imm
                return f"JEQ → {imm} (equal)"
            return "JEQ — no jump (not equal)"

        if op == OpCode.JNE:
            if not self.regs.sr.zero:
                self.regs.pc = imm
                return f"JNE → {imm} (not equal)"
            return "JNE — no jump (equal)"

        # ── Subroutine ──────────────────────────────────────────
        if op == OpCode.CALL:
            self.regs.push(self.regs.pc)
            self.regs.pc = imm
            return f"CALL → {imm} (return addr pushed)"

        if op == OpCode.RET:
            ret_addr = self.regs.pop()
            self.regs.pc = ret_addr
            return f"RET → {ret_addr}"

        # ── Stack ───────────────────────────────────────────────
        if op == OpCode.PUSH:
            self.regs.push(self.regs.gpr[s1 % 18])
            return f"PUSH GPR[{s1%18}]"

        if op == OpCode.POP:
            self.regs.gpr[dst % 18] = self.regs.pop()
            return f"POP → GPR[{dst%18}]"

        return f"UNKNOWN opcode 0x{op:02X}"

    def _hcheck_scan(self) -> Optional[str]:
        """
        HCHECK: periodic integrity scan of all H-registers.

        §3.31: Detects corruption — bit flip, buffer overflow.
        Scans all registers and validates guards on each.
        """
        for i in range(HREG_COUNT):
            h = self.regs.hreg[i]
            if any(x != 0 for x in h):  # Skip zero registers
                if any(x < 0 for x in h):
                    return f"H{i}: negative component detected"
                # Only check guard on non-zero registers that look like hyperbolic data
                if h[14] != 0 or h[15] != 0 or h[16] != 0:
                    if not guard_check(h):
                        return f"H{i}: guard check failed"
        return None

    def dump_state(self) -> dict:
        """Return full machine state as dict."""
        return {
            "pc": self.regs.pc,
            "cycle": self.cycle,
            "halted": self._halted,
            "exit_code": self._exit_code,
            "gpr": list(self.regs.gpr),
            "hreg": [list(h) for h in self.regs.hreg],
            "sr": {
                "guard": self.regs.sr.guard_pass,
                "zero": self.regs.sr.zero,
                "overflow": self.regs.sr.overflow,
            },
            "stack_depth": len(self.regs.stack),
            "guard_strict": self.guard_strict,
        }

    def reset(self) -> None:
        """Reset machine to initial state."""
        self.regs = RegisterFile()
        self.code = []
        self.trace = []
        self.cycle = 0
        self._halted = False
        self._exit_code = 0
