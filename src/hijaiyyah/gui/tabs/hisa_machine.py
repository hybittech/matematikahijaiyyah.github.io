"""
Tab: H-ISA Machine — Interactive CPU Emulator
===============================================
Full virtual machine interface with:
  - Program editor (H-ISA assembly)
  - Step / Run / Reset controls
  - Register file visualization (GPR + H-Regs + Status)
  - Instruction trace log
  - Bytecode hex view
  - Quick-load demo programs
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional

from ...core.guards import compute_U
from ...core.master_table import MASTER_TABLE
from ...hisa.assembler import assemble
from ...hisa.machine import HISAMachine
from ...hisa.opcodes import InstructionWord
from ..theme import THEME
from ..widgets import OutputWriter, make_text

# ── Demo Programs (H-ISA Assembly) ───────────────────────────────

DEMO_PROGRAMS: Dict[str, str] = {
    "Load Ba": """\
; Load letter Ba (index 1) into H0
; Then check guard
CLOAD 0 0 0 1
VCHK  0 0 0 0
PRINT 0 0 0 0
HALT  0 0 0 0
""",
    "Add Ba + Sin": """\
; Load Ba into H0, Sin into H1
; Add them into H2
; Check guard on result
CLOAD 0 0 0 1
CLOAD 1 0 0 11
CADD  2 0 1 0
VCHK  0 2 0 0
PRINT 2 0 0 0
HALT  0 0 0 0
""",
    "String bsm": """\
; Compute Cod18("بسم") = v18(ب) + v18(س) + v18(م)
; Ba=1, Sin=11, Mim=23
CLOAD 0 0 0 1
CLOAD 1 0 0 11
CADD  2 0 1 0
CLOAD 1 0 0 23
CADD  2 2 1 0
VCHK  0 2 0 0
VRHO  0 2 0 0
PRINT 2 0 0 0
HALT  0 0 0 0
""",
    "All 28 Guard Check": """\
; Load and guard-check each of the 28 letters
CLOAD 0 0 0 0
VCHK  0 0 0 0
CLOAD 0 0 0 1
VCHK  0 0 0 0
CLOAD 0 0 0 2
VCHK  0 0 0 0
CLOAD 0 0 0 3
VCHK  0 0 0 0
CLOAD 0 0 0 4
VCHK  0 0 0 0
CLOAD 0 0 0 5
VCHK  0 0 0 0
CLOAD 0 0 0 6
VCHK  0 0 0 0
CLOAD 0 0 0 7
VCHK  0 0 0 0
CLOAD 0 0 0 8
VCHK  0 0 0 0
CLOAD 0 0 0 9
VCHK  0 0 0 0
HALT  0 0 0 0
""",
    "Norm + Distance": """\
; Load Alif (0) and Ha (26)
; Compute norms and distance
CLOAD 0 0 0 0
CLOAD 1 0 0 26
VNORM 0 0 0 0
VNORM 0 1 0 0
VDIST 0 0 1 0
HALT  0 0 0 0
""",
}


class HISAMachineTab:
    """
    Tab: H-ISA Machine — Interactive CPU Emulator

    Layout:
    ┌──────────────────┬──────────────────────────────┐
    │   ASM Editor     │     Register Display          │
    │   + Controls     │     + Status Flags            │
    │                  │     + H-Reg Contents           │
    ├──────────────────┴──────────────────────────────┤
    │              Execution Trace Log                 │
    └──────────────────────────────────────────────────┘
    """

    def __init__(self, notebook: ttk.Notebook, machine: HISAMachine) -> None:
        self._machine = machine
        self._table = MASTER_TABLE
        self._tab = ttk.Frame(notebook)
        notebook.add(self._tab, text="  ⚙ H-ISA Machine  ")

        # Widget references
        self._asm_editor: Optional[tk.Text] = None
        self._reg_display: Optional[tk.Text] = None
        self._trace_display: Optional[tk.Text] = None
        self._reg_out: Optional[OutputWriter] = None
        self._trace_out: Optional[OutputWriter] = None
        self._status_var = tk.StringVar(value="IDLE")
        self._pc_var = tk.StringVar(value="PC: 0")
        self._cycle_var = tk.StringVar(value="Cycle: 0")
        self._guard_var = tk.StringVar(value="GUARD: —")

        self._build()

    def _build(self) -> None:
        # ── Top section: editor + registers ──────────────────────
        top_paned = ttk.PanedWindow(self._tab, orient=tk.HORIZONTAL)
        top_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: ASM editor + controls
        left_frame = ttk.Frame(top_paned)
        top_paned.add(left_frame, weight=1)
        self._build_editor(left_frame)

        # Right: register display
        right_frame = ttk.Frame(top_paned)
        top_paned.add(right_frame, weight=1)
        self._build_registers(right_frame)

        # ── Bottom section: trace log ────────────────────────────
        bottom_frame = ttk.Frame(self._tab)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        self._build_trace(bottom_frame)

    def _build_editor(self, parent: ttk.Frame) -> None:
        """Build the assembly editor panel with controls."""
        # Header
        header = ttk.Frame(parent)
        header.pack(fill=tk.X)
        ttk.Label(
            header,
            text="H-ISA Assembly Program",
            font=THEME.font_ui_bold,
        ).pack(side=tk.LEFT)

        # Status indicators
        status_frame = ttk.Frame(header)
        status_frame.pack(side=tk.RIGHT)
        ttk.Label(status_frame, textvariable=self._pc_var).pack(side=tk.LEFT, padx=4)
        ttk.Label(status_frame, textvariable=self._cycle_var).pack(side=tk.LEFT, padx=4)
        ttk.Label(status_frame, textvariable=self._guard_var).pack(side=tk.LEFT, padx=4)

        # Editor
        self._asm_editor = tk.Text(
            parent,
            font=THEME.font_mono_lg,
            bg=THEME.text_bg,
            fg="#81ecec",
            insertbackground="#81ecec",
            wrap=tk.NONE,
            undo=True,
            height=12,
        )
        self._asm_editor.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self._asm_editor.insert("1.0", DEMO_PROGRAMS["Load Ba"])

        # Control buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            btn_frame,
            text="▶ Run All",
            command=self._run_all,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            btn_frame,
            text="⏭ Step",
            command=self._step_one,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            btn_frame,
            text="⟳ Reset",
            command=self._reset,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            btn_frame,
            text="📋 Load Program",
            command=self._load_program,
        ).pack(side=tk.LEFT, padx=2)

        # Demo program selector
        demo_frame = ttk.Frame(parent)
        demo_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(demo_frame, text="Demos:").pack(side=tk.LEFT)
        for name in DEMO_PROGRAMS:
            ttk.Button(
                demo_frame,
                text=name,
                command=lambda n=name: self._load_demo(n),
            ).pack(side=tk.LEFT, padx=2)

    def _build_registers(self, parent: ttk.Frame) -> None:
        """Build the register visualization panel."""
        ttk.Label(
            parent,
            text="Machine State",
            font=THEME.font_ui_bold,
        ).pack(anchor=tk.W)

        self._reg_display, _ = make_text(
            parent,
            font=THEME.font_mono,
            wrap=tk.NONE,
        )
        self._reg_out = OutputWriter(self._reg_display)
        self._reg_out.add_tags(
            {
                "header": {"foreground": THEME.hijaiyyah_fg, "font": (*THEME.font_mono, "bold")},
                "value": {"foreground": THEME.number_fg},
                "pass": {"foreground": THEME.success},
                "fail": {"foreground": THEME.error},
                "dim": {"foreground": THEME.dim_fg},
            }
        )

        self._refresh_registers()

    def _build_trace(self, parent: ttk.Frame) -> None:
        """Build the execution trace panel."""
        ttk.Label(
            parent,
            text="Execution Trace",
            font=THEME.font_ui_bold,
        ).pack(anchor=tk.W)

        self._trace_display, _ = make_text(
            parent,
            font=THEME.font_mono_sm,
            bg="#0a0a0a",
        )
        self._trace_out = OutputWriter(self._trace_display)
        self._trace_out.add_tags(
            {
                "cycle": {"foreground": THEME.dim_fg},
                "op": {"foreground": "#81ecec"},
                "pass": {"foreground": THEME.success},
                "fail": {"foreground": THEME.error},
            }
        )

    # ── Actions ──────────────────────────────────────────────────

    def _load_demo(self, name: str) -> None:
        """Load a demo program into the editor."""
        if self._asm_editor is None:
            return
        self._asm_editor.delete("1.0", tk.END)
        self._asm_editor.insert("1.0", DEMO_PROGRAMS.get(name, ""))
        self._reset()

    def _load_program(self) -> None:
        """Assemble the editor contents and load into machine."""
        if self._asm_editor is None:
            return

        source = self._asm_editor.get("1.0", tk.END).strip()
        if not source:
            return

        self._machine.reset()

        try:
            bytecode = assemble(source)
            self._machine.load_program(bytecode)
            self._status_var.set("LOADED")

            if self._trace_out:
                self._trace_out.clear()
                self._trace_out.writeln(f"Program loaded: {len(bytecode)} instructions")
                self._trace_out.writeln(f"Bytecode: {' '.join(f'{x:08X}' for x in bytecode)}")
                self._trace_out.writeln("")

        except Exception as e:
            if self._trace_out:
                self._trace_out.clear()
                self._trace_out.writeln(f"ASSEMBLY ERROR: {e}", "fail")

        self._refresh_registers()

    def _step_one(self) -> None:
        """Execute a single instruction."""
        if not self._machine.code:
            self._load_program()
            if not self._machine.code:
                return

        entry = self._machine.step()
        if entry is not None and self._trace_out:
            tag = "pass" if "PASS" in entry.description else "op"
            if "FAIL" in entry.description:
                tag = "fail"
            self._trace_out.writeln(
                f"  [{entry.cycle:04d}] {entry.description}",
                tag,
            )

        self._refresh_registers()
        self._update_status()

    def _run_all(self) -> None:
        """Load and execute entire program."""
        self._load_program()
        if not self._machine.code:
            return

        max_cycles = 1000
        cycle = 0

        while cycle < max_cycles:
            entry = self._machine.step()
            if entry is None:
                break

            if self._trace_out:
                tag = "pass" if "PASS" in entry.description else "op"
                if "FAIL" in entry.description:
                    tag = "fail"
                self._trace_out.writeln(
                    f"  [{entry.cycle:04d}] {entry.description}",
                    tag,
                )

            if "HALT" in entry.description:
                break

            cycle += 1

        if cycle >= max_cycles and self._trace_out:
            self._trace_out.writeln(
                f"\n  ⚠ Execution limit reached ({max_cycles} cycles)",
                "fail",
            )

        if self._trace_out:
            self._trace_out.writeln(
                f"\n  Done: {self._machine.cycle} cycles executed",
                "pass",
            )

        self._refresh_registers()
        self._update_status()

    def _reset(self) -> None:
        """Reset machine to initial state."""
        self._machine.reset()
        self._status_var.set("IDLE")
        self._pc_var.set("PC: 0")
        self._cycle_var.set("Cycle: 0")
        self._guard_var.set("GUARD: —")

        if self._trace_out:
            self._trace_out.clear()
            self._trace_out.writeln("Machine reset.")

        self._refresh_registers()

    # ── Display ──────────────────────────────────────────────────

    def _update_status(self) -> None:
        """Update status bar variables."""
        state = self._machine.dump_state()
        self._pc_var.set(f"PC: {state['pc']}")
        self._cycle_var.set(f"Cycle: {self._machine.cycle}")

        sr = state.get("sr", {})
        guard = sr.get("guard", False)
        self._guard_var.set(f"GUARD: {'PASS' if guard else 'FAIL'}")

        if state["pc"] >= len(self._machine.code):
            self._status_var.set("HALTED")
        else:
            self._status_var.set("RUNNING")

    def _refresh_registers(self) -> None:
        """Refresh the register display with current machine state."""
        if self._reg_out is None:
            return

        state = self._machine.dump_state()
        sr = state.get("sr", {})
        hreg = state.get("hreg", [])

        self._reg_out.clear()

        # ── Header
        self._reg_out.writeln("H-ISA MACHINE STATE", "header")
        self._reg_out.writeln("=" * 50)
        self._reg_out.writeln()

        # ── Program Counter & Status
        self._reg_out.writeln("CONTROL REGISTERS", "header")
        self._reg_out.writeln(f"  PC      = {state['pc']}", "value")
        self._reg_out.writeln(f"  Cycle   = {self._machine.cycle}", "value")
        self._reg_out.writeln(f"  Program = {len(self._machine.code)} instructions")
        self._reg_out.writeln()

        # ── Status Register
        guard_pass = sr.get("guard", False)
        zero_flag = sr.get("zero", False)

        self._reg_out.writeln("STATUS REGISTER (SR)", "header")
        guard_tag = "pass" if guard_pass else "fail"
        self._reg_out.writeln(f"  GUARD_PASS = {guard_pass}", guard_tag)
        self._reg_out.writeln(f"  ZERO       = {zero_flag}", "dim")
        self._reg_out.writeln()

        # ── H-Registers (codex registers)
        self._reg_out.writeln("CODEX REGISTERS (H0–H3)", "header")

        slot_names = [
            "Θ̂",
            "Na",
            "Nb",
            "Nd",
            "Kp",
            "Kx",
            "Ks",
            "Ka",
            "Kc",
            "Qp",
            "Qx",
            "Qs",
            "Qa",
            "Qc",
            "AN",
            "AK",
            "AQ",
            "H*",
        ]

        for i in range(min(4, len(hreg))):
            h = hreg[i]
            is_zero = all(x == 0 for x in h)

            if is_zero:
                self._reg_out.writeln(f"  H{i} = [all zeros]", "dim")
            else:
                self._reg_out.writeln(f"  H{i}:", "value")

                # Show as formatted vector
                vec_str = "(" + ", ".join(str(x) for x in h) + ")"
                self._reg_out.writeln(f"    v₁₈ = {vec_str}", "value")

                # Show named components (non-zero only)
                nonzero = []
                for j, val in enumerate(h):
                    if val != 0 and j < len(slot_names):
                        nonzero.append(f"{slot_names[j]}={val}")
                if nonzero:
                    self._reg_out.writeln(f"    Active: {', '.join(nonzero)}", "value")

                # Show decomposition
                if h[0] > 0 or any(x > 0 for x in h):
                    U = compute_U(h)
                    rho = h[0] - U
                    self._reg_out.writeln(
                        f"    Θ̂={h[0]} U={U} ρ={rho} (mod4={h[0] % 4})",
                        "dim",
                    )

                # Try to identify the letter
                letter = self._identify_vector(h)
                if letter:
                    self._reg_out.writeln(f"    Letter: {letter}", "pass")

            self._reg_out.writeln()

        # ── GPR (general purpose registers)
        gpr = state.get("gpr", [])
        nonzero_gpr = [(i, v) for i, v in enumerate(gpr) if v != 0]
        if nonzero_gpr:
            self._reg_out.writeln("GENERAL PURPOSE REGISTERS", "header")
            for i, v in nonzero_gpr:
                self._reg_out.writeln(f"  R{i:<2d} = {v}", "value")
            self._reg_out.writeln()

        # ── Instruction at PC
        if state["pc"] < len(self._machine.code):
            raw = self._machine.code[state["pc"]]
            iw = InstructionWord(raw)
            self._reg_out.writeln("NEXT INSTRUCTION", "header")
            self._reg_out.writeln(f"  Address:  {state['pc']}", "dim")
            self._reg_out.writeln(f"  Hex:      0x{raw:08X}", "dim")
            self._reg_out.writeln(f"  Decoded:  {iw.disassemble()}", "value")
        else:
            self._reg_out.writeln("PROGRAM COMPLETE", "pass")

    def _identify_vector(self, vec: list) -> Optional[str]:
        """Try to identify which letter a vector corresponds to."""
        for entry in self._table.all_entries():
            if list(entry.vector) == vec:
                return f"{entry.char} ({entry.name})"
        return None
