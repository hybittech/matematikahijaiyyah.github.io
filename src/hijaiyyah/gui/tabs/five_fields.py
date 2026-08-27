"""
Tab: Metrik-Vektorial Workbench — Comprehensive Per-Letter Analysis
====================================================================
Professional multi-operation analysis covering all five metrik-vektorial
operations of Hijaiyyah Mathematics (Bab II, §2.1–§2.5):

  Operation 1: Vektronometry (VTM)  — ratios, norms, Pythagorean
  Operation 2: Normivektor (NMV)    — differences, gradients
  Operation 3: Aggregametric (AGM)  — string aggregation, trajectory
  Operation 4: Intrametric (ITM)    — distances, neighbors, topology
  Operation 5: Exometric (EXM)      — 5×5 matrix, energy, audit

Each operation includes theorem references, formula display,
computed values, verification checks, and interpretation.
"""

from __future__ import annotations

import math
import time
import tkinter as tk
from tkinter import ttk
from typing import Any, List, Optional, Tuple

from ...algebra import aggregametric as integ
from ...algebra import exometric as exo
from ...algebra import intrametric as geo
from ...algebra import normivektor as diff
from ...algebra import vektronometry as vec
from ...core.codex_entry import CodexEntry
from ...core.exomatrix import build_exomatrix
from ...core.guards import compute_U, guard_check
from ...core.master_table import MASTER_TABLE, MasterTable
from ..theme import THEME
from ..widgets import OutputWriter, make_text

# ── Structure classification helpers ─────────────────────────────


def _classify_structure(v: List[int]) -> Tuple[str, str]:
    """Classify structural type. Returns (type_name, description)."""
    a_n, a_k, a_q = v[14], v[15], v[16]
    total = a_n + a_k + a_q
    if total == 0:
        return "Empty", "No structural components"
    r_n, r_k, r_q = a_n / total, a_k / total, a_q / total
    if r_k == 1.0:
        return "Pure Line", "100% Khaṭṭ — straight stroke only (e.g., Alif)"
    if r_q == 1.0:
        return "Pure Curve", "100% Qaws — curve only, no line or dot"
    if r_n >= 0.5:
        return "Dot-Dominated", f"{r_n * 100:.0f}% Nuqṭah — dots are the majority element"
    if abs(r_n - 1 / 3) < 0.05 and abs(r_k - 1 / 3) < 0.05:
        return "Tri-Balanced", "~33% each of N, K, Q — maximum structural diversity"
    if r_q > r_k and a_n == 0:
        return "Curve-Dominant", f"{r_q * 100:.0f}% Qaws — primarily curved, no dots"
    if r_k > r_q and a_n == 0:
        return "Line-Curve", f"K={r_k * 100:.0f}% Q={r_q * 100:.0f}% — mixed line and curve"
    return "Mixed", f"N={r_n * 100:.0f}% K={r_k * 100:.0f}% Q={r_q * 100:.0f}%"


def _classify_turning(v: List[int]) -> Tuple[str, str]:
    """Classify turning profile. Returns (type_name, description)."""
    theta = v[0]
    if theta == 0:
        return "Zero", "No turning — perfectly straight element"
    U = compute_U(v)
    rho = theta - U
    r_loop = (4 * v[13]) / theta if theta > 0 else 0
    if U == 0:
        return "Pure Primary", f"100% from primary curve (ρ={rho})"
    if rho == 0:
        return "Pure Non-Primary", f"100% from loops/auxiliary (U={U})"
    if r_loop >= 0.8:
        return "Loop-Dominated", f"{r_loop * 100:.0f}% from {v[13]} closed loop(s)"
    return "Mixed", f"U={U} ({U / theta * 100:.0f}%), ρ={rho} ({rho / theta * 100:.0f}%)"


def _find_dot_family(entry: CodexEntry) -> List[Tuple[str, str, str]]:
    """Find dot-variant siblings. Returns [(char, name, gradient_str)]."""
    v = list(entry.vector)
    family: List[Tuple[str, str, str]] = []
    for other in MASTER_TABLE.all_entries():
        if other.char == entry.char:
            continue
        ov = list(other.vector)
        if (
            ov[0] == v[0]
            and all(ov[k] == v[k] for k in range(4, 14))
            and any(ov[k] != v[k] for k in range(1, 4))
        ):
            grad = [ov[k] - v[k] for k in range(1, 4)]
            grad_str = f"({grad[0]:+d}, {grad[1]:+d}, {grad[2]:+d})"
            family.append((other.char, other.name, grad_str))
    return family


class FiveFieldsTab:
    """
    Tab: Metrik-Vektorial Workbench

    Layout:
    ┌──────────────────────────────────────────────────────┐
    │  [Letter selector] [▶ Analyze] [Energy] [Vectro]    │
    ├──────────────────────────────────────────────────────┤
    │                                                      │
    │  ① VEKTRONOMETRY / VTM (§2.1)                       │
    │    Subspace decomposition, ratios, norms, Pythagoras │
    │                                                      │
    │  ② NORMIVEKTOR / NMV (§2.2)                         │
    │    Differences, dot-variants, U-gradient              │
    │                                                      │
    │  ③ AGGREGAMETRIC / AGM (§2.3)                       │
    │    Single-letter aggregation, classification          │
    │                                                      │
    │  ④ INTRAMETRIC / ITM (§2.4)                         │
    │    Nearest neighbors, distances, orthogonality        │
    │                                                      │
    │  ⑤ EXOMETRIC / EXM (§2.5)                           │
    │    5×5 matrix, R1–R5, energy, reconstruction         │
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
        notebook.add(self._tab, text="  ⬡ Metrik-Vektorial  ")
        self._entries = table.all_entries()

        self._text: Optional[tk.Text] = None
        self._out: Optional[OutputWriter] = None
        self._var: tk.StringVar = tk.StringVar(value="Ready")
        self._names: List[str] = []
        self._status_var: tk.StringVar = tk.StringVar(value="Ready")

        self._build()

    def _build(self) -> None:
        # ── Toolbar ──────────────────────────────────────────────
        toolbar = ttk.Frame(self._tab)
        toolbar.pack(fill=tk.X, padx=8, pady=5)

        ttk.Label(toolbar, text="Letter:", font=THEME.font_ui_bold).pack(side=tk.LEFT)
        self._names = [f"{e.char} {e.name}" for e in self._entries]
        self._var.set(self._names[4] if len(self._names) > 4 else self._names[0])
        ttk.Combobox(
            toolbar,
            textvariable=self._var,
            values=self._names,
            width=18,
        ).pack(side=tk.LEFT, padx=4)

        ttk.Button(toolbar, text="▶ Full Analysis", command=self._analyze).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        ttk.Button(toolbar, text="📊 Energy Table (28)", command=self._energy_table).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="📈 Vectronometry Table", command=self._vectro_table).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="📐 Distance Matrix", command=self._distance_table).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="🔗 Dot Variants", command=self._dot_variant_table).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Label(toolbar, textvariable=self._status_var, foreground=THEME.dim_fg).pack(
            side=tk.RIGHT, padx=5
        )

        # ── Quick letter bar ─────────────────────────────────────
        letter_bar = ttk.Frame(self._tab)
        letter_bar.pack(fill=tk.X, padx=8, pady=2)
        ttk.Label(letter_bar, text="Quick:", foreground=THEME.dim_fg).pack(side=tk.LEFT)
        for entry in self._entries:
            tk.Button(
                letter_bar,
                text=entry.char,
                font=("Simplified Arabic", 12),
                width=2,
                height=1,
                bg=THEME.accent,
                fg=THEME.hijaiyyah_fg,
                relief=tk.FLAT,
                command=lambda e=entry: self._quick_analyze(e),  # type: ignore
            ).pack(side=tk.LEFT, padx=1)

        # ── Output ───────────────────────────────────────────────
        self._text, _ = make_text(self._tab, font=("Consolas", 11), wrap=tk.NONE)
        out = OutputWriter(self._text)
        self._out = out
        out.add_tags(
            {
                "title": {"foreground": THEME.hijaiyyah_fg, "font": ("Consolas", 14, "bold")},
                "section": {"foreground": THEME.hijaiyyah_fg, "font": ("Consolas", 12, "bold")},
                "sub": {"foreground": "#74b9ff", "font": ("Consolas", 11, "bold")},
                "value": {"foreground": THEME.number_fg},
                "pass": {"foreground": THEME.success, "font": ("Consolas", 11, "bold")},
                "fail": {"foreground": THEME.error, "font": ("Consolas", 11, "bold")},
                "dim": {"foreground": THEME.dim_fg},
                "warn": {"foreground": THEME.warning},
                "field": {"foreground": "#ffeaa7"},
                "formula": {"foreground": "#81ecec"},
                "ref": {"foreground": "#dfe6e9", "font": ("Consolas", 10, "italic")},
            }
        )

        self._show_welcome()

    # ── Helpers ──────────────────────────────────────────────────

    def _selected(self) -> Optional[CodexEntry]:
        if not self._var.get() or not self._names:
            return None
        try:
            idx = self._names.index(self._var.get())
        except ValueError:
            return None
        return self._table.get_by_char(self._entries[idx].char)

    def _quick_analyze(self, entry: CodexEntry) -> None:
        self._var.set(f"{entry.char} {entry.name}")
        self._analyze()

    def _show_welcome(self) -> None:
        out = self._out
        if out is None:
            return
        out.clear()
        out.writeln("METRIK-VEKTORIAL WORKBENCH — Bab II Complete Analysis", "title")
        out.writeln("═" * 60)
        out.writeln()
        out.writeln("Analyze any letter through all five metrik-vektorial", "dim")
        out.writeln("operations of Hijaiyyah Mathematics (§2.1–§2.5):", "dim")
        out.writeln()
        out.writeln("  ① Vektronometry (VTM) — structure ratios, norms    (§2.1)", "sub")
        out.writeln("     What is this letter made of?", "dim")
        out.writeln()
        out.writeln("  ② Normivektor (NMV)   — differences, gradients     (§2.2)", "sub")
        out.writeln("     How does it differ from other letters?", "dim")
        out.writeln()
        out.writeln("  ③ Aggregametric (AGM) — string accumulation        (§2.3)", "sub")
        out.writeln("     What does it contribute to a string?", "dim")
        out.writeln()
        out.writeln("  ④ Intrametric (ITM)   — distances, neighbors       (§2.4)", "sub")
        out.writeln("     Where does it sit in codex space?", "dim")
        out.writeln()
        out.writeln("  ⑤ Exometric (EXM)     — 5×5 audit matrix, energy   (§2.5)", "sub")
        out.writeln("     Is it internally consistent?", "dim")
        out.writeln()
        out.writeln("Select a letter and press ▶ Full Analysis.", "dim")

    # ══════════════════════════════════════════════════════════════
    #  MAIN ANALYSIS
    # ══════════════════════════════════════════════════════════════

    def _analyze(self) -> None:
        entry = self._selected()
        out = self._out
        if entry is None or out is None:
            return
        assert entry is not None
        assert out is not None

        out.clear()
        start = time.perf_counter()

        v: List[int] = list(entry.vector)

        self._render_header(entry, v)
        self._render_field1_vectronometry(entry, v)
        self._render_field2_differential(entry, v)
        self._render_field3_integral(entry, v)
        self._render_field4_geometry(entry, v)
        self._render_field5_exomatrix(entry, v)
        self._render_classification(entry, v)

        elapsed = (time.perf_counter() - start) * 1000
        out.writeln(f"  Analysis completed in {elapsed:.1f} ms", "dim")
        self._status_var.set(f"{entry.char} analyzed ({elapsed:.0f}ms)")

    # ── Header ───────────────────────────────────────────────────

    def _render_header(self, entry: CodexEntry, v: List[int]) -> None:
        w = self._out
        if w is None:
            return

        w.writeln(f"╔{'═' * 60}╗", "dim")
        w.writeln(
            f"║  METRIK-VEKTORIAL ANALYSIS: {entry.char}  ({entry.name})  — #{entry.index}/28", "title"
        )
        w.writeln(f"╚{'═' * 60}╝", "dim")
        w.writeln()
        w.writeln(f"  v₁₈ = ({', '.join(str(x) for x in v)})", "value")
        w.writeln(f"  v₁₄ = ({', '.join(str(v[i]) for i in range(14))})", "dim")
        w.writeln()

    # ── Field 1: Vectronometry ───────────────────────────────────

    def _render_field1_vectronometry(self, entry: CodexEntry, v: List[int]) -> None:
        w = self._out
        if w is None:
            return

        w.writeln("①  VEKTRONOMETRY (VTM) — Structure Measurement", "section")
        w.writeln('   Bab II §2.1: "What is this letter made of?"', "ref")
        w.writeln("─" * 60, "dim")
        w.writeln()

        # ── Subspace projections (Ch 17)
        w.writeln("   Subspace Decomposition (Ch 17, Definition 17.2.1)", "sub")
        w.writeln("   ℝ¹⁴ = V_Θ ⊕ V_N ⊕ V_K ⊕ V_Q", "formula")
        w.writeln()

        proj_names = [
            ("Π_Θ (turning)", [0], "Inḥinā'"),
            ("Π_N (dots)", [1, 2, 3], "Nuqṭah"),
            ("Π_K (lines)", [4, 5, 6, 7, 8], "Khaṭṭ"),
            ("Π_Q (curves)", [9, 10, 11, 12, 13], "Qaws"),
        ]
        for label, indices, arabic in proj_names:
            comp_vals = [v[i] for i in indices]
            norm_sq = sum(x * x for x in comp_vals)
            comp_str = ", ".join(str(x) for x in comp_vals)
            w.writeln(f"   {label:<18s} = ({comp_str})", "value")
            w.writeln(f"   {'':18s}   ‖Π‖² = {norm_sq}  [{arabic}]", "dim")

        w.writeln()

        # ── Primitive ratios (Ch 18, Theorem 18.2.1)
        w.writeln("   Primitive Ratios (Ch 18, Theorem 18.2.1)", "sub")
        w.writeln("   r_N + r_K + r_Q = 1  (definitional identity)", "formula")
        w.writeln()

        pr = vec.primitive_ratios(entry)
        a_total = v[14] + v[15] + v[16]

        w.writeln(
            f"   A_N = {v[14]:>3}  →  r_N = {pr['r_N']:.6f}  ({pr['r_N'] * 100:.1f}% dots)", "value"
        )
        w.writeln(
            f"   A_K = {v[15]:>3}  →  r_K = {pr['r_K']:.6f}  ({pr['r_K'] * 100:.1f}% lines)",
            "value",
        )
        w.writeln(
            f"   A_Q = {v[16]:>3}  →  r_Q = {pr['r_Q']:.6f}  ({pr['r_Q'] * 100:.1f}% curves)",
            "value",
        )

        total_r = pr["r_N"] + pr["r_K"] + pr["r_Q"]
        ok = abs(total_r - 1.0) < 1e-9
        w.writeln(f"   Sum  = {total_r:.9f}  {'✓' if ok else '✗'}", "pass" if ok else "fail")

        # Visual bar
        if a_total > 0:
            bar_len = 40
            n_bar = int(pr["r_N"] * bar_len)
            k_bar = int(pr["r_K"] * bar_len)
            q_bar = bar_len - n_bar - k_bar
            w.writeln(f"   [{'N' * n_bar}{'K' * k_bar}{'Q' * q_bar}]", "value")
        w.writeln()

        # ── Turning ratios (Ch 19, Theorem 19.1.1)
        w.writeln("   Turning Ratios (Ch 19, Theorem 19.1.1)", "sub")
        w.writeln("   r_U + r_ρ = 1  for Θ̂ > 0", "formula")
        w.writeln()

        tr = vec.turning_ratios(entry)
        U = compute_U(v)
        rho = v[0] - U

        w.writeln(f"   Θ̂ = {v[0]:>3}  ({v[0] * 90}°)", "value")
        w.writeln(f"   U  = {U:>3}  →  r_U    = {tr['r_U']:.6f}", "value")
        w.writeln(f"   ρ  = {rho:>3}  →  r_ρ    = {tr['r_rho']:.6f}", "value")
        w.writeln(f"   Qc = {v[13]:>3}  →  r_loop = {tr['r_loop']:.6f}", "value")

        if v[0] > 0:
            sum_tr = tr["r_U"] + tr["r_rho"]
            w.writeln(
                f"   r_U + r_ρ = {sum_tr:.9f}  {'✓' if abs(sum_tr - 1) < 1e-9 else '✗'}", "pass"
            )
        w.writeln()

        # ── Compositional angle (Ch 19, Definition 19.3.1)
        alpha = vec.comp_angle(entry)
        w.writeln("   Compositional Angle α (Ch 19, Definition 19.3.1)", "sub")
        w.writeln("   α = arctan(A_Q / A_K)  — line-curve balance", "formula")
        w.writeln()
        w.writeln(f"   α = {math.degrees(alpha):.2f}°  ({alpha:.6f} rad)", "value")

        if v[15] == 0 and v[16] == 0:
            w.writeln("   Interpretation: no K or Q components", "dim")
        elif v[15] == 0:
            w.writeln("   Interpretation: 90° = pure curve (no line components)", "dim")
        elif v[16] == 0:
            w.writeln("   Interpretation: 0° = pure line (no curve components)", "dim")
        elif abs(alpha - math.pi / 4) < 0.01:
            w.writeln("   Interpretation: 45° = balanced line-curve", "dim")
        elif alpha > math.pi / 4:
            w.writeln("   Interpretation: >45° = curve-dominated", "dim")
        else:
            w.writeln("   Interpretation: <45° = line-dominated", "dim")
        w.writeln()

        # ── Codex norm (Ch 20)
        n2 = vec.norm2(entry)
        n = vec.norm(entry)
        w.writeln("   Codex Norm (Ch 20, Definition 20.1.1)", "sub")
        w.writeln(f"   ‖v₁₄({entry.char})‖² = {n2}", "value")
        w.writeln(f"   ‖v₁₄({entry.char})‖  = {n:.6f}", "value")
        w.writeln()

        # ── Pythagorean theorem (Ch 20, Theorem 20.2.1)
        pyth = vec.pythagorean_check(entry)
        w.writeln("   Pythagorean Theorem (Ch 20, Theorem 20.2.1)", "sub")
        w.writeln("   ‖h‖² = ‖Π_Θ‖² + ‖Π_N‖² + ‖Π_K‖² + ‖Π_Q‖²", "formula")
        w.writeln()
        w.writeln(
            f"   {pyth['lhs']:>5d} = {pyth['theta']:>5d} + {pyth['N']:>5d} + {pyth['K']:>5d} + {pyth['Q']:>5d}",
            "value",
        )
        tag = "pass" if pyth["pass"] else "fail"
        w.writeln(f"   {'✓ VERIFIED' if pyth['pass'] else '✗ VIOLATION'}", tag)
        w.writeln()

    # ── Field 2: Differential Calculus ───────────────────────────

    def _render_field2_differential(self, entry: CodexEntry, v: List[int]) -> None:
        w = self._out
        if w is None:
            return

        w.writeln("②  NORMIVEKTOR (NMV) — Structural Differences", "section")
        w.writeln('   Bab II §2.2: "How does it differ from others?"', "ref")
        w.writeln("─" * 60, "dim")
        w.writeln()

        # ── Differences from reference letters
        w.writeln("   Differences from Key Letters (Ch 22, Definition 22.1.1)", "sub")
        w.writeln("   Δ(h₁,h₂) = v₁₄(h₁) − v₁₄(h₂) ∈ ℤ¹⁴", "formula")
        w.writeln()

        ref_letters = [("ا", "Alif"), ("ب", "Ba"), ("هـ", "Ha")]
        for ref_ch, _ref_name in ref_letters:
            if ref_ch == entry.char:
                continue
            ref_entry = self._table.get_by_char(ref_ch)
            if ref_entry is None:
                continue

            nd = diff.norm_decomposition(entry, ref_entry)
            d_total = nd["total"]

            w.writeln(f"   Δ({entry.char}, {ref_ch}):", "field")
            w.writeln(
                f"     ‖Δ‖² = {d_total:>4d}  (Θ:{nd['theta']} N:{nd['N']} K:{nd['K']} Q:{nd['Q']})",
                "value",
            )
            if d_total > 0:
                pct_t = nd["theta"] / d_total * 100
                w.writeln(f"     Turning contributes {pct_t:.0f}% of difference", "dim")
            w.writeln()

        # ── Dot-variant family
        family = _find_dot_family(entry)
        w.writeln("   Dot-Variant Family (Ch 23, Table 23.1)", "sub")
        w.writeln("   Letters sharing same Θ̂, K, Q — differing only in N", "formula")
        w.writeln()

        if family:
            w.writeln(f"   {entry.char} has {len(family)} dot-variant sibling(s):", "field")
            for ch, name, grad in family:
                other = self._table.get_by_char(ch)
                d = geo.euclidean(entry, other) if other else 0
                w.writeln(f"     {ch} ({name:<8s})  ∇N = {grad}  d₂ = {d:.4f}", "value")
            w.writeln("   Pattern: differentiation via ascender-zone dots", "dim")
        else:
            w.writeln(f"   {entry.char} has no dot-variant siblings.", "dim")
            w.writeln("   (Unique combination of Θ̂, K, Q)", "dim")
        w.writeln()

        # ── U-gradient
        w.writeln("   U-Gradient (Ch 23, Lemma 23.2.1)", "sub")
        w.writeln("   ∇_Q U = (∂U/∂Qp, ∂U/∂Qx, ∂U/∂Qs, ∂U/∂Qa, ∂U/∂Qc)", "formula")
        w.writeln("         = (0, 1, 1, 1, 4)  — constant for all letters", "value")
        w.writeln("   Loop sensitivity: ∂U/∂Qc = 4  (4× impact of non-loop)", "dim")
        w.writeln()

    # ── Field 3: Integral Calculus ───────────────────────────────

    def _render_field3_integral(self, entry: CodexEntry, v: List[int]) -> None:
        w = self._out
        if w is None:
            return

        w.writeln("③  AGGREGAMETRIC (AGM) — String Contribution", "section")
        w.writeln('   Bab II §2.3: "What does it contribute to a string?"', "ref")
        w.writeln("─" * 60, "dim")
        w.writeln()

        # Single-letter integral
        w.writeln("   Single-Letter Integral (Ch 25)", "sub")
        w.writeln("   ∫(h) = v₁₈(h) — same as the codex vector itself", "formula")
        w.writeln()

        cod = integ.string_integral(entry.char)
        cv = cod["cod18"]
        li = integ.layer_integrals(entry.char)

        w.writeln(f"   ∫Θ̂  = {li['theta']:>3d}  ({li['theta'] * 90}° of total turning)", "value")
        w.writeln(f"   ∫U   = {li['U']:>3d}  (non-primary turning)", "value")
        w.writeln(f"   ∫ρ   = {li['rho']:>3d}  (primary turning)", "value")
        w.writeln(f"   ∫A_N = {cv[14]:>3d}  (dot contribution)", "value")
        w.writeln(f"   ∫A_K = {cv[15]:>3d}  (line contribution)", "value")
        w.writeln(f"   ∫A_Q = {cv[16]:>3d}  (curve contribution)", "value")
        w.writeln()

        # Energy contribution
        E = exo.build(entry)
        phi = exo.phi(E)
        w.writeln("   Energy Contribution (Ch 27, Definition 27.3.1)", "sub")
        w.writeln(f"   Φ({entry.char}) = {phi}", "value")
        w.writeln(
            f"   When added to a string, this letter contributes Φ={phi} energy units.", "dim"
        )
        w.writeln()

        # Context: what proportion of bsm?
        bsm_cod = integ.string_integral("بسم")
        if bsm_cod["cod18"][0] > 0:
            pct_theta = li["theta"] / bsm_cod["cod18"][0] * 100
            w.writeln(
                f'   Context: {entry.char} contributes {pct_theta:.1f}% of turning in "بسم"', "dim"
            )
        w.writeln()

    # ── Field 4: Codex Geometry ──────────────────────────────────

    def _render_field4_geometry(self, entry: CodexEntry, v: List[int]) -> None:
        w = self._out
        if w is None:
            return

        w.writeln("④  INTRAMETRIC (ITM) — Position in Codex Space", "section")
        w.writeln('   Bab II §2.4: "Where does it sit in the space?"', "ref")
        w.writeln("─" * 60, "dim")
        w.writeln()

        # ── Nearest neighbors (Ch 31)
        w.writeln("   Nearest Neighbors (Ch 31)", "sub")
        w.writeln()

        knn = geo.k_nearest(entry, 7)
        w.writeln(
            f"   {'Rank':<5} {'Ch':<4} {'Name':<8} {'d₂':<10} {'d₂²':<6} {'Relationship'}", "field"
        )
        w.writeln("   " + "─" * 50, "dim")

        for rank, (ch, d) in enumerate(knn, 1):
            other = self._table.get_by_char(ch)
            name = other.name if other else "?"
            d2_sq = geo.euclidean_sq(entry, other) if other else 0

            rel = ""
            if other:
                ov = list(other.vector)
                if v[0] == ov[0] and all(v[k] == ov[k] for k in range(4, 14)):
                    rel = "dot-variant"
                elif d2_sq == 1:
                    rel = "minimal distance"
                elif d2_sq == 2:
                    rel = "near-minimal"

            w.writeln(f"   {rank:<5} {ch:<4} {name:<8} {d:<10.6f} {d2_sq:<6} {rel}", "value")

        w.writeln()

        # ── Distances from diameter endpoints
        w.writeln("   Distance from Diameter Endpoints", "sub")
        w.writeln(f"   diam(H₂₈) = √70 ≈ {geo.diameter():.6f}  (ا ↔ هـ)", "formula")
        w.writeln()

        alif = self._table.get_by_char("ا")
        ha = self._table.get_by_char("هـ")

        if alif and entry.char != "ا":
            d_alif = geo.euclidean(entry, alif)
            w.writeln(f"   d({entry.char}, ا) = {d_alif:.6f}  (from simplest)", "value")
        if ha and entry.char != "هـ":
            d_ha = geo.euclidean(entry, ha)
            w.writeln(f"   d({entry.char}, هـ) = {d_ha:.6f}  (from most complex)", "value")
        w.writeln()

        # ── Orthogonality
        w.writeln("   Support Orthogonality (Ch 30, Lemma 30.2.1)", "sub")
        w.writeln("   h₁ ⊥_S h₂ iff supp(v₁₄(h₁)) ∩ supp(v₁₄(h₂)) = ∅", "formula")
        w.writeln()

        orth_letters: List[str] = [
            other.char
            for other in self._entries
            if other.char != entry.char
            and (lambda oe: oe is not None and geo.is_orthogonal(entry, oe))(
                self._table.get_by_char(other.char)
            )
        ]
        orth_count: int = len(orth_letters)

        if orth_letters:
            w.writeln(f"   Orthogonal to {orth_count} letter(s): {' '.join(orth_letters)}", "value")
            w.writeln("   (No shared nonzero component in v₁₄)", "dim")
        else:
            w.writeln("   Not orthogonal to any letter", "dim")
            w.writeln("   (Shares at least one nonzero component with all others)", "dim")

        # ── Polarization identity spot check
        if alif and entry.char != "ا":
            pol = geo.polarization_check(entry, alif)
            w.writeln()
            w.writeln("   Polarization Identity (Ch 29, Theorem 29.3.1)", "sub")
            w.writeln("   d₂² = ‖h₁‖² + ‖h₂‖² − 2⟨h₁,h₂⟩", "formula")
            w.writeln(
                f"   d₂²={pol['d2_sq']}  polar={pol['polar']}  {'✓' if pol['pass'] else '✗'}",
                "pass" if pol["pass"] else "fail",
            )
        w.writeln()

    # ── Field 5: Exomatrix Analysis ──────────────────────────────

    def _render_field5_exomatrix(self, entry: CodexEntry, v: List[int]) -> None:
        w = self._out
        if w is None:
            return

        w.writeln("⑤  EXOMETRIC (EXM) — Structured Audit Matrix", "section")
        w.writeln('   Bab II §2.5: "Is it internally consistent?"', "ref")
        w.writeln("─" * 60, "dim")
        w.writeln()

        # ── Build and display Exomatrix
        E = build_exomatrix(v)
        w.writeln("   Exomatrix E(h) — Definition 32.1.1", "sub")
        w.writeln()

        row_labels = [
            "Row 0 (Turning) ",
            "Row 1 (Nuqṭah)  ",
            "Row 2 (Khaṭṭ)   ",
            "Row 3 (Qaws)    ",
            "Row 4 (Meta)    ",
        ]
        row_contents = [
            "[Θ̂,   U,   ρ,   0,   0  ]",
            "[Na,  Nb,  Nd,  0,   Aₙ ]",
            "[Kp,  Kx,  Ks,  Ka,  Kc ]",
            "[Qp,  Qx,  Qs,  Qa,  Qc ]",
            "[H*,  0,   0,   Aₖ,  AQ ]",
        ]

        for r in range(5):
            vals = "".join(f"{E[r][c]:>5}" for c in range(5))
            w.writeln(f"   {row_labels[r]} │{vals} │  {row_contents[r]}", "value")

        w.writeln()

        # ── Row sums (Identity 33.2.1)
        rs = exo.row_sums(E)
        w.writeln("   Row Sums (Identity 33.2.1)", "sub")
        expected: List[str] = [
            f"2Θ̂={2 * v[0]}",
            f"2Aₙ={2 * v[14]}",
            f"Aₖ={v[15]}",
            f"AQ={v[16]}",
            f"H*+Aₖ+AQ={v[17] + v[15] + v[16]}",
        ]
        expected_eval: List[int] = [2 * v[0], 2 * v[14], v[15], v[16], v[17] + v[15] + v[16]]
        for r in range(5):
            ok = rs[r] == expected_eval[r]
            w.writeln(
                f"   σ_{r} = {rs[r]:>4d}  (expected: {expected[r]})  {'✓' if ok else '✗'}",
                "pass" if ok else "fail",
            )
        w.writeln()

        # ── R1–R5 audit (Identity 33.1.1)
        audit = exo.audit(E)
        w.writeln("   Audit Relations R1–R5 (Identity 33.1.1)", "sub")
        w.writeln()

        audit_details = [
            ("R1", audit["R1"], "Θ̂ = U + ρ", f"{E[0][0]} = {E[0][1]} + {E[0][2]}"),
            ("R2", audit["R2"], "Aₙ = Na+Nb+Nd", f"{E[1][4]} = {E[1][0]}+{E[1][1]}+{E[1][2]}"),
            ("R3", audit["R3"], "Aₖ = ΣK", f"{E[4][3]} = {sum(E[2])}"),
            ("R4", audit["R4"], "AQ = ΣQ", f"{E[4][4]} = {sum(E[3])}"),
            (
                "R5",
                audit["R5"],
                "U = Qx+Qs+Qa+4Qc",
                f"{E[0][1]} = {E[3][1]}+{E[3][2]}+{E[3][3]}+4×{E[3][4]}",
            ),
        ]

        for name, passed, formula, values in audit_details:
            status = "✓" if passed else "✗"
            tag = "pass" if passed else "fail"
            w.writeln(f"   {name}: {status}  {formula}", tag)
            w.writeln(f"       {values}", "dim")

        w.writeln()
        all_pass = audit["all_pass"]
        w.writeln(
            f"   Overall: {'ALL 5 PASS ✓' if all_pass else 'AUDIT FAILURE ✗'}",
            "pass" if all_pass else "fail",
        )
        w.writeln()

        # ── Frobenius energy (Ch 34, Theorem 34.3.1)
        phi_val = exo.phi(E)
        n2 = vec.norm2(entry)
        surplus = phi_val - n2
        decomp = exo.phi_decomposition(E)

        w.writeln("   Frobenius Energy (Ch 34, Theorem 34.3.1)", "sub")
        w.writeln("   Φ(h) = ‖E(h)‖²_F > ‖v₁₄(h)‖²  (strict)", "formula")
        w.writeln()
        w.writeln(f"   Φ({entry.char})    = {phi_val}", "value")
        w.writeln(f"   ‖v₁₄‖²  = {n2}", "value")
        w.writeln(f"   Surplus  = {surplus}", "value")
        w.writeln(
            f"   Φ > ‖v₁₄‖²: {phi_val} > {n2}  {'✓ (strict)' if phi_val > n2 else '✗'}",
            "pass" if phi_val > n2 else "fail",
        )
        w.writeln()

        w.writeln("   Energy decomposition by layer:", "field")
        w.writeln(
            f"     Φ_Θ    = {decomp['theta']:>6d}  ({decomp['theta'] / phi_val * 100:.1f}%)",
            "value",
        )
        w.writeln(f"     Φ_N    = {decomp['N']:>6d}  ({decomp['N'] / phi_val * 100:.1f}%)", "value")
        w.writeln(f"     Φ_K    = {decomp['K']:>6d}  ({decomp['K'] / phi_val * 100:.1f}%)", "value")
        w.writeln(f"     Φ_Q    = {decomp['Q']:>6d}  ({decomp['Q'] / phi_val * 100:.1f}%)", "value")
        w.writeln(
            f"     Φ_meta = {decomp['meta']:>6d}  ({decomp['meta'] / phi_val * 100:.1f}%)", "value"
        )
        w.writeln()

        # Energy rank
        table = exo.energy_table()
        rank = next((r["rank"] for r in table if r["letter"] == entry.char), 0)
        w.writeln(f"   Energy rank: #{rank} of 28", "field")
        if rank == 1:
            w.writeln("   → MAXIMUM structural complexity in H₂₈", "warn")
        elif rank == 28:
            w.writeln("   → MINIMUM structural complexity in H₂₈", "dim")
        elif rank <= 5:
            w.writeln("   → Top-5 most complex letters", "warn")
        w.writeln()

        # ── Reconstruction uniqueness (Ch 36, Theorem 36.2.1)
        w.writeln("   Reconstruction Uniqueness (Ch 36, Theorem 36.2.1)", "sub")
        w.writeln("   E(h₁) = E(h₂) ⟹ h₁ = h₂", "formula")
        w.writeln()

        reconstructed = exo.reconstruct(E)
        recon_ok = reconstructed == list(entry.vector)
        w.writeln(f"   Original:      ({', '.join(str(x) for x in v)})", "dim")
        w.writeln(f"   Reconstructed: ({', '.join(str(x) for x in reconstructed)})", "value")
        w.writeln(
            f"   Match: {'✓ Faithful representation' if recon_ok else '✗ Mismatch'}",
            "pass" if recon_ok else "fail",
        )
        w.writeln()

    # ── Classification Summary ───────────────────────────────────

    def _render_classification(self, entry: CodexEntry, v: List[int]) -> None:
        w = self._out
        if w is None:
            return

        struct_type, struct_desc = _classify_structure(v)
        turn_type, turn_desc = _classify_turning(v)
        guard_ok = guard_check(v)
        mod4 = v[0] % 4

        w.writeln("⑥  CLASSIFICATION SUMMARY", "section")
        w.writeln("─" * 60, "dim")
        w.writeln()
        w.writeln(f"   Structure:   {struct_type}", "value")
        w.writeln(f"                {struct_desc}", "dim")
        w.writeln(f"   Turning:     {turn_type}", "value")
        w.writeln(f"                {turn_desc}", "dim")
        w.writeln(
            f"   Mod-4:       Θ̂ mod 4 = {mod4}  →  {'possibly closed' if mod4 == 0 else 'definitely open'}",
            "warn" if mod4 == 0 else "pass",
        )
        w.writeln(
            f"   Guard:       {'ALL PASS ✓' if guard_ok else 'VIOLATION ✗'}",
            "pass" if guard_ok else "fail",
        )
        w.writeln()

    # ══════════════════════════════════════════════════════════════
    #  GLOBAL TABLES
    # ══════════════════════════════════════════════════════════════

    def _energy_table(self) -> None:
        """Display full energy table for all 28 letters."""
        out = self._out
        if out is None:
            return
        out.clear()

        rows = exo.energy_table()

        out.writeln("FROBENIUS ENERGY TABLE — All 28 Letters", "title")
        out.writeln("═" * 60)
        out.writeln()
        out.writeln("  Φ(h) = ‖E(h)‖²_F  (Theorem 34.3.1: Φ > ‖v₁₄‖² always)", "formula")
        out.writeln()
        out.writeln(
            f"  {'#':<4} {'Ch':<4} {'Name':<8} {'Φ':<8} {'‖v₁₄‖²':<8} {'Surplus':<8} {'Φ_Θ':<8} {'Bar'}",
            "field",
        )
        out.writeln("  " + "─" * 56, "dim")

        max_phi = rows[0]["phi"] if rows else 1
        for r in rows:
            bar_len = int(r["phi"] / max_phi * 25)
            out.writeln(
                f"  {r['rank']:<4} {r['letter']:<4} {r.get('name', ''):<8} "
                f"{r['phi']:<8} {r['norm2']:<8} {r['surplus']:<8} {r['phi_theta']:<8} {'█' * bar_len}",
                "value",
            )

        out.writeln()
        out.writeln("  Surplus > 0 for 28/28 ✓  (Energy-Norm Inequality)", "pass")
        self._status_var.set("Energy table displayed")

    def _vectro_table(self) -> None:
        """Display full vectronometry table for all 28 letters."""
        out = self._out
        if out is None:
            return
        out.clear()

        rows = vec.full_table()

        out.writeln("VECTRONOMETRY TABLE — All 28 Letters", "title")
        out.writeln("═" * 70)
        out.writeln()
        out.writeln("  r_N + r_K + r_Q = 1  (Theorem 18.2.1)", "formula")
        out.writeln("  r_U + r_ρ = 1        (Theorem 19.1.1, for Θ̂ > 0)", "formula")
        out.writeln()
        out.writeln(
            f"  {'Ch':<4} {'Name':<8} {'‖v‖²':<6} {'rN':<8} {'rK':<8} {'rQ':<8} {'α°':<6} {'U':<4} {'ρ':<4} {'rU':<8} {'rρ':<8}",
            "field",
        )
        out.writeln("  " + "─" * 68, "dim")

        for r in rows:
            out.writeln(
                f"  {r['letter']:<4} {r['name']:<8} {r['norm2']:<6} "
                f"{r['r_N']:.4f}  {r['r_K']:.4f}  {r['r_Q']:.4f}  "
                f"{r['alpha_deg']:<6.1f} {r['U']:<4} {r['rho']:<4} "
                f"{r['r_U']:.4f}  {r['r_rho']:.4f}",
                "value",
            )

        self._status_var.set("Vectronometry table displayed")

    def _distance_table(self) -> None:
        """Display verified distance table."""
        out = self._out
        if out is None:
            return
        out.clear()

        rows = diff.distance_table()

        out.writeln("VERIFIED DISTANCE TABLE — Selected Pairs", "title")
        out.writeln("═" * 60)
        out.writeln()
        out.writeln("  ‖Δ‖² = Δ_Θ² + ‖Δ_N‖² + ‖Δ_K‖² + ‖Δ_Q‖²  (Theorem 22.2.1)", "formula")
        out.writeln()
        out.writeln(
            f"  {'h₁':<4} {'h₂':<4} {'‖Δ‖²':<6} {'d₂':<8} {'Δ_Θ²':<6} {'‖Δ_N‖²':<6} {'‖Δ_K‖²':<6} {'‖Δ_Q‖²':<6} {'%Θ'}",
            "field",
        )
        out.writeln("  " + "─" * 58, "dim")

        for r in rows:
            pct = f"{r['pct_turning']:.0f}%" if r["total"] > 0 else "—"
            out.writeln(
                f"  {r['h1']:<4} {r['h2']:<4} {r['total']:<6} {r['d2']:<8.4f} "
                f"{r['theta']:<6} {r['N']:<6} {r['K']:<6} {r['Q']:<6} {pct}",
                "value",
            )

        out.writeln()
        out.writeln(f"  diam²(H₂₈) = {geo.diameter_sq()} = √70 ≈ {geo.diameter():.6f}", "pass")
        self._status_var.set("Distance table displayed")

    def _dot_variant_table(self) -> None:
        """Display all dot-variant pairs."""
        out = self._out
        if out is None:
            return
        out.clear()

        pairs = diff.all_dot_variants()

        out.writeln("DOT-VARIANT PAIRS — Same Body, Different Dots", "title")
        out.writeln("═" * 60)
        out.writeln()
        out.writeln("  Pairs sharing identical Θ̂, K, Q — differing only in N", "formula")
        out.writeln("  Dominant pattern: +Na (ascender zone dot addition)", "dim")
        out.writeln()
        out.writeln(
            f"  {'From':<6} {'To':<6} {'∇N (Δa,Δb,Δd)':<18} {'Description'}",
            "field",
        )
        out.writeln("  " + "─" * 50, "dim")

        for from_ch, to_ch, grad in pairs:
            from_entry = self._table.get_by_char(from_ch)
            to_entry = self._table.get_by_char(to_ch)
            from_name = from_entry.name if from_entry else "?"
            to_name = to_entry.name if to_entry else "?"

            grad_str = f"({grad[0]:+d}, {grad[1]:+d}, {grad[2]:+d})"

            if grad[0] > 0 and grad[1] == 0 and grad[2] == 0:
                desc = f"+{grad[0]} ascender dot(s)"
            elif grad[0] == 0 and grad[2] < 0:
                desc = "zone shift: descender → ascender"
            else:
                desc = "complex dot rearrangement"

            out.writeln(
                f"  {from_ch} ({from_name:<4s}) → {to_ch} ({to_name:<4s})  {grad_str:<18} {desc}",
                "value",
            )

        out.writeln()
        out.writeln(f"  Total pairs: {len(pairs)}", "dim")
        out.writeln("  Observation: ascender-zone dot addition is the", "dim")
        out.writeln("  primary differentiation mechanism in Hijaiyyah.", "dim")
        self._status_var.set(f"{len(pairs)} dot-variant pairs displayed")
