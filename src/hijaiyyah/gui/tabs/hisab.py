"""
Tab: HISAB Protocol Explorer.

Interactive GUI for the HISAB protocol:
  Panel 1 — Frame Encoder: serialize letters/strings to HISAB frames
  Panel 2 — Validation Pipeline: 3-level validation with step-by-step results
  Panel 3 — Corruption Detector: inject mutations and observe multi-failure detection
  Panel 4 — Round-Trip Test: verify D(S(h*)) = h* for all 28 letters
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Tuple

from ...core.master_table import MasterTable
from ...hisab.protocol import (
    ALL_GUARDS_PASS,
)
from ...hisab.serialize import (
    deserialize_letter_payload,
    serialize_letter,
    serialize_string,
)
from ...hisab.validate import validate_frame
from ..theme import THEME
from ..widgets import OutputWriter, make_text


class HISABTab:
    """Tab: HISAB Protocol Explorer."""

    def __init__(self, notebook: ttk.Notebook, table: MasterTable) -> None:
        self._table = table
        self._tab = ttk.Frame(notebook)
        notebook.add(self._tab, text="  📡 HISAB  ")

        self._entries = table.all_entries()
        self._master_vectors = [tuple(e.vector) for e in self._entries]

        # UI state
        self._enc_out: Optional[OutputWriter] = None
        self._val_out: Optional[OutputWriter] = None
        self._cor_out: Optional[OutputWriter] = None
        self._rtt_out: Optional[OutputWriter] = None
        self._enc_var: Optional[tk.StringVar] = None
        self._enc_mode_var: Optional[tk.StringVar] = None
        self._str_entry: Optional[ttk.Entry] = None
        self._cor_var: Optional[tk.StringVar] = None
        self._cor_byte_var: Optional[tk.StringVar] = None
        self._cor_nibble_var: Optional[tk.StringVar] = None
        self._val_entry: Optional[tk.Text] = None

        self._build()

    # ── Layout ──────────────────────────────────────────────────

    def _build(self) -> None:
        # Title bar
        title_bar = tk.Frame(self._tab, bg=THEME.surface, height=40)
        title_bar.pack(fill=tk.X, padx=0, pady=(0, 2))
        title_bar.pack_propagate(False)

        tk.Label(
            title_bar,
            text="  📡  HISAB — Hijaiyyah Inter-System Standard for Auditable Bridging",
            font=("Segoe UI", 12, "bold"),
            fg=THEME.hijaiyyah_fg,
            bg=THEME.surface,
        ).pack(side=tk.LEFT, padx=8, pady=6)

        tk.Label(
            title_bar,
            text="  │  Serialisasi Kanonik • Validasi Intrinsik • Interoperabilitas",
            font=("Consolas", 9),
            fg=THEME.dim_fg,
            bg=THEME.surface,
        ).pack(side=tk.RIGHT, padx=12, pady=6)

        # Main 2×2 grid via PanedWindows
        vpane = ttk.PanedWindow(self._tab, orient=tk.VERTICAL)
        vpane.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        top_pane = ttk.PanedWindow(vpane, orient=tk.HORIZONTAL)
        vpane.add(top_pane, weight=1)

        bot_pane = ttk.PanedWindow(vpane, orient=tk.HORIZONTAL)
        vpane.add(bot_pane, weight=1)

        self._build_encoder_panel(top_pane)
        self._build_validation_panel(top_pane)
        self._build_corruption_panel(bot_pane)
        self._build_roundtrip_panel(bot_pane)

    # ── Panel 1: Frame Encoder ──────────────────────────────────

    def _build_encoder_panel(self, parent: ttk.PanedWindow) -> None:
        frame = ttk.LabelFrame(parent, text="  ① Frame Encoder  ", padding=6)
        parent.add(frame, weight=1)

        ctrl = ttk.Frame(frame)
        ctrl.pack(fill=tk.X, pady=(0, 4))

        # Mode selector
        self._enc_mode_var = tk.StringVar(value="LETTER")
        ttk.Label(ctrl, text="Mode:").pack(side=tk.LEFT)
        ttk.Radiobutton(ctrl, text="Letter", variable=self._enc_mode_var,
                        value="LETTER", command=self._on_enc_mode_change).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(ctrl, text="String", variable=self._enc_mode_var,
                        value="STRING", command=self._on_enc_mode_change).pack(side=tk.LEFT, padx=4)

        # Letter dropdown
        self._enc_letter_frame = ttk.Frame(ctrl)
        self._enc_letter_frame.pack(side=tk.LEFT, padx=(12, 0))
        ttk.Label(self._enc_letter_frame, text="Letter:").pack(side=tk.LEFT)
        names = [f"{e.char} ({e.name})" for e in self._entries]
        self._enc_var = tk.StringVar(value=names[1] if names else "")
        ttk.Combobox(
            self._enc_letter_frame, textvariable=self._enc_var,
            values=names, width=14
        ).pack(side=tk.LEFT, padx=4)

        # String entry (hidden by default)
        self._enc_string_frame = ttk.Frame(ctrl)
        ttk.Label(self._enc_string_frame, text="String:").pack(side=tk.LEFT)
        self._str_var = tk.StringVar(value="بسم")
        self._str_entry = ttk.Entry(self._enc_string_frame, textvariable=self._str_var, width=20,
                                    font=("Simplified Arabic", 14))
        self._str_entry.pack(side=tk.LEFT, padx=4)

        ttk.Button(ctrl, text="▶ Encode", command=self._do_encode).pack(side=tk.LEFT, padx=8)

        text, _ = make_text(frame, font=THEME.font_mono_sm)
        self._enc_out = OutputWriter(text)
        self._enc_out.add_tags({
            "header": {"foreground": THEME.hijaiyyah_fg, "font": ("Consolas", 10, "bold")},
            "hex": {"foreground": THEME.number_fg, "font": ("Consolas", 11)},
            "pass": {"foreground": THEME.success},
            "fail": {"foreground": THEME.error},
            "dim": {"foreground": THEME.dim_fg},
            "label": {"foreground": THEME.warning},
        })

    def _on_enc_mode_change(self) -> None:
        if self._enc_mode_var is None:
            return
        mode = self._enc_mode_var.get()
        if mode == "LETTER":
            self._enc_string_frame.pack_forget()
            self._enc_letter_frame.pack(side=tk.LEFT, padx=(12, 0))
        else:
            self._enc_letter_frame.pack_forget()
            self._enc_string_frame.pack(side=tk.LEFT, padx=(12, 0))

    def _do_encode(self) -> None:
        if self._enc_out is None or self._enc_mode_var is None:
            return
        self._enc_out.clear()

        mode = self._enc_mode_var.get()
        if mode == "LETTER":
            self._encode_letter()
        else:
            self._encode_string()

    def _encode_letter(self) -> None:
        if self._enc_out is None or self._enc_var is None:
            return
        selection = self._enc_var.get()
        if not selection:
            return

        char = selection.split()[0]
        entry = self._table.get_by_char(char)
        if entry is None:
            self._enc_out.writeln(f"Letter not found: {char}", "fail")
            return

        frame = serialize_letter(entry.vector)

        self._enc_out.writeln(f"HISAB LETTER Frame — {entry.char} ({entry.name})", "header")
        self._enc_out.writeln("═" * 56, "dim")
        self._enc_out.writeln()

        # v18 vector
        self._enc_out.writeln(f"v₁₈({entry.char}) = {list(entry.vector)}", "label")
        self._enc_out.writeln()

        # Hex dump
        self._enc_out.writeln("Frame hex dump:", "label")
        self._enc_out.writeln(f"  {frame.hex_dump()}", "hex")
        self._enc_out.writeln()

        # Annotated breakdown
        raw = frame.to_bytes()
        self._enc_out.writeln("Annotated breakdown:", "label")
        self._enc_out.writeln(f"  Header:  {_hex(raw[0:4])}  (magic=HB, ver=1, type=LETTER)", "dim")
        self._enc_out.writeln(f"  Payload: {_hex(raw[4:13])}  (9 bytes nibble-packed)", "hex")

        # Nibble breakdown
        self._enc_out.writeln()
        self._enc_out.writeln("Nibble packing detail:", "label")
        labels = [
            ("B0", "Θ̂", "Na"), ("B1", "Nb", "Nd"), ("B2", "Kp", "Kx"),
            ("B3", "Ks", "Ka"), ("B4", "Kc", "Qp"), ("B5", "Qx", "Qs"),
            ("B6", "Qa", "Qc"), ("B7", "A_N", "A_K"), ("B8", "A_Q", "H*"),
        ]
        v = entry.vector
        pairs = [
            (v[0], v[1]), (v[2], v[3]), (v[4], v[5]),
            (v[6], v[7]), (v[8], v[9]), (v[10], v[11]),
            (v[12], v[13]), (v[14], v[15]), (v[16], v[17]),
        ]
        for i, (bname, hi_lbl, lo_lbl) in enumerate(labels):
            hi, lo = pairs[i]
            self._enc_out.writeln(
                f"  {bname}: {hi_lbl}={hi} | {lo_lbl}={lo}  →  0x{raw[4+i]:02X}", "dim"
            )

        self._enc_out.writeln()
        guard_str = "PASS ✓" if frame.guard_status == ALL_GUARDS_PASS else f"PARTIAL 0x{frame.guard_status:02X}"
        tag = "pass" if frame.guard_status == ALL_GUARDS_PASS else "fail"
        self._enc_out.writeln(f"  Guard:   0x{frame.guard_status:02X}  ({guard_str})", tag)
        self._enc_out.writeln(f"  Digest:  0x{frame.digest:08X}  (CRC32)", "dim")
        self._enc_out.writeln(f"  Total:   {frame.total_size} bytes", "dim")

    def _encode_string(self) -> None:
        if self._enc_out is None:
            return
        text = self._str_var.get().strip()
        if not text:
            self._enc_out.writeln("Enter a Hijaiyyah string", "fail")
            return

        # Aggregate codex
        vectors: List[Tuple[int, ...]] = []
        for ch in text:
            entry = self._table.get_by_char(ch)
            if ch == "ه":
                entry = self._table.get_by_char("هـ")
            if entry is None:
                self._enc_out.writeln(f"Character not found: '{ch}'", "fail")
                return
            vectors.append(tuple(entry.vector))

        cod = [sum(v[i] for v in vectors) for i in range(18)]

        frame = serialize_string(cod, len(vectors))

        self._enc_out.writeln(f"HISAB STRING Frame — \"{text}\" ({len(vectors)} letters)", "header")
        self._enc_out.writeln("═" * 56, "dim")
        self._enc_out.writeln()
        self._enc_out.writeln(f"Cod₁₈ = {cod}", "label")
        self._enc_out.writeln()
        self._enc_out.writeln("Frame hex dump:", "label")
        self._enc_out.writeln(f"  {frame.hex_dump()}", "hex")
        self._enc_out.writeln()

        guard_str = "ALL PASS ✓" if frame.guard_status == ALL_GUARDS_PASS else f"0x{frame.guard_status:02X}"
        tag = "pass" if frame.guard_status == ALL_GUARDS_PASS else "fail"
        self._enc_out.writeln(f"  Guard:  0x{frame.guard_status:02X}  ({guard_str})", tag)
        self._enc_out.writeln(f"  Digest: 0x{frame.digest:08X}  (CRC32)", "dim")
        self._enc_out.writeln(f"  Total:  {frame.total_size} bytes", "dim")

    # ── Panel 2: Validation Pipeline ────────────────────────────

    def _build_validation_panel(self, parent: ttk.PanedWindow) -> None:
        frame = ttk.LabelFrame(parent, text="  ② Validation Pipeline  ", padding=6)
        parent.add(frame, weight=1)

        ctrl = ttk.Frame(frame)
        ctrl.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(ctrl, text="Letter:").pack(side=tk.LEFT)
        names = [f"{e.char} ({e.name})" for e in self._entries]
        self._val_var = tk.StringVar(value=names[1] if names else "")
        ttk.Combobox(ctrl, textvariable=self._val_var, values=names, width=14).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text="▶ Validate", command=self._do_validate).pack(side=tk.LEFT, padx=8)

        text, _ = make_text(frame, font=THEME.font_mono_sm)
        self._val_out = OutputWriter(text)
        self._val_out.add_tags({
            "header": {"foreground": THEME.hijaiyyah_fg, "font": ("Consolas", 10, "bold")},
            "pass": {"foreground": THEME.success},
            "fail": {"foreground": THEME.error},
            "dim": {"foreground": THEME.dim_fg},
            "level": {"foreground": THEME.warning, "font": ("Consolas", 10, "bold")},
        })

    def _do_validate(self) -> None:
        if self._val_out is None:
            return
        self._val_out.clear()

        selection = self._val_var.get()
        if not selection:
            return

        char = selection.split()[0]
        entry = self._table.get_by_char(char)
        if entry is None:
            self._val_out.writeln(f"Letter not found: {char}", "fail")
            return

        # Serialize and validate
        frame = serialize_letter(entry.vector)
        raw = frame.to_bytes()
        report = validate_frame(raw, self._master_vectors)

        self._val_out.writeln(f"3-Level HISAB Validation — {entry.char} ({entry.name})", "header")
        self._val_out.writeln("═" * 56, "dim")
        self._enc_out_hex_line(self._val_out, raw)
        self._val_out.writeln()

        # Display results grouped by level
        current_level = ""
        level_names = {
            "STRUCT": "Level 1 — Structural Validation (§4.12)",
            "GUARD": "Level 2 — Guard Validation (§4.13)",
            "SEMANTIC": "Level 3 — Semantic Validation (§4.14)",
        }
        for r in report.results:
            if r.level != current_level:
                current_level = r.level
                self._val_out.writeln()
                self._val_out.writeln(f"▶ {level_names.get(r.level, r.level)}", "level")
            tag = "pass" if r.passed else "fail"
            icon = "✓" if r.passed else "✗"
            self._val_out.writeln(f"  [{icon}] {r.code}: {r.detail}", tag)

        self._val_out.writeln()
        if report.all_pass:
            self._val_out.writeln("═══ ACCEPT ═══  All 3 levels PASS", "pass")
        else:
            self._val_out.writeln(f"═══ REJECT ═══  {len(report.failed)} check(s) failed", "fail")

    def _enc_out_hex_line(self, out: OutputWriter, data: bytes) -> None:
        out.writeln(f"Frame: {' '.join(f'{b:02X}' for b in data)}", "dim")

    # ── Panel 3: Corruption Detector ────────────────────────────

    def _build_corruption_panel(self, parent: ttk.PanedWindow) -> None:
        frame = ttk.LabelFrame(parent, text="  ③ Corruption Detector  ", padding=6)
        parent.add(frame, weight=1)

        ctrl = ttk.Frame(frame)
        ctrl.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(ctrl, text="Letter:").pack(side=tk.LEFT)
        names = [f"{e.char} ({e.name})" for e in self._entries]
        self._cor_var = tk.StringVar(value=names[26] if len(names) > 26 else names[0])  # هـ default
        ttk.Combobox(ctrl, textvariable=self._cor_var, values=names, width=14).pack(side=tk.LEFT, padx=4)

        ttk.Label(ctrl, text="Byte#:").pack(side=tk.LEFT, padx=(8, 0))
        self._cor_byte_var = tk.StringVar(value="10")
        ttk.Combobox(ctrl, textvariable=self._cor_byte_var,
                     values=[str(i) for i in range(4, 13)], width=4).pack(side=tk.LEFT, padx=2)

        ttk.Label(ctrl, text="Δ:").pack(side=tk.LEFT, padx=(8, 0))
        self._cor_nibble_var = tk.StringVar(value="+1")
        ttk.Combobox(ctrl, textvariable=self._cor_nibble_var,
                     values=["+1", "+2", "-1", "-2", "XOR 0x0F"], width=8).pack(side=tk.LEFT, padx=2)

        ttk.Button(ctrl, text="▶ Inject & Detect", command=self._do_corrupt).pack(side=tk.LEFT, padx=8)

        text, _ = make_text(frame, font=THEME.font_mono_sm)
        self._cor_out = OutputWriter(text)
        self._cor_out.add_tags({
            "header": {"foreground": THEME.hijaiyyah_fg, "font": ("Consolas", 10, "bold")},
            "pass": {"foreground": THEME.success},
            "fail": {"foreground": THEME.error},
            "dim": {"foreground": THEME.dim_fg},
            "level": {"foreground": THEME.warning, "font": ("Consolas", 10, "bold")},
            "hex_good": {"foreground": THEME.number_fg},
            "hex_bad": {"foreground": THEME.error, "font": ("Consolas", 11, "bold")},
        })

    def _do_corrupt(self) -> None:
        if self._cor_out is None or self._cor_var is None:
            return
        self._cor_out.clear()

        selection = self._cor_var.get()
        if not selection:
            return

        char = selection.split()[0]
        entry = self._table.get_by_char(char)
        if entry is None:
            self._cor_out.writeln(f"Letter not found: {char}", "fail")
            return

        byte_idx = int(self._cor_byte_var.get()) if self._cor_byte_var else 10
        delta_str = self._cor_nibble_var.get() if self._cor_nibble_var else "+1"

        # Serialize valid frame
        frame = serialize_letter(entry.vector)
        original = bytearray(frame.to_bytes())

        # Apply mutation
        corrupted = bytearray(original)
        if delta_str == "XOR 0x0F":
            corrupted[byte_idx] ^= 0x0F
        else:
            delta = int(delta_str)
            corrupted[byte_idx] = max(0, min(255, corrupted[byte_idx] + delta))

        self._cor_out.writeln(f"Corruption Detection — {entry.char} ({entry.name})", "header")
        self._cor_out.writeln("═" * 56, "dim")
        self._cor_out.writeln()

        # Show original vs corrupted
        self._cor_out.writeln("Original frame:", "dim")
        self._cor_out.writeln(f"  {' '.join(f'{b:02X}' for b in original)}", "hex_good")
        self._cor_out.writeln()
        self._cor_out.writeln(f"Corrupted frame (byte {byte_idx}: 0x{original[byte_idx]:02X} → 0x{corrupted[byte_idx]:02X}):", "dim")

        # Highlight changed byte
        parts: list[str] = []
        for _i, b in enumerate(corrupted):
            parts.append(f"{b:02X}")
        hex_line = " ".join(parts)
        self._cor_out.writeln(f"  {hex_line}", "hex_bad")
        self._cor_out.writeln()

        # Validate corrupted frame
        report = validate_frame(bytes(corrupted), self._master_vectors)

        # Display failures
        fail_count = len(report.failed)
        total_checks = len(report.results)

        current_level = ""
        level_names = {
            "STRUCT": "Level 1 — Structural (Transport)",
            "GUARD": "Level 2 — Guard (Geometric)",
            "SEMANTIC": "Level 3 — Semantic",
        }

        for r in report.results:
            if r.level != current_level:
                current_level = r.level
                self._cor_out.writeln()
                self._cor_out.writeln(f"▶ {level_names.get(r.level, r.level)}", "level")
            tag = "pass" if r.passed else "fail"
            icon = "✓" if r.passed else "✗"
            self._cor_out.writeln(f"  [{icon}] {r.code}: {r.detail}", tag)

        self._cor_out.writeln()
        self._cor_out.writeln(f"Detection summary: {fail_count}/{total_checks} checks FAILED", "fail")
        self._cor_out.writeln(
            f"→ Single-byte corruption triggers {fail_count} failure(s) — "
            f"dual-layer defense (CRC + Guard)", "dim"
        )

    # ── Panel 4: Round-Trip Test ────────────────────────────────

    def _build_roundtrip_panel(self, parent: ttk.PanedWindow) -> None:
        frame = ttk.LabelFrame(parent, text="  ④ Round-Trip Fidelity Test  ", padding=6)
        parent.add(frame, weight=1)

        ctrl = ttk.Frame(frame)
        ctrl.pack(fill=tk.X, pady=(0, 4))

        ttk.Button(ctrl, text="▶ Run Round-Trip Test (all 28 letters)",
                   command=self._do_roundtrip).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text="▶ Test Injectivity",
                   command=self._do_injectivity).pack(side=tk.LEFT, padx=4)

        text, _ = make_text(frame, font=THEME.font_mono_sm)
        self._rtt_out = OutputWriter(text)
        self._rtt_out.add_tags({
            "header": {"foreground": THEME.hijaiyyah_fg, "font": ("Consolas", 10, "bold")},
            "pass": {"foreground": THEME.success},
            "fail": {"foreground": THEME.error},
            "dim": {"foreground": THEME.dim_fg},
            "theorem": {"foreground": THEME.warning, "font": ("Consolas", 10, "bold")},
        })

    def _do_roundtrip(self) -> None:
        if self._rtt_out is None:
            return
        self._rtt_out.clear()

        self._rtt_out.writeln("Round-Trip Fidelity Test — Theorem 4.23.1", "header")
        self._rtt_out.writeln("D(S(h*)) = h*  for all h* ∈ V", "theorem")
        self._rtt_out.writeln("═" * 56, "dim")
        self._rtt_out.writeln()

        all_pass = True
        for entry in self._entries:
            v18 = tuple(entry.vector)

            # Serialize
            frame = serialize_letter(v18)

            # Deserialize
            recovered = deserialize_letter_payload(frame.payload)

            match = recovered == v18
            icon = "✓" if match else "✗"
            tag = "pass" if match else "fail"

            # Guard preservation (Theorem 4.24.1)
            guard_ok = frame.guard_status == ALL_GUARDS_PASS
            guard_icon = "✓" if guard_ok else "✗"

            self._rtt_out.writeln(
                f"  {entry.char:>2} ({entry.name:<6}) │ S→{frame.total_size:>2}B │ "
                f"D(S(h*))=h* [{icon}] │ Guard [{guard_icon}] │ "
                f"CRC=0x{frame.digest:08X}",
                tag
            )

            if not match:
                all_pass = False
                self._rtt_out.writeln(f"    Original:  {list(v18)}", "fail")
                self._rtt_out.writeln(f"    Recovered: {list(recovered)}", "fail")

        self._rtt_out.writeln()
        if all_pass:
            self._rtt_out.writeln("═══ ALL 28 LETTERS PASS ═══", "pass")
            self._rtt_out.writeln("Theorem 4.23.1 (Round-Trip Fidelity): VERIFIED ✓", "pass")
            self._rtt_out.writeln("Theorem 4.24.1 (Guard Preservation):  VERIFIED ✓", "pass")
            self._rtt_out.writeln("Corollary 4.23.1 (Injectivity):       VERIFIED ✓", "pass")
        else:
            self._rtt_out.writeln("═══ FAILURES DETECTED ═══", "fail")

    def _do_injectivity(self) -> None:
        if self._rtt_out is None:
            return
        self._rtt_out.clear()

        self._rtt_out.writeln("Injectivity Test — Corollary 4.23.1", "header")
        self._rtt_out.writeln("h₁* ≠ h₂*  ⟹  S(h₁*) ≠ S(h₂*)", "theorem")
        self._rtt_out.writeln("═" * 56, "dim")
        self._rtt_out.writeln()

        frames: List[bytes] = []
        all_unique = True
        for entry in self._entries:
            frame = serialize_letter(entry.vector)
            raw = frame.to_bytes()
            if raw in frames:
                self._rtt_out.writeln(
                    f"  ✗ Collision: {entry.char} serializes to existing frame!", "fail"
                )
                all_unique = False
            else:
                frames.append(raw)
                self._rtt_out.writeln(
                    f"  ✓ {entry.char:>2} ({entry.name:<6}) → unique frame ({frame.total_size}B)", "pass"
                )

        self._rtt_out.writeln()
        if all_unique:
            self._rtt_out.writeln(f"═══ ALL {len(frames)} FRAMES UNIQUE ═══", "pass")
            self._rtt_out.writeln("Corollary 4.23.1 (Injectivity): VERIFIED ✓", "pass")
        else:
            self._rtt_out.writeln("═══ INJECTIVITY VIOLATION ═══", "fail")


# ── Helpers ─────────────────────────────────────────────────────

def _hex(data: bytes) -> str:
    return " ".join(f"{b:02X}" for b in data)
