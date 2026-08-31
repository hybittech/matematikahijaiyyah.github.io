"""
Tab: Bytecode Inspector — Interactive H-ISA Instruction Decoder
================================================================
Real-time instruction word decoder with:
  - Live hex input with instant decode
  - Visual bit-field breakdown
  - Opcode reference table
  - Instruction builder (reverse: pick opcode → get hex)
  - Batch decode mode
  - Copy-to-clipboard
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional

from ...core.master_table import MASTER_TABLE
from ...hisa.opcodes import InstructionWord
from ..theme import THEME
from ..widgets import OutputWriter, make_text

# ── Opcode documentation ─────────────────────────────────────────

OPCODE_DOCS: Dict[int, Dict[str, str]] = {
    0x01: {
        "name": "CLOAD",
        "syntax": "CLOAD dst 0 0 imm",
        "desc": "Load letter[imm] from Master Table into H[dst]",
        "fields": "DST=target H-register (0-3), IMM=letter index (0-27)",
        "example": "0x01000001 → CLOAD H0 ← letter[1] (ب Ba)",
    },
    0x02: {
        "name": "CADD",
        "syntax": "CADD dst src1 src2 0",
        "desc": "H[dst] = H[src1] + H[src2] (18D component-wise)",
        "fields": "DST=result, SRC1=first operand, SRC2=second operand",
        "example": "0x02201000 → CADD H2 = H0 + H1",
    },
    0x03: {
        "name": "CSUB",
        "syntax": "CSUB dst src1 src2 0",
        "desc": "H[dst] = H[src1] − H[src2] (14D Delta vector)",
        "fields": "DST=result, SRC1=minuend, SRC2=subtrahend",
        "example": "0x03201000 → CSUB H2 = H0 − H1",
    },
    0x04: {
        "name": "VCHK",
        "syntax": "VCHK 0 src1 0 0",
        "desc": "Guard check on H[src1] → sets SR.GUARD_PASS flag",
        "fields": "SRC1=register to check (0-3)",
        "example": "0x04000000 → VCHK H0 → PASS/FAIL",
    },
    0x05: {
        "name": "VDIST",
        "syntax": "VDIST 0 src1 src2 0",
        "desc": "R0 = ‖H[src1] − H[src2]‖² (squared Euclidean distance, 14D)",
        "fields": "SRC1=first vector, SRC2=second vector, result in R0",
        "example": "0x05001000 → R0 = ‖H0 − H1‖²",
    },
    0x06: {
        "name": "VRHO",
        "syntax": "VRHO 0 src1 0 0",
        "desc": "R0 = ρ(H[src1]) = Θ̂ − U (turning residue)",
        "fields": "SRC1=register to decompose",
        "example": "0x06000000 → R0 = ρ(H0)",
    },
    0x07: {
        "name": "VNORM",
        "syntax": "VNORM 0 src1 0 0",
        "desc": "R0 = ‖H[src1]‖² (squared 14D codex norm)",
        "fields": "SRC1=register to measure",
        "example": "0x07010000 → R0 = ‖H1‖²",
    },
    0x08: {
        "name": "VDOT",
        "syntax": "VDOT 0 src1 src2 0",
        "desc": "R0 = ⟨H[src1], H[src2]⟩ (14D inner product)",
        "fields": "SRC1=first vector, SRC2=second vector",
        "example": "0x08001000 → R0 = ⟨H0, H1⟩",
    },
    0x09: {
        "name": "CHASH",
        "syntax": "CHASH dst src1 0 0",
        "desc": "H[dst] = SHA-256(H[src1]) truncated to 18 bytes",
        "fields": "DST=output, SRC1=input",
        "example": "0x09100000 → H1 = hash(H0)",
    },
    0x0B: {
        "name": "VMOV",
        "syntax": "VMOV dst src1 0 0",
        "desc": "H[dst] = copy of H[src1]",
        "fields": "DST=destination, SRC1=source",
        "example": "0x0B100000 → H1 = H0",
    },
    0x0E: {
        "name": "PRINT",
        "syntax": "PRINT dst 0 0 0",
        "desc": "Output H[dst] to trace log",
        "fields": "DST=register to print (0-3)",
        "example": "0x0E000000 → print H0",
    },
    0x0F: {
        "name": "HALT",
        "syntax": "HALT 0 0 0 0",
        "desc": "Stop execution",
        "fields": "No operands",
        "example": "0x0F000000 → halt",
    },
    0x10: {
        "name": "VPROJ_T",
        "syntax": "VPROJ_T dst src1 0 0",
        "desc": "H[dst] = Π_Θ(H[src1]) — keep only Θ̂, zero rest",
        "fields": "DST=output, SRC1=input",
        "example": "0x10100000 → H1 = Π_Θ(H0)",
    },
    0x11: {
        "name": "VPROJ_N",
        "syntax": "VPROJ_N dst src1 0 0",
        "desc": "H[dst] = Π_N(H[src1]) — keep only Na,Nb,Nd",
        "fields": "DST=output, SRC1=input",
        "example": "0x11100000 → H1 = Π_N(H0)",
    },
    0x12: {
        "name": "VPROJ_K",
        "syntax": "VPROJ_K dst src1 0 0",
        "desc": "H[dst] = Π_K(H[src1]) — keep only Kp..Kc",
        "fields": "DST=output, SRC1=input",
        "example": "0x12100000 → H1 = Π_K(H0)",
    },
    0x13: {
        "name": "VPROJ_Q",
        "syntax": "VPROJ_Q dst src1 0 0",
        "desc": "H[dst] = Π_Q(H[src1]) — keep only Qp..Qc",
        "fields": "DST=output, SRC1=input",
        "example": "0x13100000 → H1 = Π_Q(H0)",
    },
}

# Letter index → name for CLOAD display
_LETTER_NAMES: Dict[int, str] = {}
for _e in MASTER_TABLE.all_entries():
    _LETTER_NAMES[_e.index - 1] = f"{_e.char} ({_e.name})"


class BytecodeTab:
    """
    Tab: Bytecode Inspector

    Three modes:
      1. DECODE — type hex → see breakdown
      2. BUILD  — pick opcode + operands → get hex
      3. BATCH  — paste multiple hex words → decode all
    """

    def __init__(self, notebook: ttk.Notebook) -> None:
        self._tab = ttk.Frame(notebook)
        notebook.add(self._tab, text="  ⬡ Bytecode Inspector  ")

        self._hex_var = tk.StringVar(value="01000001")
        self._result_text: Optional[tk.Text] = None
        self._result_out: Optional[OutputWriter] = None
        self._batch_input: Optional[tk.Text] = None
        self._batch_output: Optional[tk.Text] = None
        self._batch_out: Optional[OutputWriter] = None

        # Builder variables
        self._build_op_var = tk.StringVar(value="CLOAD")
        self._build_dst_var = tk.StringVar(value="0")
        self._build_s1_var = tk.StringVar(value="0")
        self._build_s2_var = tk.StringVar(value="0")
        self._build_imm_var = tk.StringVar(value="1")
        self._build_hex_var = tk.StringVar(value="")
        self._build_asm_var = tk.StringVar(value="")

        self._build()
        self._decode_live()

    def _build(self) -> None:
        """Build the three-section layout."""
        notebook = ttk.Notebook(self._tab)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Decoder
        decode_tab = ttk.Frame(notebook)
        notebook.add(decode_tab, text="  🔍 Decode Hex  ")
        self._build_decoder(decode_tab)

        # Tab 2: Builder
        build_tab = ttk.Frame(notebook)
        notebook.add(build_tab, text="  🔧 Build Instruction  ")
        self._build_builder(build_tab)

        # Tab 3: Batch
        batch_tab = ttk.Frame(notebook)
        notebook.add(batch_tab, text="  📋 Batch Decode  ")
        self._build_batch(batch_tab)

        # Tab 4: Reference
        ref_tab = ttk.Frame(notebook)
        notebook.add(ref_tab, text="  📖 Opcode Reference  ")
        self._build_reference(ref_tab)

    # ══════════════════════════════════════════════════════════════
    #  SECTION 1 — LIVE HEX DECODER
    # ══════════════════════════════════════════════════════════════

    def _build_decoder(self, parent: ttk.Frame) -> None:
        """Build the hex decoder panel with real-time updates."""

        # Instructions
        info = ttk.Frame(parent)
        info.pack(fill=tk.X, padx=10, pady=(10, 5))
        ttk.Label(
            info,
            text="H-ISA Instruction Word Decoder",
            font=THEME.font_ui_bold,
        ).pack(anchor=tk.W)
        ttk.Label(
            info,
            text=(
                "Type a 32-bit hex value (8 hex digits) below.\n"
                "Format: [OPCODE:8 bits][DST:4][SRC1:4][SRC2:4][IMM:12]\n"
                "The decode updates in real-time as you type."
            ),
            foreground=THEME.dim_fg,
        ).pack(anchor=tk.W, pady=(2, 0))

        # Hex input with real-time binding
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(input_frame, text="Hex (32-bit):").pack(side=tk.LEFT)
        ttk.Label(input_frame, text="0x").pack(side=tk.LEFT)

        hex_entry = tk.Entry(
            input_frame,
            textvariable=self._hex_var,
            font=("Consolas", 18, "bold"),
            width=12,
            bg=THEME.text_bg,
            fg=THEME.number_fg,
            insertbackground=THEME.number_fg,
        )
        hex_entry.pack(side=tk.LEFT, padx=5)

        # Bind real-time decode on every keystroke
        self._hex_var.trace_add("write", lambda *_: self._decode_live())

        # Quick examples
        examples_frame = ttk.Frame(parent)
        examples_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        ttk.Label(examples_frame, text="Examples:").pack(side=tk.LEFT)

        quick_examples = [
            ("CLOAD ب", "01000001"),
            ("CADD H2=H0+H1", "02201000"),
            ("VCHK H0", "04000000"),
            ("VDIST", "05001000"),
            ("VRHO", "06000000"),
            ("HALT", "0F000000"),
        ]
        for label, hex_val in quick_examples:
            ttk.Button(
                examples_frame,
                text=label,
                command=lambda h=hex_val: self._set_hex(h),
            ).pack(side=tk.LEFT, padx=2)

        # Result display
        self._result_text, _ = make_text(parent, font=THEME.font_mono)
        self._result_out = OutputWriter(self._result_text)
        self._result_out.add_tags(
            {
                "header": {"foreground": THEME.hijaiyyah_fg, "font": (*THEME.font_mono, "bold")},
                "value": {"foreground": THEME.number_fg},
                "field": {"foreground": "#ffeaa7"},
                "dim": {"foreground": THEME.dim_fg},
                "pass": {"foreground": THEME.success},
                "error": {"foreground": THEME.error},
                "bit": {"foreground": "#fd79a8", "font": ("Consolas", 12, "bold")},
            }
        )

    def _set_hex(self, hex_val: str) -> None:
        """Set the hex input to a specific value."""
        self._hex_var.set(hex_val)

    def _decode_live(self) -> None:
        """Decode the current hex value and display results in real-time."""
        if self._result_out is None:
            return

        hex_str = self._hex_var.get().strip()
        self._result_out.clear()

        if not hex_str:
            self._result_out.writeln("Enter a hex value above (e.g., 01000001)", "dim")
            return

        # Validate hex
        try:
            if hex_str.startswith("0x") or hex_str.startswith("0X"):
                hex_str = hex_str[2:]
            raw = int(hex_str, 16)
        except ValueError:
            self._result_out.writeln(f"Invalid hex: '{hex_str}'", "error")
            self._result_out.writeln("Enter 1-8 hex digits (0-9, A-F)", "dim")
            return

        if raw > 0xFFFFFFFF:
            self._result_out.writeln("Value exceeds 32 bits (max: FFFFFFFF)", "error")
            return

        iw = InstructionWord(raw)

        # ── Header
        self._result_out.writeln("INSTRUCTION WORD DECODE", "header")
        self._result_out.writeln("=" * 55)
        self._result_out.writeln()

        # ── Raw value
        self._result_out.writeln(f"  Hex:    0x{raw:08X}", "value")
        self._result_out.writeln(f"  Binary: {raw:032b}", "bit")
        self._result_out.writeln(f"  Dec:    {raw}", "dim")
        self._result_out.writeln()

        # ── Bit field breakdown
        self._result_out.writeln("BIT FIELD BREAKDOWN", "header")
        self._result_out.writeln(
            "  ┌────────────┬──────┬──────┬──────┬──────────────┐",
            "dim",
        )
        self._result_out.writeln(
            "  │  OPCODE    │ DST  │ SRC1 │ SRC2 │     IMM      │",
            "dim",
        )
        self._result_out.writeln(
            "  │  bits 31-24│ 23-20│ 19-16│ 15-12│   bits 11-0  │",
            "dim",
        )
        self._result_out.writeln(
            "  ├────────────┼──────┼──────┼──────┼──────────────┤",
            "dim",
        )

        op_bits = f"{iw.opcode:08b}"
        dst_bits = f"{iw.dst:04b}"
        s1_bits = f"{iw.src1:04b}"
        s2_bits = f"{iw.src2:04b}"
        imm_bits = f"{iw.imm:012b}"

        self._result_out.writeln(
            f"  │ {op_bits} │ {dst_bits} │ {s1_bits} │ {s2_bits} │ {imm_bits} │",
            "bit",
        )
        self._result_out.writeln(
            f"  │ 0x{iw.opcode:02X}      │  {iw.dst}   │  {iw.src1}   │  {iw.src2}   │  {iw.imm:<10d} │",
            "value",
        )
        self._result_out.writeln(
            "  └────────────┴──────┴──────┴──────┴──────────────┘",
            "dim",
        )
        self._result_out.writeln()

        # ── Decoded fields
        self._result_out.writeln("DECODED FIELDS", "header")
        self._result_out.writeln(f"  Opcode:  0x{iw.opcode:02X} ({iw.opcode})", "field")
        self._result_out.writeln(f"  DST:     H{iw.dst} (register {iw.dst})", "field")
        self._result_out.writeln(f"  SRC1:    H{iw.src1} (register {iw.src1})", "field")
        self._result_out.writeln(f"  SRC2:    H{iw.src2} (register {iw.src2})", "field")
        self._result_out.writeln(f"  IMM:     {iw.imm} (0x{iw.imm:03X})", "field")
        self._result_out.writeln()

        # ── Instruction meaning
        self._result_out.writeln("INSTRUCTION MEANING", "header")
        disasm = iw.disassemble()
        self._result_out.writeln(f"  Assembly: {disasm}", "pass")

        # Detailed description from docs
        doc = OPCODE_DOCS.get(iw.opcode)
        if doc:
            self._result_out.writeln()
            self._result_out.writeln(f"  Name:     {doc['name']}", "value")
            self._result_out.writeln(f"  Syntax:   {doc['syntax']}", "dim")
            self._result_out.writeln(f"  Desc:     {doc['desc']}", "dim")
            self._result_out.writeln(f"  Fields:   {doc['fields']}", "dim")

            # Special: CLOAD shows letter name
            if iw.opcode == 0x01 and iw.imm in _LETTER_NAMES:
                letter_info = _LETTER_NAMES[iw.imm]
                self._result_out.writeln()
                self._result_out.writeln(
                    f"  Letter:   index {iw.imm} → {letter_info}",
                    "pass",
                )
        else:
            self._result_out.writeln("  (Unknown opcode — not in H-ISA spec)", "error")

    # ══════════════════════════════════════════════════════════════
    #  SECTION 2 — INSTRUCTION BUILDER
    # ══════════════════════════════════════════════════════════════

    def _build_builder(self, parent: ttk.Frame) -> None:
        """Build the instruction constructor panel."""

        info = ttk.Frame(parent)
        info.pack(fill=tk.X, padx=10, pady=(10, 5))
        ttk.Label(
            info,
            text="Instruction Builder — Construct H-ISA Words",
            font=THEME.font_ui_bold,
        ).pack(anchor=tk.W)
        ttk.Label(
            info,
            text=(
                "Select an opcode and set operands below.\n"
                "The hex instruction word is generated automatically."
            ),
            foreground=THEME.dim_fg,
        ).pack(anchor=tk.W, pady=(2, 0))

        # Opcode selector
        op_frame = ttk.Frame(parent)
        op_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(op_frame, text="Opcode:").pack(side=tk.LEFT)
        op_names = [doc["name"] for doc in OPCODE_DOCS.values()]
        op_combo = ttk.Combobox(
            op_frame,
            textvariable=self._build_op_var,
            values=op_names,
            width=12,
            state="readonly",
        )
        op_combo.pack(side=tk.LEFT, padx=5)
        op_combo.bind("<<ComboboxSelected>>", lambda _: self._update_builder())

        # Operand inputs
        operand_frame = ttk.Frame(parent)
        operand_frame.pack(fill=tk.X, padx=10, pady=5)

        for label, var, hint in [
            ("DST (0-3):", self._build_dst_var, "Target H-register"),
            ("SRC1 (0-3):", self._build_s1_var, "First source"),
            ("SRC2 (0-3):", self._build_s2_var, "Second source"),
            ("IMM (0-4095):", self._build_imm_var, "Immediate value"),
        ]:
            col = ttk.Frame(operand_frame)
            col.pack(side=tk.LEFT, padx=5)
            ttk.Label(col, text=label).pack(anchor=tk.W)
            entry = tk.Entry(
                col,
                textvariable=var,
                width=6,
                font=("Consolas", 12),
                bg=THEME.text_bg,
                fg=THEME.number_fg,
            )
            entry.pack()
            ttk.Label(col, text=hint, foreground=THEME.dim_fg).pack(anchor=tk.W)
            var.trace_add("write", lambda *_: self._update_builder())

        # Letter selector for CLOAD
        letter_frame = ttk.Frame(parent)
        letter_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(letter_frame, text="Quick letter (for CLOAD IMM):").pack(side=tk.LEFT)

        entries = MASTER_TABLE.all_entries()
        # `letter`, not `entry` — a tk.Entry is bound to that name above.
        # IMM is the 1-based letter index the ROM and HLOAD use, so the button
        # passes letter.index rather than its position in the list.
        for i, letter in enumerate(entries):
            if i >= 14:
                break
            ttk.Button(
                letter_frame,
                text=letter.char,
                width=2,
                command=lambda idx=letter.index: self._set_imm_letter(idx),
            ).pack(side=tk.LEFT, padx=1)

        letter_frame2 = ttk.Frame(parent)
        letter_frame2.pack(fill=tk.X, padx=10, pady=(0, 5))
        for i, letter in enumerate(entries):
            if i < 14:
                continue
            ttk.Button(
                letter_frame2,
                text=letter.char,
                width=2,
                command=lambda idx=letter.index: self._set_imm_letter(idx),
            ).pack(side=tk.LEFT, padx=1)

        # Result
        result_frame = ttk.Frame(parent)
        result_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(result_frame, text="Result:", font=THEME.font_ui_bold).pack(anchor=tk.W)

        hex_frame = ttk.Frame(result_frame)
        hex_frame.pack(fill=tk.X, pady=5)

        ttk.Label(hex_frame, text="Hex:").pack(side=tk.LEFT)
        hex_result = tk.Entry(
            hex_frame,
            textvariable=self._build_hex_var,
            font=("Consolas", 18, "bold"),
            width=12,
            bg=THEME.text_bg,
            fg=THEME.number_fg,
            state="readonly",
        )
        hex_result.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            hex_frame,
            text="📋 Copy Hex",
            command=lambda: self._copy_to_clipboard(self._build_hex_var.get()),
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            hex_frame,
            text="→ Send to Decoder",
            command=lambda: self._hex_var.set(self._build_hex_var.get().replace("0x", "")),
        ).pack(side=tk.LEFT, padx=5)

        asm_frame = ttk.Frame(result_frame)
        asm_frame.pack(fill=tk.X)
        ttk.Label(asm_frame, text="ASM:").pack(side=tk.LEFT)
        tk.Entry(
            asm_frame,
            textvariable=self._build_asm_var,
            font=("Consolas", 14),
            width=30,
            bg=THEME.text_bg,
            fg="#81ecec",
            state="readonly",
        ).pack(side=tk.LEFT, padx=5)

        self._update_builder()

    def _set_imm_letter(self, idx: int) -> None:
        """
        Set IMM to a 1-based letter index and switch the opcode to CLOAD.

        The buttons used to pass their position in the list, which is 0-based:
        pressing ب produced CLOAD #1 and loaded Alif, and pressing ا produced
        CLOAD #0, an address the ROM reports as invalid.
        """
        self._build_op_var.set("CLOAD")
        self._build_imm_var.set(str(idx))
        self._update_builder()

    def _update_builder(self) -> None:
        """Recompute the instruction word from builder inputs."""
        op_name = self._build_op_var.get()

        # Find opcode value
        op_val = 0
        for code, doc in OPCODE_DOCS.items():
            if doc["name"] == op_name:
                op_val = code
                break

        try:
            dst = int(self._build_dst_var.get()) & 0xF
        except ValueError:
            dst = 0
        try:
            s1 = int(self._build_s1_var.get()) & 0xF
        except ValueError:
            s1 = 0
        try:
            s2 = int(self._build_s2_var.get()) & 0xF
        except ValueError:
            s2 = 0
        try:
            imm = int(self._build_imm_var.get()) & 0xFFF
        except ValueError:
            imm = 0

        word = (op_val << 24) | (dst << 20) | (s1 << 16) | (s2 << 12) | imm
        self._build_hex_var.set(f"0x{word:08X}")

        # Generate assembly text
        asm = f"{op_name} {dst} {s1} {s2} {imm}"
        if op_name == "CLOAD" and imm in _LETTER_NAMES:
            asm += f"  ; {_LETTER_NAMES[imm]}"
        self._build_asm_var.set(asm)

    # ══════════════════════════════════════════════════════════════
    #  SECTION 3 — BATCH DECODE
    # ══════════════════════════════════════════════════════════════

    def _build_batch(self, parent: ttk.Frame) -> None:
        """Build the batch decode panel."""

        info = ttk.Frame(parent)
        info.pack(fill=tk.X, padx=10, pady=(10, 5))
        ttk.Label(
            info,
            text="Batch Decode — Paste Multiple Hex Words",
            font=THEME.font_ui_bold,
        ).pack(anchor=tk.W)
        ttk.Label(
            info,
            text="Paste one hex value per line (e.g., program dump from H-ISA machine).",
            foreground=THEME.dim_fg,
        ).pack(anchor=tk.W)

        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left: input
        left = ttk.Frame(paned)
        paned.add(left, weight=1)
        ttk.Label(left, text="Hex Input (one per line):").pack(anchor=tk.W)
        self._batch_input = tk.Text(
            left,
            font=THEME.font_mono,
            bg=THEME.text_bg,
            fg=THEME.number_fg,
            insertbackground=THEME.number_fg,
            height=15,
            width=15,
        )
        self._batch_input.pack(fill=tk.BOTH, expand=True)
        self._batch_input.insert(
            "1.0", "01000001\n01100001\n02201000\n04020000\n0E200000\n0F000000"
        )

        btn = ttk.Frame(left)
        btn.pack(fill=tk.X, pady=5)
        ttk.Button(btn, text="▶ Decode All", command=self._batch_decode).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn, text="Clear", command=self._batch_clear).pack(side=tk.LEFT, padx=2)

        # Right: output
        right = ttk.Frame(paned)
        paned.add(right, weight=2)
        ttk.Label(right, text="Decoded Output:").pack(anchor=tk.W)
        self._batch_output, _ = make_text(right, font=THEME.font_mono_sm)
        self._batch_out = OutputWriter(self._batch_output)
        self._batch_out.add_tags(
            {
                "addr": {"foreground": THEME.dim_fg},
                "hex": {"foreground": THEME.number_fg},
                "asm": {"foreground": "#81ecec"},
                "desc": {"foreground": THEME.fg},
                "pass": {"foreground": THEME.success},
                "error": {"foreground": THEME.error},
            }
        )

    def _batch_decode(self) -> None:
        """Decode all hex values from batch input."""
        if self._batch_input is None or self._batch_out is None:
            return

        text = self._batch_input.get("1.0", tk.END).strip()
        if not text:
            return

        self._batch_out.clear()
        self._batch_out.writeln("BATCH DECODE", "pass")
        self._batch_out.writeln(
            f"{'Addr':<6} {'Hex':<12} {'Assembly':<35} {'Description'}",
            "addr",
        )
        self._batch_out.writeln("-" * 80, "addr")

        for i, line in enumerate(text.split("\n")):
            line = line.strip()
            if not line:
                continue

            try:
                clean = line.replace("0x", "").replace("0X", "")
                raw = int(clean, 16)
                iw = InstructionWord(raw)
                disasm = iw.disassemble()

                doc = OPCODE_DOCS.get(iw.opcode)
                desc = doc["desc"] if doc else "Unknown"

                extra = ""
                if iw.opcode == 0x01 and iw.imm in _LETTER_NAMES:
                    extra = f" [{_LETTER_NAMES[iw.imm]}]"

                self._batch_out.writeln(
                    f"  {i:04d}  0x{raw:08X}  {disasm:<33s}  {desc}{extra}",
                    "asm",
                )
            except ValueError:
                self._batch_out.writeln(f"  {i:04d}  {line:<12s}  ERROR: invalid hex", "error")

        self._batch_out.writeln()
        self._batch_out.writeln("Decode complete.", "pass")

    def _batch_clear(self) -> None:
        if self._batch_input is not None:
            self._batch_input.delete("1.0", tk.END)
        if self._batch_out is not None:
            self._batch_out.clear()

    # ══════════════════════════════════════════════════════════════
    #  SECTION 4 — OPCODE REFERENCE
    # ══════════════════════════════════════════════════════════════

    def _build_reference(self, parent: ttk.Frame) -> None:
        """Build the opcode reference table."""

        ttk.Label(
            parent,
            text="H-ISA Opcode Reference — Complete Instruction Set",
            font=THEME.font_ui_bold,
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))

        ttk.Label(
            parent,
            text=(
                "Instruction word format: 32-bit fixed width\n"
                "[OPCODE: 8 bits | DST: 4 bits | SRC1: 4 bits | SRC2: 4 bits | IMM: 12 bits]"
            ),
            foreground=THEME.dim_fg,
        ).pack(anchor=tk.W, padx=10)

        ref_text, _ = make_text(parent, font=THEME.font_mono_sm, wrap=tk.NONE)
        ref_out = OutputWriter(ref_text)
        ref_out.add_tags(
            {
                "header": {"foreground": THEME.hijaiyyah_fg, "font": (*THEME.font_mono, "bold")},
                "value": {"foreground": THEME.number_fg},
                "dim": {"foreground": THEME.dim_fg},
            }
        )

        ref_out.writeln(
            f"{'Hex':<6} {'Name':<10} {'Syntax':<25} {'Description'}",
            "header",
        )
        ref_out.writeln("=" * 85, "dim")

        for code in sorted(OPCODE_DOCS.keys()):
            doc = OPCODE_DOCS[code]
            ref_out.writeln(
                f"0x{code:02X}   {doc['name']:<10} {doc['syntax']:<25} {doc['desc']}",
                "value",
            )
            ref_out.writeln(f"       Fields:  {doc['fields']}", "dim")
            ref_out.writeln(f"       Example: {doc['example']}", "dim")
            ref_out.writeln()

        ref_out.writeln("REGISTER LAYOUT", "header")
        ref_out.writeln("=" * 50, "dim")
        ref_out.writeln("  H0-H3:  4 codex registers (18 × uint8 each)", "value")
        ref_out.writeln("  R0-R17: 18 general purpose registers", "value")
        ref_out.writeln("  SR:     Status register", "value")
        ref_out.writeln("    .GUARD_PASS: set by VCHK", "dim")
        ref_out.writeln("    .ZERO:       set when result is zero vector", "dim")
        ref_out.writeln("    .OVERFLOW:   set when component > 255", "dim")
        ref_out.writeln()
        ref_out.writeln("LETTER INDEX TABLE (for CLOAD IMM field)", "header")
        ref_out.writeln("=" * 50, "dim")
        for idx, name in sorted(_LETTER_NAMES.items()):
            ref_out.writeln(f"  IMM={idx:<3d} → {name}", "value")

    # ── Utility ──────────────────────────────────────────────────

    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to system clipboard."""
        self._tab.clipboard_clear()
        self._tab.clipboard_append(text)
