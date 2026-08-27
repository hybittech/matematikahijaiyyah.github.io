"""
Tab: String Aggregametric — Additive Codex Computation Engine
==============================================================
Professional string analysis with:
  - Real-time codex computation (Cod₁₈)
  - Full 18-component breakdown with named slots
  - Layer aggregation (ΣΘ̂, ΣU, Σρ) with identity verification
  - Cumulative trajectory visualization (S₀ → Sₙ)
  - Per-letter decomposition table
  - Centroid (mean v₁₈)
  - String comparison mode
  - Preset strings for quick analysis
  - Anagram verification
  - Energy aggregation computation
"""

from __future__ import annotations

import math
import time
import tkinter as tk
from tkinter import ttk
from typing import Any, List, Optional, Tuple

from ...algebra import aggregametric as integ
from ...algebra import exometric as exo
from ...core.guards import compute_U
from ...core.master_table import MasterTable
from ..theme import THEME
from ..widgets import OutputWriter, make_text

# ── Preset strings for quick analysis ────────────────────────────

PRESETS: List[Tuple[str, str]] = [
    ("بسم", "Bismillah prefix"),
    ("الله", "Allah"),
    ("بسم الله", "Bismillah"),
    ("بسم الله الرحمن الرحيم", "Full Basmala"),
    ("محمد", "Muhammad"),
    ("علم", "Ilm (knowledge)"),
    ("كتب", "Kataba (wrote)"),
    ("نور", "Nur (light)"),
    ("حق", "Haqq (truth)"),
    ("سلم", "Salama (peace)"),
]


class StringIntegralTab:
    """
    Tab: String Aggregametric — Additive Codex Computation Engine

    Layout:
    ┌──────────────────────────────────────────────────────┐
    │  Input: [text field] [▶ Compute] [presets...]        │
    │  Compare: [text field 2] [▶ Compare]                 │
    ├──────────────────────────────────────────────────────┤
    │                                                      │
    │  ① Cod₁₈ Vector (18 named components)               │
    │  ② Layer Aggregation (Θ̂, U, ρ with identity check)  │
    │  ③ Per-Letter Decomposition Table                    │
    │  ④ Cumulative Trajectory (S₀ → Sₙ)                 │
    │  ⑤ Centroid (mean v₁₈)                              │
    │  ⑥ Energy Aggregation                                │
    │  ⑦ Comparison (if two strings)                       │
    │                                                      │
    └──────────────────────────────────────────────────────┘
    """

    def __init__(
        self,
        notebook: ttk.Notebook,
        table: MasterTable,
        evaluator: Any,
    ) -> None:
        self._table = table
        self._tab = ttk.Frame(notebook)
        notebook.add(self._tab, text="  Σ String Aggregametric  ")

        self._text: Optional[tk.Text] = None
        self._out: Optional[OutputWriter] = None
        self._input1 = tk.StringVar(value="بسم")
        self._input2 = tk.StringVar(value="الله")
        self._status_var = tk.StringVar(value="Ready")

        self._build()

    def _build(self) -> None:
        # ── Input Section ────────────────────────────────────────
        input_frame = ttk.Frame(self._tab)
        input_frame.pack(fill=tk.X, padx=8, pady=5)

        # Primary input
        row1 = ttk.Frame(input_frame)
        row1.pack(fill=tk.X, pady=2)

        ttk.Label(row1, text="String 1:", font=THEME.font_ui_bold).pack(side=tk.LEFT)
        entry1 = tk.Entry(
            row1,
            textvariable=self._input1,
            font=("Simplified Arabic", 18),
            width=25,
            bg=THEME.text_bg,
            fg=THEME.hijaiyyah_fg,
            insertbackground=THEME.hijaiyyah_fg,
        )
        entry1.pack(side=tk.LEFT, padx=5)

        ttk.Button(row1, text="▶ Analyze", command=self._compute).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="⟳ Clear", command=self._clear).pack(side=tk.LEFT, padx=2)

        # Status
        ttk.Label(row1, textvariable=self._status_var, foreground=THEME.dim_fg).pack(
            side=tk.RIGHT, padx=5
        )

        # Compare input
        row2 = ttk.Frame(input_frame)
        row2.pack(fill=tk.X, pady=2)

        ttk.Label(row2, text="String 2:", foreground=THEME.dim_fg).pack(side=tk.LEFT)
        entry2 = tk.Entry(
            row2,
            textvariable=self._input2,
            font=("Simplified Arabic", 16),
            width=25,
            bg=THEME.text_bg,
            fg="#fdcb6e",
            insertbackground="#fdcb6e",
        )
        entry2.pack(side=tk.LEFT, padx=5)

        ttk.Button(row2, text="⇆ Compare Both", command=self._compare).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text="📝 Anagram Check", command=self._anagram_check).pack(
            side=tk.LEFT, padx=2
        )

        # Preset buttons
        preset_frame = ttk.Frame(input_frame)
        preset_frame.pack(fill=tk.X, pady=2)
        ttk.Label(preset_frame, text="Presets:", foreground=THEME.dim_fg).pack(side=tk.LEFT)

        for text, _desc in PRESETS:
            ttk.Button(
                preset_frame,
                text=text,
                command=lambda t=text: self._set_and_compute(t),
            ).pack(side=tk.LEFT, padx=1)

        # ── Output Section ───────────────────────────────────────
        self._text, _ = make_text(self._tab, font=("Consolas", 11), wrap=tk.NONE)
        self._out = OutputWriter(self._text)
        self._out.add_tags(
            {
                "title": {"foreground": THEME.hijaiyyah_fg, "font": ("Consolas", 14, "bold")},
                "section": {"foreground": THEME.hijaiyyah_fg, "font": ("Consolas", 11, "bold")},
                "value": {"foreground": THEME.number_fg},
                "pass": {"foreground": THEME.success},
                "fail": {"foreground": THEME.error},
                "dim": {"foreground": THEME.dim_fg},
                "warn": {"foreground": THEME.warning},
                "field": {"foreground": "#ffeaa7"},
                "formula": {"foreground": "#81ecec"},
                "letter": {"foreground": THEME.hijaiyyah_fg},
                "compare": {"foreground": "#fdcb6e"},
            }
        )

        self._show_welcome()

    # ── Welcome ──────────────────────────────────────────────────

    def _show_welcome(self) -> None:
        if self._out is None:
            return
        self._out.clear()
        self._out.writeln("STRING AGGREGAMETRIC ENGINE — Σₘ h⃗", "title")
        self._out.writeln("═" * 60)
        self._out.writeln()
        self._out.writeln("Compute the additive codex aggregation for any Hijaiyyah string.", "dim")
        self._out.writeln()
        self._out.writeln("  Cod₁₈(w) = Σᵢ v₁₈(xᵢ)   (Definition §2.3.1)", "formula")
        self._out.writeln("  Σ_{uv} = Σ_u + Σ_v        (Theorem §2.3.2 — Additivity)", "formula")
        self._out.writeln("  Σ_w Θ̂ = Σ_w U + Σ_w ρ    (Turning budget conservation)", "formula")
        self._out.writeln()
        self._out.writeln("Features:", "dim")
        self._out.writeln("  ① Full 18D codex vector with named components", "dim")
        self._out.writeln("  ② Layer aggregation with identity verification", "dim")
        self._out.writeln("  ③ Per-letter decomposition table", "dim")
        self._out.writeln("  ④ Cumulative trajectory S₀ → Sₙ", "dim")
        self._out.writeln("  ⑤ Centroid (mean letter profile)", "dim")
        self._out.writeln("  ⑥ Energy aggregation Σ Φ(xᵢ)", "dim")
        self._out.writeln("  ⑦ Two-string comparison", "dim")
        self._out.writeln("  ⑧ Anagram invariance check", "dim")
        self._out.writeln()
        self._out.writeln("Enter a string above and press ▶ Analyze.", "dim")

    # ── Actions ──────────────────────────────────────────────────

    def _set_and_compute(self, text: str) -> None:
        self._input1.set(text)
        self._compute()

    def _clear(self) -> None:
        if self._out:
            self._out.clear()
            self._show_welcome()
        self._status_var.set("Ready")

    def _compute(self) -> None:
        """Compute full string integral analysis."""
        text = self._input1.get().strip()
        if not text:
            self._status_var.set("Enter a string")
            return

        if self._out is None:
            return

        self._out.clear()
        start_time = time.perf_counter()

        try:
            self._render_analysis(text)
            elapsed = (time.perf_counter() - start_time) * 1000
            self._status_var.set(f"Done ({elapsed:.0f}ms)")
        except Exception as e:
            self._out.writeln(f"ERROR: {e}", "fail")
            self._status_var.set("Error")

    def _compare(self) -> None:
        """Compare two strings side by side."""
        text1 = self._input1.get().strip()
        text2 = self._input2.get().strip()
        if not text1 or not text2:
            self._status_var.set("Enter both strings")
            return

        if self._out is None:
            return

        self._out.clear()

        try:
            self._render_analysis(text1)
            self._out.writeln()
            self._out.writeln("═" * 60)
            self._out.writeln()
            self._render_analysis(text2, label="STRING 2")
            self._out.writeln()
            self._render_comparison(text1, text2)
            self._status_var.set("Comparison complete")
        except Exception as e:
            self._out.writeln(f"ERROR: {e}", "fail")

    def _anagram_check(self) -> None:
        """Check if two strings are anagrams (same codex)."""
        text1 = self._input1.get().strip()
        text2 = self._input2.get().strip()
        if not text1 or not text2:
            self._status_var.set("Enter both strings")
            return

        if self._out is None:
            return

        self._out.clear()
        cod1 = integ.string_integral(text1)
        cod2 = integ.string_integral(text2)

        self._out.writeln("ANAGRAM INVARIANCE CHECK — Theorem 25.3.1", "title")
        self._out.writeln("═" * 60)
        self._out.writeln()
        self._out.writeln(
            f"  ∫_{'{x₁⋯xₙ}'} = ∫_{'{x_σ(1)⋯x_σ(n)}'}  for any permutation σ", "formula"
        )
        self._out.writeln()

        v1 = cod1["cod18"]
        v2 = cod2["cod18"]
        match = v1 == v2

        self._out.writeln(f"  String 1: {text1}", "value")
        self._out.writeln(f"  Cod₁₈:   ({', '.join(str(x) for x in v1)})", "dim")
        self._out.writeln()
        self._out.writeln(f"  String 2: {text2}", "compare")
        self._out.writeln(f"  Cod₁₈:   ({', '.join(str(x) for x in v2)})", "dim")
        self._out.writeln()

        if match:
            self._out.writeln("  Result: ANAGRAM ✓ — identical codex vectors", "pass")
            self._out.writeln("  These strings contain the same multiset of letters.", "dim")
        else:
            self._out.writeln("  Result: NOT ANAGRAM ✗ — different codex vectors", "fail")
            diff = [v1[i] - v2[i] for i in range(18)]
            nonzero = [(i, diff[i]) for i in range(18) if diff[i] != 0]
            self._out.writeln()
            self._out.writeln("  Differing components:", "field")
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
            for idx, delta in nonzero:
                name = slot_names[idx] if idx < len(slot_names) else f"[{idx}]"
                self._out.writeln(f"    {name}: {v1[idx]} vs {v2[idx]} (Δ = {delta:+d})", "warn")

    # ── Core rendering ───────────────────────────────────────────

    def _render_analysis(self, text: str, label: str = "STRING ANALYSIS") -> None:
        """Render complete analysis for a single string."""
        w = self._out
        if w is None:
            return

        # Compute
        cod = integ.string_integral(text)
        v = cod["cod18"]
        n = cod["length"]
        layers = integ.layer_integrals(text)
        cent = integ.centroid(text)
        traj = integ.cumulative(text)

        U_total = layers["U"]
        rho_total = layers["rho"]

        # ── Header
        w.writeln(f"{label}", "title")
        w.writeln("═" * 60)
        w.writeln()
        w.writeln(f"  Input:  {text}", "letter")
        w.writeln(f"  Length: {n} Hijaiyyah letter{'s' if n != 1 else ''}", "dim")
        w.writeln()

        # ── Section 1: Cod₁₈ Vector
        w.writeln("① COD₁₈ VECTOR — 18-Dimensional String Integral", "section")
        w.writeln("─" * 60, "dim")
        w.writeln()
        w.writeln("  Cod₁₈(w) = Σᵢ v₁₈(xᵢ)  for each Hijaiyyah letter xᵢ in w", "formula")
        w.writeln()

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
        slot_groups = [
            ("Inḥinā'", [0]),
            ("Nuqṭah", [1, 2, 3]),
            ("Khaṭṭ", [4, 5, 6, 7, 8]),
            ("Qaws", [9, 10, 11, 12, 13]),
            ("Checksum", [14, 15, 16]),
            ("Marker", [17]),
        ]

        for group_name, indices in slot_groups:
            parts = []
            for idx in indices:
                name = slot_names[idx]
                val = v[idx]
                if val != 0:
                    parts.append(f"{name}={val}")
                else:
                    parts.append(f"{name}=·")
            w.writeln(f"  {group_name:<10s} {' '.join(parts)}", "value")

        w.writeln()
        full_vec = "(" + ", ".join(str(x) for x in v) + ")"
        w.writeln(f"  Full: {full_vec}", "dim")
        w.writeln()

        # ── Section 2: Layer Integrals
        w.writeln("② LAYER AGGREGATION — Turning Budget Conservation", "section")
        w.writeln("─" * 60, "dim")
        w.writeln()
        w.writeln(f"  Σ Θ̂ = {layers['theta']:>4d}  ({layers['theta'] * 90}°)", "value")
        w.writeln(f"  Σ U  = {U_total:>4d}  (non-primary turning budget)", "value")
        w.writeln(f"  Σ ρ  = {rho_total:>4d}  (primary turning residue)", "value")
        w.writeln()

        identity_ok = layers["theta"] == U_total + rho_total
        w.writeln("  Identity: ΣΘ̂ = ΣU + Σρ", "formula")
        w.writeln(
            f"           {layers['theta']} = {U_total} + {rho_total}  "
            f"{'✓ VERIFIED' if identity_ok else '✗ VIOLATION'}",
            "pass" if identity_ok else "fail",
        )
        w.writeln()

        # Ratios
        if layers["theta"] > 0:
            r_u = U_total / layers["theta"]
            r_rho = rho_total / layers["theta"]
            w.writeln("  Turning profile:", "field")
            w.writeln(f"    r_U   = {r_u:.4f}  ({r_u * 100:.1f}% non-primary)", "dim")
            w.writeln(f"    r_ρ   = {r_rho:.4f}  ({r_rho * 100:.1f}% primary)", "dim")

            # Visual bar
            bar_len = 40
            u_bar = int(r_u * bar_len)
            rho_bar = bar_len - u_bar
            w.writeln(f"    [{'█' * u_bar}{'░' * rho_bar}]", "value")
            w.writeln(f"     {'U':>{u_bar + 1}}{'ρ':>{rho_bar}}", "dim")
        w.writeln()

        # ── Section 3: Per-Letter Decomposition
        w.writeln("③ PER-LETTER DECOMPOSITION", "section")
        w.writeln("─" * 60, "dim")
        w.writeln()
        w.writeln(
            f"  {'Ch':<4} {'Name':<8} {'Θ̂':<4} {'Θ°':<5} "
            f"{'N(a,b,d)':<12} {'K(p,x,s,a,c)':<16} {'Q(p,x,s,a,c)':<16} {'U':<4} {'ρ':<4}",
            "field",
        )
        w.writeln("  " + "─" * 72, "dim")

        for ch in text:
            entry = self._table.get_by_char(ch)
            if entry is None:
                if ch.strip():
                    w.writeln(f"  {ch:<4} (not Hijaiyyah — skipped)", "dim")
                continue

            ev = list(entry.vector)
            U_letter = compute_U(ev)
            rho_letter = ev[0] - U_letter

            n_str = f"({ev[1]},{ev[2]},{ev[3]})"
            k_str = f"({ev[4]},{ev[5]},{ev[6]},{ev[7]},{ev[8]})"
            q_str = f"({ev[9]},{ev[10]},{ev[11]},{ev[12]},{ev[13]})"

            w.writeln(
                f"  {ch:<4} {entry.name:<8} {ev[0]:<4} {ev[0] * 90:<5} "
                f"{n_str:<12} {k_str:<16} {q_str:<16} {U_letter:<4} {rho_letter:<4}",
                "value",
            )

        w.writeln()

        # ── Section 4: Cumulative Trajectory
        if n > 0:
            w.writeln("④ CUMULATIVE TRAJECTORY — S₀ → Sₙ", "section")
            w.writeln("─" * 60, "dim")
            w.writeln()
            w.writeln("  Sₖ = Σᵢ₌₁ᵏ v₁₈(xᵢ)  (Definition 27.2.1)", "formula")
            w.writeln("  Each Sₖ is monotonically non-decreasing (Lemma 27.2.1)", "formula")
            w.writeln()
            w.writeln(
                f"  {'k':<4} {'Letter':<6} {'∫Θ̂':<6} {'∫AN':<6} {'∫AK':<6} {'∫AQ':<6} {'∫U':<6} {'∫ρ':<6}",
                "field",
            )
            w.writeln("  " + "─" * 44, "dim")

            hijaiyyah_chars = []
            for ch in text:
                if self._table.get_by_char(ch) is not None:
                    hijaiyyah_chars.append(ch)

            for k, sk in enumerate(traj):
                letter_label = (
                    hijaiyyah_chars[k - 1] if k > 0 and k <= len(hijaiyyah_chars) else "—"
                )
                U_k = sk[10] + sk[11] + sk[12] + 4 * sk[13]
                rho_k = sk[0] - U_k

                w.writeln(
                    f"  S{k:<3} {letter_label:<6} {sk[0]:<6} {sk[14]:<6} {sk[15]:<6} {sk[16]:<6} {U_k:<6} {rho_k:<6}",
                    "value" if k > 0 else "dim",
                )

            w.writeln()

            # Mean value theorem check
            if n > 0:
                mean_theta = layers["theta"] / n
                min_theta = integ.min_component_theta(text)
                max_theta = integ.max_component_theta(text)
                mvt_ok = min_theta <= mean_theta <= max_theta

                w.writeln("  Mean Value Theorem (Theorem 26.1.1):", "field")
                w.writeln(
                    "    min(Θ̂ᵢ) ≤ (1/n)∫Θ̂ ≤ max(Θ̂ᵢ)",
                    "formula",
                )
                w.writeln(
                    f"    {min_theta} ≤ {mean_theta:.2f} ≤ {max_theta}  {'✓' if mvt_ok else '✗'}",
                    "pass" if mvt_ok else "fail",
                )
                w.writeln()

        # ── Section 5: Centroid
        if n > 0:
            w.writeln("⑤ CENTROID — Mean Letter Profile", "section")
            w.writeln("─" * 60, "dim")
            w.writeln()
            w.writeln(f"  v̄(w) = (1/{n}) Σ v₁₈(xᵢ)  (Definition 27.1.1)", "formula")
            w.writeln()

            w.writeln(f"  {'Component':<12} {'Sum':<8} {'Mean':<10}", "field")
            w.writeln("  " + "─" * 30, "dim")

            for idx in range(18):
                name = slot_names[idx]
                total = v[idx]
                mean = cent[idx]
                if total > 0 or mean > 0:
                    w.writeln(f"  {name:<12} {total:<8} {mean:<10.4f}", "value")

            w.writeln()
            w.writeln(f"  Mean Θ̂ = {cent[0]:.4f} quadrants ≈ {cent[0] * 90:.1f}°", "value")
            w.writeln()

        # ── Section 6: Energy
        w.writeln("⑥ ENERGY AGGREGATION — Σ Φ(xᵢ)", "section")
        w.writeln("─" * 60, "dim")
        w.writeln()

        total_energy = 0
        energy_parts: List[Tuple[str, int]] = []

        for ch in text:
            entry = self._table.get_by_char(ch)
            if entry is None:
                continue
            E = exo.build(entry)
            phi_val = exo.phi(E)
            total_energy += phi_val
            energy_parts.append((ch, phi_val))

        w.writeln(f"  ∫_w Φ = Σ Φ(xᵢ) = {total_energy}  (Definition 27.3.1)", "value")
        w.writeln()

        if energy_parts:
            w.writeln("  Breakdown:", "field")
            for ch, phi in energy_parts:
                entry = self._table.get_by_char(ch)
                name = entry.name if entry else "?"
                bar_len = min(phi // 3, 30)
                w.writeln(f"    {ch} ({name:<6s}) Φ={phi:>4d}  {'█' * bar_len}", "value")

        w.writeln()

        if n > 0:
            lower_bound = 2 * n
            w.writeln(f"  Lower bound: ∫Φ ≥ 2n = {lower_bound}  (Lemma 27.3.1)", "formula")
            bound_ok = total_energy >= lower_bound
            w.writeln(
                f"  Check: {total_energy} ≥ {lower_bound}  {'✓' if bound_ok else '✗'}",
                "pass" if bound_ok else "fail",
            )
            w.writeln()

    def _render_comparison(self, text1: str, text2: str) -> None:
        """Render comparison between two strings."""
        w = self._out
        if w is None:
            return

        cod1 = integ.string_integral(text1)
        cod2 = integ.string_integral(text2)
        v1 = cod1["cod18"]
        v2 = cod2["cod18"]

        l1 = integ.layer_integrals(text1)
        l2 = integ.layer_integrals(text2)

        w.writeln("⑦ STRING COMPARISON", "title")
        w.writeln("═" * 60)
        w.writeln()

        # Side-by-side metrics
        w.writeln(
            f"  {'Metric':<20} {'String 1':<15} {'String 2':<15} {'Δ':<10}",
            "field",
        )
        w.writeln("  " + "─" * 55, "dim")

        metrics = [
            ("∫ Θ̂ (turning)", l1["theta"], l2["theta"]),
            ("∫ U (non-primary)", l1["U"], l2["U"]),
            ("∫ ρ (primary)", l1["rho"], l2["rho"]),
            ("Length (letters)", cod1["length"], cod2["length"]),
            ("∫ AN (total dots)", v1[14], v2[14]),
            ("∫ AK (total lines)", v1[15], v2[15]),
            ("∫ AQ (total curves)", v1[16], v2[16]),
        ]

        for name, val1, val2 in metrics:
            delta = val1 - val2
            delta_str = f"{delta:+d}" if delta != 0 else "="
            tag = "value" if delta == 0 else "warn"
            w.writeln(f"  {name:<20} {val1:<15} {val2:<15} {delta_str:<10}", tag)

        w.writeln()

        # Same turning?
        if l1["theta"] == l2["theta"]:
            w.writeln(
                f"  ✦ Same total turning ({l1['theta']} quadrants = {l1['theta'] * 90}°)",
                "pass",
            )
            if l1["U"] != l2["U"]:
                w.writeln(
                    f"    But different profiles: U₁={l1['U']} vs U₂={l2['U']}",
                    "warn",
                )
        else:
            w.writeln(
                f"  Different total turning: {l1['theta']} vs {l2['theta']}",
                "compare",
            )

        w.writeln()

        # Vector difference
        diff = [v1[i] - v2[i] for i in range(18)]
        d2_sq = sum(d * d for d in diff[:14])

        w.writeln("  Codex distance:", "field")
        w.writeln(f"    ‖Δ‖² = {d2_sq}", "value")
        w.writeln(f"    ‖Δ‖  = {math.sqrt(d2_sq):.6f}", "value")

        nonzero_dims = sum(1 for d in diff if d != 0)
        w.writeln(f"    Differing dimensions: {nonzero_dims}/18", "dim")
        w.writeln()

        # Anagram?
        is_anagram = v1 == v2
        if is_anagram:
            w.writeln("  Anagram status: YES — identical codex ✓", "pass")
        else:
            w.writeln("  Anagram status: NO — different codex", "dim")

        w.writeln()
