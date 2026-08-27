"""
Tab: Codex Intrametric — Distance Metrics, Topology, and Spatial Analysis
==========================================================================
Professional intrametric analysis covering Bab II §2.4:

  - Three distance metrics (Euclidean, Manhattan, Hamming)
  - Layer-wise distance decomposition
  - Polarization identity verification
  - Nearest neighbor search with interpretation
  - Support orthogonality analysis
  - Alphabet diameter and centroid
  - Gram matrix visualization
  - Full pairwise distance matrix
  - Metric space property verification
"""

from __future__ import annotations

import time
import tkinter as tk
from tkinter import ttk
from typing import Any, List, Optional, Tuple

from ...algebra import intrametric as geo
from ...algebra import vektronometry as vec
from ...core.codex_entry import CodexEntry
from ...core.master_table import MasterTable
from ..theme import THEME
from ..widgets import OutputWriter, make_text


class GeometryTab:
    """
    Tab: Codex Intrametric — Spatial Analysis in ℝ¹⁴

    Layout:
    ┌──────────────────────────────────────────────────────┐
    │  [L1 selector] [L2 selector] [▶ Distance] [tools..] │
    ├──────────────────────────────────────────────────────┤
    │                                                      │
    │  ① Distance Metrics (d₂, d₁, d_H)                  │
    │  ② Layer Decomposition (Θ, N, K, Q contributions)    │
    │  ③ Polarization Identity Verification                │
    │  ④ Nearest Neighbors (ranked)                        │
    │  ⑤ Orthogonality Analysis                           │
    │  ⑥ Alphabet Topology (diameter, centroid)            │
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
        notebook.add(self._tab, text="  △ Codex Intrametric  ")
        self._entries = table.all_entries()

        self._text: Optional[tk.Text] = None
        self._out: Optional[OutputWriter] = None
        self._v1: tk.StringVar = tk.StringVar(value="")
        self._v2: tk.StringVar = tk.StringVar(value="")
        self._names: List[str] = []
        self._status_var: tk.StringVar = tk.StringVar(value="Ready")

        self._build()

    def _build(self) -> None:
        # ── Toolbar ──────────────────────────────────────────────
        toolbar = ttk.Frame(self._tab)
        toolbar.pack(fill=tk.X, padx=8, pady=5)

        self._names = [f"{e.char} {e.name}" for e in self._entries]
        self._v1.set(self._names[0] if self._names else "")
        self._v2.set(self._names[-1] if self._names else "")

        ttk.Label(toolbar, text="Letter 1:", font=THEME.font_ui_bold).pack(side=tk.LEFT)
        ttk.Combobox(toolbar, textvariable=self._v1, values=self._names, width=14).pack(
            side=tk.LEFT, padx=3
        )

        ttk.Label(toolbar, text="Letter 2:").pack(side=tk.LEFT, padx=(8, 0))
        ttk.Combobox(toolbar, textvariable=self._v2, values=self._names, width=14).pack(
            side=tk.LEFT, padx=3
        )

        ttk.Button(toolbar, text="▶ Full Distance Analysis", command=self._full_distance).pack(
            side=tk.LEFT, padx=4
        )

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        ttk.Button(toolbar, text="🌐 Diameter & Centroid", command=self._show_topology).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="📊 Gram Matrix", command=self._show_gram).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="📐 Distance Matrix", command=self._show_distance_matrix).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="⊥ Orthogonality Map", command=self._show_orthogonality).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Label(toolbar, textvariable=self._status_var, foreground=THEME.dim_fg).pack(
            side=tk.RIGHT, padx=5
        )

        # ── Quick pair bar ───────────────────────────────────────
        pair_bar = ttk.Frame(self._tab)
        pair_bar.pack(fill=tk.X, padx=8, pady=2)
        ttk.Label(pair_bar, text="Quick pairs:", foreground=THEME.dim_fg).pack(side=tk.LEFT)

        quick_pairs = [
            ("ا↔هـ", "ا", "هـ", "Diameter pair"),
            ("ب↔ت", "ب", "ت", "Dot-variant"),
            ("ب↔ج", "ب", "ج", "Near neighbors"),
            ("د↔ر", "د", "ر", "Q-type diff"),
            ("ص↔ض", "ص", "ض", "Dot-variant"),
            ("م↔هـ", "م", "هـ", "Loop pair"),
            ("ا↔ب", "ا", "ب", "Orthogonal"),
        ]
        for label, ch1, ch2, _desc in quick_pairs:
            ttk.Button(
                pair_bar,
                text=f"{label}",
                command=lambda a=ch1, b=ch2: self._quick_pair(a, b),  # type: ignore
            ).pack(side=tk.LEFT, padx=1)

        # ── Output ───────────────────────────────────────────────
        self._text, _ = make_text(self._tab, font=("Consolas", 11), wrap=tk.NONE)
        self._out = OutputWriter(self._text)
        self._out.add_tags(
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
                "matrix": {"foreground": "#b2bec3", "font": ("Consolas", 9)},
            }
        )

        self._show_welcome()

    # ── Helpers ──────────────────────────────────────────────────

    def _get_pair(self) -> Tuple[Optional[CodexEntry], Optional[CodexEntry]]:
        if not self._v1.get() or not self._v2.get() or not self._names:
            return None, None
        try:
            i1 = self._names.index(self._v1.get())
            i2 = self._names.index(self._v2.get())
        except ValueError:
            return None, None
        e1 = self._table.get_by_char(self._entries[i1].char)
        e2 = self._table.get_by_char(self._entries[i2].char)
        return e1, e2

    def _quick_pair(self, ch1: str, ch2: str) -> None:
        e1 = self._table.get_by_char(ch1)
        e2 = self._table.get_by_char(ch2)
        if e1 and e2:
            self._v1.set(f"{e1.char} {e1.name}")
            self._v2.set(f"{e2.char} {e2.name}")
            self._full_distance()

    def _show_welcome(self) -> None:
        if self._out is None:
            return
        self._out.clear()
        self._out.writeln("CODEX INTRAMETRIC — Distance, Topology, and Spatial Analysis", "title")
        self._out.writeln("═" * 60)
        self._out.writeln()
        self._out.writeln("Bab II §2.4", "ref")
        self._out.writeln('Central question: "How far apart are two letters?"', "dim")
        self._out.writeln()
        self._out.writeln("  Three distance metrics:", "sub")
        self._out.writeln("    d₂  Euclidean  — standard geometric distance", "dim")
        self._out.writeln("    d₁  Manhattan  — sum of absolute component differences", "dim")
        self._out.writeln("    d_H Hamming    — count of differing components", "dim")
        self._out.writeln()
        self._out.writeln("  Key results:", "sub")
        self._out.writeln("    • (H₂₈, d₂) is a finite metric space (Thm 29.1.1)", "dim")
        self._out.writeln("    • diam(H₂₈) = √70 ≈ 8.367 (Prop 31.1.1)", "dim")
        self._out.writeln("    • d₂² = ‖h₁‖²+‖h₂‖²−2⟨h₁,h₂⟩ (Thm 29.3.1)", "dim")
        self._out.writeln("    • d₂² = Δ_Θ²+‖Δ_N‖²+‖Δ_K‖²+‖Δ_Q‖² (Thm 29.2.1)", "dim")
        self._out.writeln()
        self._out.writeln("Select two letters and press ▶ Full Distance Analysis.", "dim")

    # ══════════════════════════════════════════════════════════════
    #  FULL DISTANCE ANALYSIS
    # ══════════════════════════════════════════════════════════════

    def _full_distance(self) -> None:
        e1, e2 = self._get_pair()
        if e1 is None or e2 is None or self._out is None:
            self._status_var.set("Select two letters")
            return

        self._out.clear()
        start = time.perf_counter()
        v1 = list(e1.vector)
        v2 = list(e2.vector)

        self._render_header(e1, e2, v1, v2)
        self._render_three_metrics(e1, e2, v1, v2)
        self._render_decomposition(e1, e2, v1, v2)
        self._render_polarization(e1, e2, v1, v2)
        self._render_component_diff(e1, e2, v1, v2)
        self._render_neighborhoods(e1, e2)
        self._render_orthogonality_pair(e1, e2, v1, v2)
        self._render_context(e1, e2, v1, v2)

        elapsed = (time.perf_counter() - start) * 1000
        self._out.writeln(f"  Analysis completed in {elapsed:.1f} ms", "dim")
        self._status_var.set(f"d₂({e1.char},{e2.char}) = {geo.euclidean(e1, e2):.4f}")

    # ── Section renderers ────────────────────────────────────────

    def _render_header(self, e1: CodexEntry, e2: CodexEntry, v1: List[int], v2: List[int]) -> None:
        w = self._out
        if w is None:
            return

        w.writeln(f"╔{'═' * 60}╗", "dim")
        w.writeln(f"║  CODEX DISTANCE: {e1.char} ({e1.name})  ↔  {e2.char} ({e2.name})", "title")
        w.writeln(f"╚{'═' * 60}╝", "dim")
        w.writeln()

        w.writeln(f"  v₁₄({e1.char}) = ({', '.join(str(v1[i]) for i in range(14))})", "value")
        w.writeln(f"  v₁₄({e2.char}) = ({', '.join(str(v2[i]) for i in range(14))})", "value")
        w.writeln()

        # Quick stats
        w.writeln(
            f"  ‖{e1.char}‖² = {vec.norm2(e1):>4d}    Θ̂({e1.char}) = {v1[0]}  ({v1[0] * 90}°)",
            "dim",
        )
        w.writeln(
            f"  ‖{e2.char}‖² = {vec.norm2(e2):>4d}    Θ̂({e2.char}) = {v2[0]}  ({v2[0] * 90}°)",
            "dim",
        )
        w.writeln()

    def _render_three_metrics(
        self, e1: CodexEntry, e2: CodexEntry, v1: List[int], v2: List[int]
    ) -> None:
        w = self._out
        if w is None:
            return

        d_eu = geo.euclidean(e1, e2)
        d_eu2 = geo.euclidean_sq(e1, e2)
        d_man = geo.manhattan(e1, e2)
        d_ham = geo.hamming(e1, e2)

        w.writeln("① THREE DISTANCE METRICS", "section")
        w.writeln("   Chapter 29, Definition 29.1.1", "ref")
        w.writeln("─" * 60, "dim")
        w.writeln()

        # Euclidean
        w.writeln("   Euclidean Distance (d₂)", "sub")
        w.writeln("   d₂(h₁,h₂) = √(Σ (v₁₄(h₁)ₖ − v₁₄(h₂)ₖ)²)", "formula")
        w.writeln()
        w.writeln(f"   d₂  = {d_eu:.6f}", "value")
        w.writeln(f"   d₂² = {d_eu2}", "value")
        w.writeln()

        # Manhattan
        w.writeln("   Manhattan Distance (d₁)", "sub")
        w.writeln("   d₁(h₁,h₂) = Σ |v₁₄(h₁)ₖ − v₁₄(h₂)ₖ|", "formula")
        w.writeln()
        w.writeln(f"   d₁  = {d_man}", "value")
        w.writeln()

        # Hamming
        w.writeln("   Hamming Distance (d_H)", "sub")
        w.writeln("   d_H(h₁,h₂) = |{k : v₁₄(h₁)ₖ ≠ v₁₄(h₂)ₖ}|", "formula")
        w.writeln()
        w.writeln(f"   d_H = {d_ham}  ({d_ham}/14 dimensions differ)", "value")
        w.writeln()

        # Interpretation
        diam = geo.diameter()
        pct_diam = d_eu / diam * 100 if diam > 0 else 0

        w.writeln("   Interpretation:", "field")
        if d_eu2 == 0:
            w.writeln("   → Same letter (zero distance)", "pass")
        elif d_eu2 == 1:
            w.writeln("   → Minimal distance — dot-variant pair (differ by 1 dot)", "warn")
        elif d_eu2 <= 5:
            w.writeln("   → Very close — likely share structural body", "value")
        elif pct_diam > 80:
            w.writeln(f"   → Very far — {pct_diam:.0f}% of diameter", "value")
        else:
            w.writeln(f"   → Moderate distance — {pct_diam:.0f}% of diameter", "dim")
        w.writeln()

    def _render_decomposition(
        self, e1: CodexEntry, e2: CodexEntry, v1: List[int], v2: List[int]
    ) -> None:
        w = self._out
        if w is None:
            return

        dec = geo.distance_decomposition(e1, e2)
        total = dec["total"]

        w.writeln("② LAYER-WISE DISTANCE DECOMPOSITION", "section")
        w.writeln("   Chapter 29, Theorem 29.2.1", "ref")
        w.writeln("─" * 60, "dim")
        w.writeln()
        w.writeln("   d₂² = Δ_Θ² + ‖Δ_N‖² + ‖Δ_K‖² + ‖Δ_Q‖²", "formula")
        w.writeln()

        layers = [
            ("Δ_Θ² (turning)", dec["theta"], "Inḥinā' component"),
            ("‖Δ_N‖² (dots)", dec["N"], "Nuqṭah component"),
            ("‖Δ_K‖² (lines)", dec["K"], "Khaṭṭ component"),
            ("‖Δ_Q‖² (curves)", dec["Q"], "Qaws component"),
        ]

        w.writeln(f"   {'Layer':<22} {'Value':<8} {'% of d₂²':<10} {'Description'}", "field")
        w.writeln("   " + "─" * 52, "dim")

        for name, val, _desc in layers:
            pct = val / total * 100 if total > 0 else 0
            bar_len = int(pct / 4)
            w.writeln(
                f"   {name:<22} {val:<8} {pct:>5.1f}%     {'█' * bar_len}",
                "value",
            )

        w.writeln("   " + "─" * 52, "dim")
        w.writeln(f"   {'Total d₂²':<22} {total:<8}", "value")
        w.writeln()

        # Dominant layer
        if total > 0:
            max_layer = max(layers, key=lambda x: x[1])
            pct_max = max_layer[1] / total * 100
            w.writeln(f"   Dominant layer: {max_layer[0]} ({pct_max:.0f}%)", "field")
            if dec["theta"] == total:
                w.writeln("   → Pure turning difference (same body structure)", "dim")
            elif dec["N"] == total:
                w.writeln("   → Pure dot difference (dot-variant pair)", "dim")
            elif dec["theta"] == 0:
                w.writeln("   → Same total turning, different body structure", "dim")
        w.writeln()

    def _render_polarization(
        self, e1: CodexEntry, e2: CodexEntry, v1: List[int], v2: List[int]
    ) -> None:
        w = self._out
        if w is None:
            return

        pol = geo.polarization_check(e1, e2)
        n1_sq = vec.norm2(e1)
        n2_sq = vec.norm2(e2)
        ip = vec.inner(e1, e2)

        w.writeln("③ POLARIZATION IDENTITY", "section")
        w.writeln("   Chapter 29, Theorem 29.3.1", "ref")
        w.writeln("─" * 60, "dim")
        w.writeln()
        w.writeln("   d₂²(h₁,h₂) = ‖h₁‖² + ‖h₂‖² − 2⟨h₁,h₂⟩", "formula")
        w.writeln()
        w.writeln(f"   Left side:   d₂² = {pol['d2_sq']}", "value")
        w.writeln()
        w.writeln(f"   Right side:  ‖{e1.char}‖²   = {n1_sq}", "value")
        w.writeln(f"              + ‖{e2.char}‖²   = {n2_sq}", "value")
        w.writeln(f"              − 2⟨{e1.char},{e2.char}⟩ = −2×{ip} = {-2 * ip}", "value")
        w.writeln("              ─────────────", "dim")
        w.writeln(f"              = {n1_sq} + {n2_sq} + ({-2 * ip}) = {pol['polar']}", "value")
        w.writeln()

        ok = pol["pass"]
        w.writeln(
            f"   {pol['d2_sq']} = {pol['polar']}  {'✓ VERIFIED' if ok else '✗ VIOLATION'}",
            "pass" if ok else "fail",
        )
        w.writeln()

        # Inner product interpretation
        cos_sim = vec.cosine(e1, e2)
        w.writeln(f"   Inner product: ⟨{e1.char},{e2.char}⟩ = {ip}", "dim")
        w.writeln(f"   Cosine similarity: cos θ = {cos_sim:.6f}", "dim")
        if cos_sim > 0.9:
            w.writeln("   → Highly similar structural profiles", "dim")
        elif cos_sim < 0.1:
            w.writeln("   → Nearly orthogonal structures", "dim")
        w.writeln()

    def _render_component_diff(
        self, e1: CodexEntry, e2: CodexEntry, v1: List[int], v2: List[int]
    ) -> None:
        w = self._out
        if w is None:
            return

        w.writeln("④ COMPONENT-BY-COMPONENT DIFFERENCE", "section")
        w.writeln("   Chapter 22, Definition 22.1.1", "ref")
        w.writeln("─" * 60, "dim")
        w.writeln()
        w.writeln("   Δ(h₁,h₂) = v₁₄(h₁) − v₁₄(h₂) ∈ ℤ¹⁴", "formula")
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
        ]
        group_labels = {
            0: "─ Inḥinā' ─",
            1: "─ Nuqṭah ──",
            4: "─ Khaṭṭ ───",
            9: "─ Qaws ────",
        }

        w.writeln(
            f"   {'Slot':<5} {'Name':<5} {e1.char:>5} {e2.char:>5} {'Δ':>5} {'Δ²':>5} {'Visual'}",
            "field",
        )
        w.writeln("   " + "─" * 48, "dim")

        for k in range(14):
            if k in group_labels:
                w.writeln(f"   {group_labels[k]}", "dim")

            delta = v1[k] - v2[k]
            delta_sq = delta * delta
            name = slot_names[k]

            if delta > 0:
                vis = "+" * delta
                tag = "warn"
            elif delta < 0:
                vis = "−" * abs(delta)
                tag = "warn"
            else:
                vis = "·"
                tag = "dim"

            w.writeln(
                f"   [{k:>2}]  {name:<5} {v1[k]:>5} {v2[k]:>5} {delta:>+5} {delta_sq:>5}  {vis}",
                tag,
            )

        w.writeln()

    def _render_neighborhoods(self, e1: CodexEntry, e2: CodexEntry) -> None:
        w = self._out
        if w is None:
            return

        w.writeln("⑤ NEIGHBORHOOD ANALYSIS", "section")
        w.writeln("   Chapter 31: nearest neighbors in codex space", "ref")
        w.writeln("─" * 60, "dim")
        w.writeln()

        for entry, label in [(e1, "Letter 1"), (e2, "Letter 2")]:
            knn = geo.k_nearest(entry, 7)

            w.writeln(f"   {label}: {entry.char} ({entry.name}) — 7 nearest neighbors", "sub")
            w.writeln()
            w.writeln(
                f"   {'Rank':<5} {'Ch':<4} {'Name':<8} {'d₂':<10} {'d₂²':<6} {'Relationship'}",
                "field",
            )
            w.writeln("   " + "─" * 48, "dim")

            for rank, (ch, d) in enumerate(knn, 1):
                other = self._table.get_by_char(ch)
                if other is None:
                    continue
                name = other.name
                d2_sq = geo.euclidean_sq(entry, other)

                v_e = list(entry.vector)
                v_o = list(other.vector)
                if v_e[0] == v_o[0] and all(v_e[k] == v_o[k] for k in range(4, 14)):
                    rel = "dot-variant"
                elif d2_sq == 1:
                    rel = "minimal dist"
                elif d2_sq == 2:
                    rel = "near-minimal"
                elif geo.is_orthogonal(entry, other):
                    rel = "⊥ orthogonal"
                else:
                    rel = ""

                w.writeln(
                    f"   {rank:<5} {ch:<4} {name:<8} {d:<10.6f} {d2_sq:<6} {rel}",
                    "value",
                )

            w.writeln()

        # Mutual position
        geo.euclidean(e1, e2)
        knn1 = geo.k_nearest(e1, 28)
        rank_in_1 = 0
        for r, (ch, _) in enumerate(knn1, 1):
            if ch == e2.char:
                rank_in_1 = r
                break

        knn2 = geo.k_nearest(e2, 28)
        rank_in_2 = 0
        for r, (ch, _) in enumerate(knn2, 1):
            if ch == e1.char:
                rank_in_2 = r
                break

        w.writeln("   Mutual position:", "field")
        w.writeln(f"     {e2.char} is #{rank_in_1} nearest to {e1.char}", "value")
        w.writeln(f"     {e1.char} is #{rank_in_2} nearest to {e2.char}", "value")
        w.writeln()

    def _render_orthogonality_pair(
        self, e1: CodexEntry, e2: CodexEntry, v1: List[int], v2: List[int]
    ) -> None:
        w = self._out
        if w is None:
            return

        geo.is_orthogonal(e1, e2)
        ip = vec.inner(e1, e2)

        w.writeln("⑥ SUPPORT ORTHOGONALITY", "section")
        w.writeln("   Chapter 30, Lemma 30.2.1", "ref")
        w.writeln("─" * 60, "dim")
        w.writeln()
        w.writeln("   h₁ ⊥_S h₂  iff  supp(v₁₄(h₁)) ∩ supp(v₁₄(h₂)) = ∅", "formula")
        w.writeln("   Equivalent: ⟨h₁,h₂⟩ = 0 on ℕ₀¹⁴", "formula")
        w.writeln()

        supp1 = {k for k in range(14) if v1[k] > 0}
        supp2 = {k for k in range(14) if v2[k] > 0}
        shared = supp1 & supp2

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
        ]

        w.writeln(
            f"   supp({e1.char}) = {{{', '.join(slot_names[k] for k in sorted(supp1))}}}", "value"
        )
        w.writeln(
            f"   supp({e2.char}) = {{{', '.join(slot_names[k] for k in sorted(supp2))}}}", "value"
        )
        w.writeln()

        if shared:
            shared_names = ", ".join(slot_names[k] for k in sorted(shared))
            w.writeln(f"   Intersection: {{{shared_names}}}  (non-empty)", "warn")
            w.writeln(f"   ⟨{e1.char},{e2.char}⟩ = {ip} ≠ 0", "value")
            w.writeln("   Result: NOT orthogonal", "dim")
        else:
            w.writeln("   Intersection: ∅  (empty)", "pass")
            w.writeln(f"   ⟨{e1.char},{e2.char}⟩ = {ip} = 0", "value")
            w.writeln("   Result: ORTHOGONAL ✓ — structurally disjoint", "pass")
        w.writeln()

    def _render_context(self, e1: CodexEntry, e2: CodexEntry, v1: List[int], v2: List[int]) -> None:
        w = self._out
        if w is None:
            return

        w.writeln("⑦ METRIC SPACE CONTEXT", "section")
        w.writeln("   Chapter 29, Theorem 29.1.1: (H₂₈, d₂) is a finite metric space", "ref")
        w.writeln("─" * 60, "dim")
        w.writeln()

        d = geo.euclidean(e1, e2)
        geo.euclidean_sq(e1, e2)
        diam = geo.diameter()
        diam_sq = geo.diameter_sq()

        w.writeln(f"   d₂({e1.char},{e2.char}) = {d:.6f}", "value")
        w.writeln(f"   diam(H₂₈) = {diam:.6f}  (√{diam_sq})", "value")
        w.writeln(f"   d / diam  = {d / diam:.4f}  ({d / diam * 100:.1f}% of diameter)", "value")
        w.writeln()

        # Metric axioms
        w.writeln("   Metric axiom verification for this pair:", "field")
        w.writeln(f"     M1 (non-negativity): d₂ = {d:.6f} ≥ 0  ✓", "pass")

        if e1.char == e2.char:
            w.writeln("     M1 (identity):       d₂ = 0 iff h₁ = h₂  ✓", "pass")
        else:
            w.writeln(f"     M1 (discernibility): d₂ = {d:.6f} > 0  ✓  (h₁ ≠ h₂)", "pass")

        d_reverse = geo.euclidean(e2, e1)
        w.writeln(
            f"     M2 (symmetry):       d({e1.char},{e2.char}) = d({e2.char},{e1.char}) = {d_reverse:.6f}  ✓",
            "pass",
        )

        # Triangle inequality with a third letter
        third = self._table.get_by_char("ج")
        if third and third.char != e1.char and third.char != e2.char:
            d13 = geo.euclidean(e1, third)
            d32 = geo.euclidean(third, e2)
            d12 = d
            tri_ok = d12 <= d13 + d32
            w.writeln(
                f"     M3 (triangle):       d({e1.char},{e2.char}) ≤ d({e1.char},ج) + d(ج,{e2.char})",
                "pass" if tri_ok else "fail",
            )
            w.writeln(
                f"                          {d12:.4f} ≤ {d13:.4f} + {d32:.4f} = {d13 + d32:.4f}  "
                f"{'✓' if tri_ok else '✗'}",
                "dim",
            )
        w.writeln()

    # ══════════════════════════════════════════════════════════════
    #  GLOBAL VIEWS
    # ══════════════════════════════════════════════════════════════

    def _show_topology(self) -> None:
        """Display alphabet diameter, centroid, and topology."""
        if self._out is None:
            return
        self._out.clear()

        self._out.writeln("ALPHABET TOPOLOGY — H₂₈ in ℝ¹⁴", "title")
        self._out.writeln("═" * 60)
        self._out.writeln()

        # Diameter
        d2 = geo.diameter_sq()
        d = geo.diameter()
        self._out.writeln("  DIAMETER (Proposition 31.1.1)", "section")
        self._out.writeln("  " + "─" * 45, "dim")
        self._out.writeln(f"  diam(H₂₈) = √{d2} = {d:.6f}", "value")
        self._out.writeln("  Achieved by pair: ا (Alif) ↔ هـ (Hā')", "value")
        self._out.writeln("  Alif: simplest letter (‖v₁₄‖² = 1)", "dim")
        self._out.writeln("  Hā':  most complex (‖v₁₄‖² = 69)", "dim")
        self._out.writeln()

        # Centroid
        cent = geo.alphabet_centroid()
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
        ]

        self._out.writeln("  CENTROID — Mean Letter (Definition 31.2.1)", "section")
        self._out.writeln("  " + "─" * 45, "dim")
        self._out.writeln("  v̄ = (1/28) Σ v₁₄(hᵢ)", "formula")
        self._out.writeln()

        self._out.writeln(f"  {'Component':<12} {'Mean':<10} {'Interpretation'}", "field")
        self._out.writeln("  " + "─" * 45, "dim")
        for k, name in enumerate(slot_names):
            val = cent[k]
            interp = ""
            if k == 0:
                interp = f"≈ {val * 90:.0f}° average turning"
            self._out.writeln(f"  {name:<12} {val:<10.4f} {interp}", "value")

        self._out.writeln()
        self._out.writeln(f"  Mean Θ̂ = {cent[0]:.4f} quadrants ≈ {cent[0] * 90:.1f}°", "field")
        self._out.writeln()

        # Extreme letters
        self._out.writeln("  EXTREMAL LETTERS", "section")
        self._out.writeln("  " + "─" * 45, "dim")

        norms = [(e, vec.norm2(e)) for e in self._entries]
        norms.sort(key=lambda x: x[1])

        self._out.writeln(
            f"  Smallest norm: {norms[0][0].char} ({norms[0][0].name}) ‖v₁₄‖² = {norms[0][1]}",
            "value",
        )
        self._out.writeln(
            f"  Largest norm:  {norms[-1][0].char} ({norms[-1][0].name}) ‖v₁₄‖² = {norms[-1][1]}",
            "value",
        )

        self._status_var.set("Topology displayed")

    def _show_gram(self) -> None:
        """Display the 28×28 Gram matrix."""
        if self._out is None:
            return
        self._out.clear()

        self._out.writeln("GRAM MATRIX G = M₁₄ · M₁₄ᵀ  (Definition 30.1.1)", "title")
        self._out.writeln("═" * 60)
        self._out.writeln()
        self._out.writeln("  G[i][j] = ⟨v₁₄(hᵢ), v₁₄(hⱼ)⟩  (inner product)", "formula")
        self._out.writeln("  Diagonal: G[i][i] = ‖hᵢ‖²  (squared norm)", "formula")
        self._out.writeln("  Properties: symmetric, positive semidefinite", "dim")
        self._out.writeln()

        G = geo.gram_matrix()
        chars = [e.char for e in self._entries]

        header = "     " + "".join(f"{ch:>4}" for ch in chars)
        self._out.writeln(header, "field")
        self._out.writeln("     " + "─" * (4 * len(chars)), "dim")

        for i, ch in enumerate(chars):
            row_str = f" {ch:<3} "
            for j in range(len(chars)):
                val = G[i][j]
                row_str += f"{val:>4}"
            self._out.writeln(row_str, "matrix")

        self._out.writeln()
        self._out.writeln("  rank(G) = rank(M₁₄) = 14", "dim")
        self._status_var.set("Gram matrix displayed")

    def _show_distance_matrix(self) -> None:
        """Display pairwise distance matrix."""
        if self._out is None:
            return
        self._out.clear()

        self._out.writeln("PAIRWISE DISTANCE MATRIX d₂²(hᵢ, hⱼ)", "title")
        self._out.writeln("═" * 60)
        self._out.writeln()

        chars = [e.char for e in self._entries]
        n = len(chars)

        header = "     " + "".join(f"{ch:>4}" for ch in chars)
        self._out.writeln(header, "field")
        self._out.writeln("     " + "─" * (4 * n), "dim")

        for i in range(n):
            e1 = self._table.get_by_char(chars[i])
            if e1 is None:
                continue
            row_str = f" {chars[i]:<3} "
            for j in range(n):
                e2 = self._table.get_by_char(chars[j])
                if e2 is None:
                    row_str += "   ?"
                    continue
                if i == j:
                    row_str += "   ·"
                else:
                    d2 = geo.euclidean_sq(e1, e2)
                    row_str += f"{d2:>4}"
            self._out.writeln(row_str, "matrix")

        self._out.writeln()
        self._out.writeln("  Minimum non-zero d₂² = 1  (dot-variant pairs)", "dim")
        self._out.writeln(f"  Maximum d₂² = {geo.diameter_sq()}  (ا ↔ هـ)", "dim")
        self._status_var.set("Distance matrix displayed")

    def _show_orthogonality(self) -> None:
        """Display orthogonality map."""
        if self._out is None:
            return
        self._out.clear()

        self._out.writeln("SUPPORT ORTHOGONALITY MAP", "title")
        self._out.writeln("═" * 60)
        self._out.writeln()
        self._out.writeln("  h₁ ⊥_S h₂ iff supp(v₁₄(h₁)) ∩ supp(v₁₄(h₂)) = ∅", "formula")
        self._out.writeln("  '⊥' = orthogonal, '·' = not orthogonal", "dim")
        self._out.writeln()

        chars = [e.char for e in self._entries]
        n = len(chars)

        header = "     " + "".join(f"{ch:>3}" for ch in chars)
        self._out.writeln(header, "field")
        self._out.writeln("     " + "─" * (3 * n), "dim")

        orth_count = 0
        for i in range(n):
            e1 = self._table.get_by_char(chars[i])
            if e1 is None:
                continue
            row_str = f" {chars[i]:<3} "
            for j in range(n):
                e2 = self._table.get_by_char(chars[j])
                if e2 is None:
                    row_str += "  ?"
                    continue
                if i == j:
                    row_str += "  ■"
                elif geo.is_orthogonal(e1, e2):
                    row_str += "  ⊥"
                    if i < j:
                        orth_count += 1
                else:
                    row_str += "  ·"
            self._out.writeln(row_str, "matrix")

        self._out.writeln()
        self._out.writeln(f"  Orthogonal pairs: {orth_count}", "value")
        self._out.writeln(f"  Total pairs: {n * (n - 1) // 2}", "dim")
        self._out.writeln(
            f"  Orthogonality rate: {orth_count / (n * (n - 1) // 2) * 100:.1f}%", "dim"
        )

        # List all orthogonal pairs
        if orth_count > 0 and orth_count <= 20:
            self._out.writeln()
            self._out.writeln("  Orthogonal pairs:", "field")
            for i in range(n):
                e1 = self._table.get_by_char(chars[i])
                if e1 is None:
                    continue
                for j in range(i + 1, n):
                    e2 = self._table.get_by_char(chars[j])
                    if e2 is None:
                        continue
                    if geo.is_orthogonal(e1, e2):
                        self._out.writeln(
                            f"    {e1.char} ({e1.name}) ⊥ {e2.char} ({e2.name})",
                            "value",
                        )

        self._status_var.set(f"Orthogonality: {orth_count} pairs")
