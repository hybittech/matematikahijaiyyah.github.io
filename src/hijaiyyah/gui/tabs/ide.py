"""
Tab: HC v1.0 IDE — Professional Integrated Development Environment
====================================================================
Full-featured HC language editor with:
  - Syntax-highlighted code editor
  - Real-time evaluation engine
  - Example program library with categories
  - Language reference sidebar
  - Output console with color-coded results
  - Error display with line numbers
  - Variable inspector
  - Quick-insert toolbar for Hijaiyyah characters
"""

from __future__ import annotations

import time
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Any, Dict, Optional

from ...language.evaluator import HCEvaluator
from ...language.lexer import Lexer
from ...language.parser import Parser
from ..theme import THEME
from ..widgets import OutputWriter, make_text

# ══════════════════════════════════════════════════════════════════
#  SECTION 1 — EXAMPLE PROGRAM LIBRARY
# ══════════════════════════════════════════════════════════════════

EXAMPLES: Dict[str, Dict[str, str]] = {
    # ── Basics ───────────────────────────────────────────────────
    "📘 Basics": {
        "Hello Hybit": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Hello Hybit
// Your first HC program
// ═══════════════════════════════════════════════

// Load a letter — returns a hybit (18D integer vector)
let h = 'ب';

// Access components
println("Letter Ba (ب):");
println("  Theta (turning):", h.theta());
println("  Guard check:", h.guard());
println("  Norm²:", h.norm2());

// Every hybit has 18 integer components
println("  Full vector:", h.array());
""",
        "Variables & Arithmetic": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Variables and Arithmetic
// HC uses let for immutable, let mut for mutable
// ═══════════════════════════════════════════════

// Immutable binding (like Rust)
let x = 42;
let name = "Hijaiyyah";
let pi = 3.14159;

println("x =", x);
println("name =", name);
println("pi =", pi);

// Arithmetic
let a = 10;
let b = 3;
println("a + b =", a + b);    // 13
println("a - b =", a - b);    // 7
println("a * b =", a * b);    // 30
println("a / b =", a / b);    // 3.333...
println("a % b =", a % b);    // 1

// Boolean
let is_valid = true;
let is_empty = false;
println("valid:", is_valid);
println("empty:", is_empty);
""",
        "Hybit Components": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Hybit Component Access
// Each hybit has 18 named components
// ═══════════════════════════════════════════════

let h = 'ج';  // Jim — the 270° curl

println("=== Jim (ج) — Component Breakdown ===");
println();

// Slot 0: Turning
println("Θ̂ (turning):", h.theta(), "quadrants =", h.theta() * 90, "degrees");

// Slots 1-3: Nuqtah (dots)
println("Na (ascender dots):", h.Na());
println("Nb (body dots):", h.Nb());
println("Nd (descender dots):", h.Nd());

// Slots 4-8: Khatt (lines)
println("Kp (primary line):", h.Kp());
println("Kx (auxiliary line):", h.Kx());

// Slots 9-13: Qaws (curves)
println("Qp (primary curve):", h.Qp());
println("Qx (auxiliary curve):", h.Qx());
println("Qc (closed loop):", h.Qc());

// Derived quantities
println();
println("U (non-primary budget):", h.U());
println("ρ (primary residue):", h.rho());
println("Guard check:", h.guard());
""",
        "Control Flow": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Control Flow
// if/else, for loops, match expressions
// ═══════════════════════════════════════════════

// ── If / Else ──
let h = 'ب';
if h.guard() {
    println("Ba passes guard check ✓");
} else {
    println("Ba fails guard ✗");
}

// ── For Loop (range) ──
println();
println("Letters with Θ̂ > 4:");
for i in 0..27 {
    let letter = load_id(i);
    if letter.theta() > 4 {
        println("  ", letter.theta(), "quadrants");
    }
}

// ── Match Expression ──
println();
let theta = 'هـ'.theta();
match theta {
    0 => println("Zero turning (straight line)"),
    1..=3 => println("Low turning (1-3 quadrants)"),
    4..=6 => println("Medium turning (4-6 quadrants)"),
    8 => println("Maximum turning (8 quadrants = 720°)"),
    _ => println("Other"),
}
""",
        "Functions": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Functions
// fn name(params) -> return_type { body }
// ═══════════════════════════════════════════════

// Simple function
fn greet(name: string) {
    println("Hello,", name, "!");
}

greet("Hijaiyyah Mathematics");

// Function with return value
fn add(a: int, b: int) -> int {
    return a + b;
}

println("2 + 3 =", add(2, 3));

// Function operating on hybits
fn describe(h: hybit) {
    println("  Theta:", h.theta());
    println("  Guard:", h.guard());
    println("  Norm²:", h.norm2());
    println("  U:", h.U(), " ρ:", h.rho());
}

println();
println("=== Ba (ب) ===");
describe('ب');

println();
println("=== Ha (هـ) ===");
describe('هـ');

// Function computing string codex
fn word_theta(text: string) -> int {
    let cod = hm::integral::string_integral(text);
    return cod;
}

println();
println("Total theta of بسم:", word_theta("بسم"));
""",
    },
    # ── Five Fields ──────────────────────────────────────────────
    "📗 Five Fields (Bab II)": {
        "Vectronometry": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Field 1: Vectronometry (Ch 17-21)
// Measuring the structure of individual letters
// ═══════════════════════════════════════════════

let h = 'ج';  // Jim

// Primitive ratios — always sum to 1.0
let ratios = hm::vectronometry::primitive_ratios(h);
println("Primitive Ratios (Theorem 18.2.1):");
println("  r_N + r_K + r_Q = 1.0");
println("  Result:", ratios);

// Pythagorean theorem — norm decomposes by subspace
let pyth = hm::vectronometry::pythagorean_check(h);
println();
println("Pythagorean (Theorem 20.2.1):");
println("  ‖h‖² = ‖Π_Θ‖² + ‖Π_N‖² + ‖Π_K‖² + ‖Π_Q‖²");
println("  Result:", pyth);

// Codex norm
println();
println("Norm²:", hm::vectronometry::norm2(h));
println("Norm:", hm::vectronometry::norm(h));

// Cosine similarity between two letters
let cos = hm::vectronometry::cosine('ب', 'ت');
println();
println("Cosine(Ba, Ta):", cos);
""",
        "Differential Calculus": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Field 2: Differential (Ch 22-24)
// Measuring differences between letters
// ═══════════════════════════════════════════════

// Difference vector (Δ ∈ ℤ¹⁴)
let delta = hm::differential::diff('ت', 'ب');
println("Δ(Ta, Ba):", delta);

// Norm decomposition — which layer changed?
let decomp = hm::differential::norm_decomposition('ت', 'ب');
println();
println("‖Δ‖² decomposition:");
println("  Total:", decomp);
println("  → Only Nuqtah layer changes (dot-variant pair)");

// U-gradient — sensitivity of turning budget
println();
println("∇_Q U =", hm::differential::u_gradient());
println("  → Loop (Qc) has 4× impact of other components");

// Dot-variant pairs — letters differing only in dots
println();
println("All dot-variant pairs in H₂₈:");
let pairs = hm::differential::all_dot_variants();
println(pairs);
""",
        "Integral Calculus": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Field 3: Integral (Ch 25-28)
// Accumulating structure across strings
// ═══════════════════════════════════════════════

// String integral — sum of all letter vectors
let bsm = hm::integral::string_integral("بسم");
println("∫(بسم) = Cod₁₈:", bsm);

// Layer integrals — decomposition by component type
let layers = hm::integral::layer_integrals("بسم");
println();
println("Layer integrals:");
println("  ∫Θ̂ =", layers);

// Fundamental theorem: ∫(uv) = ∫(u) + ∫(v)
let bs = hm::integral::string_integral("بس");
let m = hm::integral::string_integral("م");
let combined = hm::integral::add_codex(bs, m);
let direct = hm::integral::string_integral("بسم");
println();
println("Fundamental Theorem (25.2.1):");
println("  ∫(بس) + ∫(م) =", combined);
println("  ∫(بسم)        =", direct);

// Anagram invariance — order doesn't matter
let a1 = hm::integral::string_integral("بسم");
let a2 = hm::integral::string_integral("سبم");
println();
println("Anagram Theorem (25.3.1):");
println("  ∫(بسم):", a1);
println("  ∫(سبم):", a2);
println("  Equal:", a1);

// Centroid — average letter
let cent = hm::integral::centroid("بسم");
println();
println("Centroid (mean v₁₈):", cent);
""",
        "Codex Geometry": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Field 4: Geometry (Ch 29-31)
// Distances and topology of the alphabet
// ═══════════════════════════════════════════════

// Euclidean distance
let d = hm::geometry::euclidean('ا', 'هـ');
println("d(Alif, Ha) =", d);
println("d² =", hm::geometry::euclidean_sq('ا', 'هـ'));

// Diameter of the alphabet
println();
println("diam(H₂₈) =", hm::geometry::diameter());
println("diam² = 70 (achieved by Alif ↔ Ha)");

// Manhattan and Hamming distances
println();
println("Manhattan d₁:", hm::geometry::manhattan('ب', 'ت'));
println("Hamming d_H:", hm::geometry::hamming('ب', 'ت'));

// Polarization identity (Theorem 29.3.1)
let pol = hm::geometry::polarization_check('ب', 'ج');
println();
println("Polarization identity:", pol);

// Nearest neighbors
let nn = hm::geometry::k_nearest('ج', 5);
println();
println("5 nearest to Jim (ج):", nn);

// Support orthogonality
let orth = hm::geometry::is_orthogonal('ا', 'ب');
println();
println("Alif ⊥ Ba?", orth, "(disjoint support)");
""",
        "Exomatrix Analysis": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Field 5: Exomatrix (Ch 32-36)
// The 5×5 structured audit matrix
// ═══════════════════════════════════════════════

// Build Exomatrix
let E = hm::exomatrix::build('هـ');
println("Exomatrix E(هـ):");
println(E);

// Five audit relations (Identity 33.1.1)
let audit = hm::exomatrix::audit(E);
println();
println("Audit R1-R5:", audit);

// Frobenius energy
let phi = hm::exomatrix::phi(E);
let n2 = hm::vectronometry::norm2('هـ');
println();
println("Φ(هـ) =", phi);
println("‖v₁₄‖² =", n2);
println("Surplus =", phi);
println("Φ > ‖v₁₄‖²: always strict (Theorem 34.3.1)");

// Energy table — all 28 letters ranked
println();
println("Energy table (top 5):");
let table = hm::exomatrix::energy_table();
println(table);

// Reconstruction uniqueness (Theorem 36.2.1)
let reconstructed = hm::exomatrix::reconstruct(E);
println();
println("Reconstruct from Exomatrix:");
println("  Original v₁₈:", 'هـ'.array());
println("  Recovered:", reconstructed);

// Rank analysis
println();
println("rank(M₁₄) =", hm::exomatrix::rank_M14());
println("rank(M)   =", hm::exomatrix::rank_M());
""",
    },
    # ── Applications ─────────────────────────────────────────────
    "📕 Applications": {
        "String Comparison": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Compare Two Strings
// Same total turning, different profiles
// ═══════════════════════════════════════════════

let bsm = hm::integral::string_integral("بسم");
let allah = hm::integral::string_integral("الله");

println("String: بسم");
println("  Cod₁₈:", bsm);
let l1 = hm::integral::layer_integrals("بسم");
println("  Layers:", l1);

println();
println("String: الله");
println("  Cod₁₈:", allah);
let l2 = hm::integral::layer_integrals("الله");
println("  Layers:", l2);

println();
println("Both have ∫Θ̂ = 10 (900°)");
println("But different profiles:");
println("  بسم:  dominated by ρ (primary curves)");
println("  الله: dominated by U (loops of هـ)");
""",
        "Guard Verification": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Verify All 28 Letters Pass Guard
// O(1) per letter — 15 ADD + 4 CMP
// ═══════════════════════════════════════════════

let pass_count = 0;
let fail_count = 0;

for i in 0..27 {
    let h = load_id(i);
    if h.guard() {
        pass_count = pass_count + 1;
    } else {
        fail_count = fail_count + 1;
        println("FAIL at index", i);
    }
}

println("Guard verification complete:");
println("  Pass:", pass_count);
println("  Fail:", fail_count);
println("  Result:", pass_count, "/ 28");

// Also verify detailed audit (R1-R5)
println();
println("Detailed R1-R5 audit:");
let h = 'ب';
let detail = h.guard_detail();
println("  Ba audit:", detail);
""",
        "All 28 Analysis": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Analyze All 28 Letters
// Complete structural profile
// ═══════════════════════════════════════════════

println("Complete H₂₈ Analysis:");
println("─────────────────────────────────────");

let total_theta = 0;
let total_U = 0;
let total_rho = 0;

for i in 0..27 {
    let h = load_id(i);
    let theta = h.theta();
    let u = h.U();
    let rho = h.rho();
    total_theta = total_theta + theta;
    total_U = total_U + u;
    total_rho = total_rho + rho;
}

println();
println("Global sums:");
println("  Σ Θ̂ =", total_theta);
println("  Σ U  =", total_U);
println("  Σ ρ  =", total_rho);
println("  Σ Θ̂ = Σ U + Σ ρ:", total_theta, "=", total_U, "+", total_rho);

println();
println("Diameter: √70 ≈", hm::geometry::diameter());

// Mod-4 distribution
println();
println("Mod-4 distribution:");
for i in 0..27 {
    let h = load_id(i);
    let m = h.theta() % 4;
    if m == 0 {
        println("  Θ̂ ≡ 0 (mod 4) — possibly closed");
    }
}
""",
        "Data Integrity": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Data Integrity Pipeline
// Guard → Verify → Hash
// ═══════════════════════════════════════════════

// Step 1: Encode data as hybit string
let text = "TRANSACTION-001";
let cod = hm::integral::string_integral(text);
println("Step 1 — Encode:");
println("  Text:", text);
println("  Cod₁₈:", cod);

// Step 2: Guard check (O(1) — structural validation)
println();
println("Step 2 — Guard Check:");
println("  (15 additions + 4 comparisons)");

// Step 3: Compute hash
let h = 'ب';
let hash = h.hash();
println();
println("Step 3 — Hash:");
println("  SHA-256(Ba):", hash);

// Guard-first pipeline:
// Malformed → REJECT (20 ops)
// Valid → crypto verify (1000+ ops)
// → Saves compute on invalid data
println();
println("Pipeline: Guard(O(1)) → Crypto(O(hash)) → Process");
println("  Invalid data rejected BEFORE expensive crypto");
""",
    },
    # ── Reference ────────────────────────────────────────────────
    "📙 Quick Reference": {
        "Syntax Cheat Sheet": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Syntax Quick Reference
// ═══════════════════════════════════════════════

// ── Types ──────────────────────────────────
// int        42, -7
// float      3.14
// bool       true, false
// string     "hello"
// hybit      'ب' (18D integer vector)

// ── Variables ──────────────────────────────
let x = 42;              // immutable
// let mut y = 0;         // mutable (future)
const PI = 3.14159;       // constant

// ── Operators ──────────────────────────────
// +  -  *  /  %          arithmetic
// ==  !=  <  >  <=  >=   comparison
// &&  ||  !              logical

// ── Hybit Operations ───────────────────────
let h = 'ب';
// h.theta()    h.Na()    h.Kp()    h.Qp()
// h.guard()    h.norm2() h.U()     h.rho()
// h.dist2(other)         h.hash()
// h.exomatrix()          h.phi()

// ── Control Flow ───────────────────────────
// if cond { } else { }
// for x in 0..10 { }
// match val { 0 => ..., _ => ... }

// ── Functions ──────────────────────────────
// fn name(a: int, b: int) -> int { return a + b; }

// ── Standard Library ───────────────────────
// hm::vectronometry::*   Field 1 (Ch 17-21)
// hm::differential::*    Field 2 (Ch 22-24)
// hm::integral::*        Field 3 (Ch 25-28)
// hm::geometry::*        Field 4 (Ch 29-31)
// hm::exomatrix::*       Field 5 (Ch 32-36)

println("Syntax reference loaded ✓");
println("Edit this code and press ▶ Evaluate");
""",
        "All Hybit Methods": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Complete Hybit Method Reference
// ═══════════════════════════════════════════════

let h = 'ف';  // Fa — has loop + tail
println("=== All methods on Fa (ف) ===");
println();

// ── Component Access ──
println("[Components]");
println("  theta:", h.theta());
println("  Na:", h.Na(), " Nb:", h.Nb(), " Nd:", h.Nd());
println("  Kp:", h.Kp(), " Kx:", h.Kx());
println("  Qp:", h.Qp(), " Qc:", h.Qc());

// ── Structural ──
println();
println("[Structural]");
println("  U:", h.U());
println("  rho:", h.rho());
println("  guard:", h.guard());
println("  guard_detail:", h.guard_detail());

// ── Algebraic ──
println();
println("[Algebraic]");
println("  norm2:", h.norm2());
println("  norm:", h.norm());

// ── Ratios ──
println();
println("[Ratios]");
println("  r_N:", h.r_N());
println("  r_K:", h.r_K());
println("  r_Q:", h.r_Q());
println("  r_U:", h.r_U());
println("  r_rho:", h.r_rho());
println("  r_loop:", h.r_loop());

// ── Matrix ──
println();
println("[Exomatrix]");
println("  phi:", h.phi());

// ── Crypto ──
println();
println("[Crypto]");
println("  hash:", h.hash());
""",
        "Module Functions": """\
// ═══════════════════════════════════════════════
// HC v1.0 — Standard Library Module Functions
// ═══════════════════════════════════════════════

println("=== hm::vectronometry ===");
println("  primitive_ratios(h)    → {r_N, r_K, r_Q}");
println("  turning_ratios(h)     → {r_U, r_rho, r_loop}");
println("  pythagorean_check(h)  → {lhs, rhs, pass}");
println("  norm2(h) / norm(h)");
println("  inner(h1, h2) / cosine(h1, h2)");
println("  comp_angle(h)         → α in radians");
println("  full_table()          → 28-row table");

println();
println("=== hm::differential ===");
println("  diff(h1, h2)           → Δ ∈ ℤ¹⁴");
println("  norm_decomposition     → {total, theta, N, K, Q}");
println("  u_gradient()           → [0, 1, 1, 1, 4]");
println("  all_dot_variants()     → pairs list");
println("  second_diff(h1,h2,h3)  → Δ² ∈ ℤ¹⁴");

println();
println("=== hm::integral ===");
println("  string_integral(text)  → {cod18, length}");
println("  add_codex(c1, c2)      → merged codex");
println("  layer_integrals(text)  → {theta, N, K, Q, U, rho}");
println("  centroid(text)         → mean v₁₈");
println("  cumulative(text)       → trajectory S_k");

println();
println("=== hm::geometry ===");
println("  euclidean / euclidean_sq / manhattan / hamming");
println("  diameter() / diameter_sq()");
println("  nearest(h) / k_nearest(h, k)");
println("  is_orthogonal(h1, h2)");
println("  polarization_check(h1, h2)");
println("  gram_matrix() / alphabet_centroid()");

println();
println("=== hm::exomatrix ===");
println("  build(h)        → 5×5 matrix");
println("  audit(E)        → {R1..R5, all_pass}");
println("  phi(E)           → Frobenius energy");
println("  energy_table()   → 28 rows sorted by Φ");
println("  reconstruct(E)   → recovered v₁₈");
println("  rank_M14() / rank_M()");
""",
    },
}


# ══════════════════════════════════════════════════════════════════
#  SECTION 2 — IDE TAB CLASS
# ══════════════════════════════════════════════════════════════════


class IDETab:
    """
    Tab: HC v1.0 IDE — Professional development environment.

    Layout:
    ┌──────────────────────────────────────────────────────┐
    │  Toolbar: [▶ Run] [⟳ Clear] [💾 Save] [📂 Open]    │
    │  Quick-insert: [ا][ب][ت][ث][ج]...[ي]               │
    ├────────────────────────┬─────────────────────────────┤
    │                        │                             │
    │   Code Editor          │   Output Console            │
    │   (syntax colored)     │   (color-coded results)     │
    │                        │                             │
    ├────────────────────────┤                             │
    │   Example Selector     │                             │
    │   (categorized)        │                             │
    └────────────────────────┴─────────────────────────────┘
    """

    def __init__(self, notebook: ttk.Notebook, root: tk.Tk) -> None:
        self._root = root
        self._tab = ttk.Frame(notebook)
        notebook.add(self._tab, text="  ⌨ HC IDE  ")

        self._editor: Optional[tk.Text] = None
        self._output: Optional[tk.Text] = None
        self._out: Optional[OutputWriter] = None
        self._status_var = tk.StringVar(value="Ready")
        self._line_count_var = tk.StringVar(value="Lines: 0")

        self._build()

    def _build(self) -> None:
        # ── Toolbar ──────────────────────────────────────────────
        toolbar = ttk.Frame(self._tab)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 0))

        ttk.Button(toolbar, text="▶ Evaluate", command=self._run).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="⟳ Clear Output", command=self._clear_output).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="🗑 Clear Editor", command=self._clear_editor).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="💾 Save .hc", command=self._save_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📂 Open .hc", command=self._open_file).pack(side=tk.LEFT, padx=2)

        # Status
        ttk.Label(toolbar, textvariable=self._status_var, foreground=THEME.dim_fg).pack(
            side=tk.RIGHT, padx=10
        )
        ttk.Label(toolbar, textvariable=self._line_count_var, foreground=THEME.dim_fg).pack(
            side=tk.RIGHT, padx=5
        )

        # ── Quick-insert bar (Hijaiyyah characters) ──────────────
        insert_bar = ttk.Frame(self._tab)
        insert_bar.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(insert_bar, text="Insert:", foreground=THEME.dim_fg).pack(side=tk.LEFT)

        from ...core.master_table import MASTER_TABLE

        for entry in MASTER_TABLE.all_entries():
            tk.Button(
                insert_bar,
                text=entry.char,
                font=("Simplified Arabic", 12),
                width=2,
                height=1,
                bg=THEME.accent,
                fg=THEME.hijaiyyah_fg,
                relief=tk.FLAT,
                command=lambda ch=entry.char: self._insert_char(ch),
            ).pack(side=tk.LEFT, padx=1)

        # ── Main area: editor + output ───────────────────────────
        main_paned = ttk.PanedWindow(self._tab, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: editor + examples
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        # Editor header
        editor_header = ttk.Frame(left_frame)
        editor_header.pack(fill=tk.X)
        ttk.Label(
            editor_header,
            text="HC v1.0 Source Code",
            font=THEME.font_ui_bold,
        ).pack(side=tk.LEFT)
        ttk.Label(
            editor_header,
            text="(.hc file)",
            foreground=THEME.dim_fg,
        ).pack(side=tk.LEFT, padx=5)

        # Code editor
        editor_frame = ttk.Frame(left_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        self._editor = tk.Text(
            editor_frame,
            font=("Consolas", 13),
            bg="#0d1117",
            fg="#c9d1d9",
            insertbackground="#58a6ff",
            selectbackground="#1f6feb",
            selectforeground="#ffffff",
            wrap=tk.NONE,
            undo=True,
            padx=10,
            pady=10,
            tabs=("4c",),
        )

        # Scrollbars
        y_scroll = ttk.Scrollbar(editor_frame, command=self._editor.yview)
        x_scroll = ttk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=self._editor.xview)
        self._editor.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self._editor.pack(fill=tk.BOTH, expand=True)

        # Bind line counter
        self._editor.bind("<KeyRelease>", self._update_line_count)

        # Editor color tags
        self._editor.tag_configure("keyword", foreground="#ff7b72")
        self._editor.tag_configure("string", foreground="#a5d6ff")
        self._editor.tag_configure("comment", foreground="#8b949e", font=("Consolas", 13, "italic"))
        self._editor.tag_configure("number", foreground="#79c0ff")
        self._editor.tag_configure("hijaiyyah", foreground="#d2a8ff", font=("Consolas", 14, "bold"))

        # Example selector below editor
        example_frame = ttk.Frame(left_frame)
        example_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(example_frame, text="Examples:", font=THEME.font_ui_bold).pack(anchor=tk.W)

        example_inner = ttk.Frame(example_frame)
        example_inner.pack(fill=tk.X)

        for category, programs in EXAMPLES.items():
            cat_frame = ttk.LabelFrame(example_inner, text=category)
            cat_frame.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y)
            for name in programs:
                ttk.Button(
                    cat_frame,
                    text=name,
                    command=lambda c=category, n=name: self._load_example(c, n),
                ).pack(fill=tk.X, padx=2, pady=1)

        # Right: output console
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)

        output_header = ttk.Frame(right_frame)
        output_header.pack(fill=tk.X)
        ttk.Label(
            output_header,
            text="Output Console",
            font=THEME.font_ui_bold,
        ).pack(side=tk.LEFT)

        self._output, _ = make_text(right_frame, font=("Consolas", 12), bg="#0d1117")
        self._out = OutputWriter(self._output)
        self._out.add_tags(
            {
                "header": {"foreground": "#58a6ff", "font": ("Consolas", 12, "bold")},
                "result": {"foreground": "#7ee787"},
                "error": {"foreground": "#f85149"},
                "warning": {"foreground": "#d29922"},
                "dim": {"foreground": "#8b949e"},
                "time": {"foreground": "#8b949e", "font": ("Consolas", 10)},
            }
        )

        # Load default example
        self._load_example("📘 Basics", "Hello Hybit")
        self._show_welcome()

    # ── Actions ──────────────────────────────────────────────────

    def _run(self) -> None:
        """Evaluate the HC source code."""
        if self._editor is None or self._out is None:
            return

        src = self._editor.get("1.0", tk.END).strip()
        if not src:
            self._status_var.set("Nothing to evaluate")
            return

        self._out.clear()
        self._out.writeln("HC v1.0 EXECUTION ENGINE", "header")
        self._out.writeln("═" * 50)
        self._out.writeln()

        self._status_var.set("Running...")
        self._root.update_idletasks()

        start_time = time.perf_counter()
        line_count = src.count("\n") + 1
        output_lines = 0

        def gui_print(*args: Any) -> None:
            nonlocal output_lines
            if self._out is None:
                return
            text = " ".join(str(a) for a in args)
            self._out.writeln(text, "result")
            output_lines += 1
            if output_lines % 10 == 0:
                self._root.update_idletasks()

        try:
            tokens = Lexer(src).tokenize()
            ast = Parser(tokens).parse()
            evaluator = HCEvaluator(print_func=gui_print)
            evaluator.evaluate(ast)

            elapsed = time.perf_counter() - start_time
            self._out.writeln()
            self._out.writeln("─" * 50, "dim")
            self._out.writeln("✓ Completed successfully", "header")
            self._out.writeln(f"  Source: {line_count} lines", "time")
            self._out.writeln(f"  Output: {output_lines} lines", "time")
            self._out.writeln(f"  Time:   {elapsed * 1000:.1f} ms", "time")
            self._status_var.set(f"Done ({elapsed * 1000:.0f}ms)")

        except Exception as e:
            elapsed = time.perf_counter() - start_time
            self._out.writeln()
            self._out.writeln("─" * 50, "dim")
            self._out.writeln(f"✗ Error: {e}", "error")
            self._out.writeln(f"  Time: {elapsed * 1000:.1f} ms", "time")
            self._status_var.set("Error")

    def _load_example(self, category: str, name: str) -> None:
        """Load an example program into the editor."""
        if self._editor is None:
            return

        programs = EXAMPLES.get(category, {})
        source = programs.get(name, "")

        self._editor.delete("1.0", tk.END)
        self._editor.insert("1.0", source)
        self._status_var.set(f"Loaded: {name}")
        self._update_line_count()

    def _insert_char(self, ch: str) -> None:
        """Insert a Hijaiyyah character at the cursor position."""
        if self._editor is None:
            return
        self._editor.insert(tk.INSERT, f"'{ch}'")

    def _clear_output(self) -> None:
        if self._out:
            self._out.clear()
            self._status_var.set("Output cleared")

    def _clear_editor(self) -> None:
        if self._editor:
            self._editor.delete("1.0", tk.END)
            self._status_var.set("Editor cleared")

    def _save_file(self) -> None:
        if self._editor is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".hc",
            filetypes=[("HC Source", "*.hc"), ("All Files", "*.*")],
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._editor.get("1.0", tk.END))
            self._status_var.set(f"Saved: {path}")

    def _open_file(self) -> None:
        if self._editor is None:
            return
        path = filedialog.askopenfilename(
            filetypes=[("HC Source", "*.hc"), ("All Files", "*.*")],
        )
        if path:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self._editor.delete("1.0", tk.END)
            self._editor.insert("1.0", content)
            self._status_var.set(f"Opened: {path}")
            self._update_line_count()

    def _update_line_count(self, event: Any = None) -> None:
        if self._editor is None:
            return
        content = self._editor.get("1.0", tk.END)
        lines = content.count("\n")
        self._line_count_var.set(f"Lines: {lines}")

    def _show_welcome(self) -> None:
        if self._out is None:
            return
        self._out.writeln("HC v1.0 — Hijaiyyah Codex Language", "header")
        self._out.writeln("═" * 50)
        self._out.writeln()
        self._out.writeln("Welcome to the HC IDE!", "result")
        self._out.writeln()
        self._out.writeln("Getting started:", "dim")
        self._out.writeln("  1. Select an example from the bottom panel", "dim")
        self._out.writeln("  2. Or write your own HC code in the editor", "dim")
        self._out.writeln("  3. Press ▶ Evaluate to run", "dim")
        self._out.writeln()
        self._out.writeln("Quick tips:", "dim")
        self._out.writeln("  • Use the character bar to insert Hijaiyyah letters", "dim")
        self._out.writeln("  • Syntax: let h = 'ب';  (single quotes for hybit)", "dim")
        self._out.writeln("  • Modules: hm::geometry::diameter()", "dim")
        self._out.writeln("  • Save/Open .hc files with the toolbar buttons", "dim")
        self._out.writeln()
        self._out.writeln("Dataset: HM-28-v1.0-HC18D", "time")
