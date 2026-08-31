"""
HC v1.0 FORMAL GRAMMAR
=======================
Complete EBNF specification for the HC (Hijaiyyah Codex) programming language.
Aligned with HL-18E Language Spec and HC Language Spec v1.0.

This module contains:
  1. FORMAL_GRAMMAR  — the complete EBNF as a string constant
  2. SLOT_NAMES      — valid component field names for hybit access
  3. LATIN_NAMES     — Latin transliterations of Hijaiyyah letter names
  4. GROUP_NAMES     — group accessor names (N, K, Q, v18, etc.)
  5. Example programs for testing

Release: HM-28-v1.0-HC18D
"""

from __future__ import annotations

from typing import Dict, FrozenSet, List, Tuple

# ══════════════════════════════════════════════════════════════════
#  SECTION 1 — FORMAL EBNF GRAMMAR
# ══════════════════════════════════════════════════════════════════

FORMAL_GRAMMAR: str = r"""
(* ================================================================ *)
(* HC v1.0: Hijaiyyah Codex Language — Formal Grammar               *)
(* HL-18E: Hijaiyyah Language for 18-Element Operations              *)
(* Release: HM-28-v1.0-HC18D                                        *)
(* ================================================================ *)

(* ── 1. Lexical Rules ──────────────────────────────────────────── *)

digit           = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7'
                | '8' | '9' ;

letter          = 'a'..'z' | 'A'..'Z' ;

integer_lit     = digit , { digit } ;

float_lit       = digit , { digit } , '.' , digit , { digit } ;

number_lit      = float_lit | integer_lit ;

string_lit      = '"' , { string_char } , '"' ;

string_char     = any_char - '"' - '\\'
                | '\\' , escape_char ;

escape_char     = 'n' | 't' | 'r' | '\\' | '"' | "'" | '0' ;

hijaiyyah_char  = 'ا' | 'ب' | 'ت' | 'ث' | 'ج' | 'ح' | 'خ' | 'د'
                | 'ذ' | 'ر' | 'ز' | 'س' | 'ش' | 'ص' | 'ض' | 'ط'
                | 'ظ' | 'ع' | 'غ' | 'ف' | 'ق' | 'ك' | 'ل' | 'م'
                | 'ن' | 'و' | 'هـ' | 'ي' ;

hijaiyyah_lit   = "'" , hijaiyyah_char , "'" ;

identifier      = ( letter | '_' ) , { letter | digit | '_' } ;

(* ── 2. Comments ───────────────────────────────────────────────── *)

line_comment    = '//' , { any_char - newline } , newline ;

block_comment   = '(--' , { any_char | block_comment } , '--)' ;

(* ── 3. Program Structure ─────────────────────────────────────── *)

program         = { statement } ;

statement       = let_stmt
                | const_stmt
                | fn_decl
                | for_stmt
                | while_stmt
                | if_expr
                | match_expr
                | return_stmt
                | break_stmt
                | continue_stmt
                | use_stmt
                | expr_stmt ;

(* ── 4. Variable Declarations ─────────────────────────────────── *)

let_stmt        = 'let' , [ 'mut' ] , identifier ,
                  [ ':' , type_expr ] , '=' , expression , ';' ;

const_stmt      = 'const' , identifier , [ ':' , type_expr ] ,
                  '=' , expression , ';' ;

(* ── 5. Function Declarations ─────────────────────────────────── *)

fn_decl         = 'fn' , identifier , '(' , [ param_list ] , ')' ,
                  [ '->' , type_expr ] , block ;

param_list      = param , { ',' , param } ;

param           = identifier , [ ':' , type_expr ] ;

(* ── 6. Block ─────────────────────────────────────────────────── *)

block           = '{' , { statement } , '}' ;

(* ── 7. Control Flow ──────────────────────────────────────────── *)

if_expr         = 'if' , expression , block ,
                  [ 'else' , ( if_expr | block ) ] ;

match_expr      = 'match' , expression , '{' , { match_arm } , '}' ;

match_arm       = pattern , '=>' , ( expression | block ) , [ ',' ] ;

pattern         = '_'
                | number_lit
                | string_lit
                | hijaiyyah_lit
                | identifier
                | range_pattern ;

range_pattern   = integer_lit , ( '..' | '..=' ) , integer_lit ;

for_stmt        = 'for' , identifier , 'in' , expression , block ;

while_stmt      = 'while' , expression , block ;

return_stmt     = 'return' , [ expression ] , ';' ;

break_stmt      = 'break' , ';' ;

continue_stmt   = 'continue' , ';' ;

use_stmt        = 'use' , module_path , ';' ;

module_path     = identifier , { '::' , identifier } ;

(* ── 8. Expressions (Precedence Climbing) ─────────────────────── *)

expression      = assignment ;

assignment      = ( identifier , '=' , expression )
                | logical_or ;

logical_or      = logical_and , { '||' , logical_and } ;

logical_and     = equality , { '&&' , equality } ;

equality        = comparison , { ( '==' | '!=' ) , comparison } ;

comparison      = range_expr , { ( '<' | '>' | '<=' | '>=' ) , range_expr } ;

range_expr      = addition , [ ( '..' | '..=' ) , addition ] ;

addition        = multiplication , { ( '+' | '-' ) , multiplication } ;

multiplication  = unary , { ( '*' | '/' | '%' ) , unary } ;

unary           = ( '!' | '-' ) , unary
                | postfix ;

postfix         = primary , { postfix_op } ;

postfix_op      = method_call
                | index_access
                | field_access ;

method_call     = '.' , identifier , '(' , [ arg_list ] , ')' ;

index_access    = '[' , expression , ']' ;

field_access    = '.' , identifier ;

primary         = number_lit
                | string_lit
                | hijaiyyah_lit
                | identifier_expr
                | '(' , expression , ')'
                | array_lit
                | if_expr
                | match_expr ;

identifier_expr = identifier , [ module_suffix | call_suffix ] ;

module_suffix   = '::' , identifier , { '::' , identifier } ,
                  [ '(' , [ arg_list ] , ')' ] ;

call_suffix     = '(' , [ arg_list ] , ')' ;

arg_list        = expression , { ',' , expression } ;

array_lit       = '[' , [ expression , { ',' , expression } ] , ']' ;

(* ── 9. Types ─────────────────────────────────────────────────── *)

type_expr       = simple_type
                | array_type
                | generic_type ;

simple_type     = 'int' | 'uint' | 'int32' | 'uint8'
                | 'float64' | 'bool' | 'char' | 'string'
                | 'hybit' | 'Delta' | 'Exomatrix'
                | 'StringCodex' | 'AuditResult'
                | identifier ;

array_type      = '[' , type_expr , ';' , integer_lit , ']' ;

generic_type    = identifier , '<' , type_expr , { ',' , type_expr } , '>' ;

(* ── 10. Hybit-Specific Syntax ────────────────────────────────── *)
(*                                                                  *)
(* Hybit is a PRIMITIVE type, not a library import.                 *)
(* The following operations are built into the language:             *)
(*                                                                  *)
(*   Component access:  h.theta, h.Na, h.Kb, h.Qc, etc.           *)
(*   Guard check:       h.guard()         -> bool                   *)
(*   Guard detail:      h.guard_detail()  -> AuditResult            *)
(*   Algebraic:         h.norm2(), h.dot(other), h.cosine(other)   *)
(*   Metric:            h.dist2(other), h.manhattan(other)          *)
(*   Projection:        h.proj_theta(), h.proj_N(), etc.            *)
(*   Ratios:            h.r_N(), h.r_K(), h.r_Q()                  *)
(*   Decomposition:     h.U(), h.rho()                              *)
(*   Exomatrix:         h.exomatrix(), h.phi()                      *)
(*   Crypto:            h.hash()                                    *)
(*   Indexing:          h[0], h[14]                                 *)
(*   Vector ops:        a + b (CADD), a - b (CSUB -> Delta)        *)
(*                                                                  *)
(* ── 11. Standard Library Modules ─────────────────────────────── *)
(*                                                                  *)
(*   hm::vectronometry   — Field 1: Ch 17-21                       *)
(*   hm::differential    — Field 2: Ch 22-24                       *)
(*   hm::integral        — Field 3: Ch 25-28                       *)
(*   hm::geometry        — Field 4: Ch 29-31                       *)
(*   hm::exomatrix       — Field 5: Ch 32-36                       *)
(*                                                                  *)
(* Module functions are called via :: syntax:                       *)
(*   hm::geometry::diameter()                                       *)
(*   hm::integral::string_integral("بسم")                           *)
(*                                                                  *)
(* ================================================================ *)
"""


# ══════════════════════════════════════════════════════════════════
#  SECTION 2 — NAMED CONSTANTS FOR LEXER/PARSER/EVALUATOR
# ══════════════════════════════════════════════════════════════════

# ── Hybit component slot names ───────────────────────────────────

SLOT_NAMES: FrozenSet[str] = frozenset(
    {
        # Primary names (matching book notation)
        "theta",
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
        "Hstar",
        # Lowercase aliases
        "na",
        "nb",
        "nd",
        "kp",
        "kx",
        "ks",
        "ka",
        "kc",
        "qp",
        "qx",
        "qs",
        "qa",
        "qc",
        "an",
        "ak",
        "aq",
        "hstar",
    }
)

# Slot name → v18 index mapping
SLOT_INDEX: Dict[str, int] = {
    "theta": 0,
    "Na": 1,
    "Nb": 2,
    "Nd": 3,
    "Kp": 4,
    "Kx": 5,
    "Ks": 6,
    "Ka": 7,
    "Kc": 8,
    "Qp": 9,
    "Qx": 10,
    "Qs": 11,
    "Qa": 12,
    "Qc": 13,
    "AN": 14,
    "AK": 15,
    "AQ": 16,
    "Hstar": 17,
    # lowercase
    "na": 1,
    "nb": 2,
    "nd": 3,
    "kp": 4,
    "kx": 5,
    "ks": 6,
    "ka": 7,
    "kc": 8,
    "qp": 9,
    "qx": 10,
    "qs": 11,
    "qa": 12,
    "qc": 13,
    "an": 14,
    "ak": 15,
    "aq": 16,
    "hstar": 17,
}

# ── Latin transliteration names ──────────────────────────────────

LATIN_NAMES: FrozenSet[str] = frozenset(
    {
        "alif",
        "ba",
        "ta",
        "tsa",
        "jim",
        "ha",
        "kha",
        "dal",
        "dzal",
        "ra",
        "zay",
        "sin",
        "syin",
        "shad",
        "dhad",
        "tha",
        "zha",
        "ain",
        "ghain",
        "fa",
        "qaf",
        "kaf",
        "lam",
        "mim",
        "nun",
        "waw",
        "haa",
        "ya",
    }
)

# Latin name → Hijaiyyah character mapping
LATIN_TO_CHAR: Dict[str, str] = {
    "alif": "ا",
    "ba": "ب",
    "ta": "ت",
    "tsa": "ث",
    "jim": "ج",
    "ha": "ح",
    "kha": "خ",
    "dal": "د",
    "dzal": "ذ",
    "ra": "ر",
    "zay": "ز",
    "sin": "س",
    "syin": "ش",
    "shad": "ص",
    "dhad": "ض",
    "tha": "ط",
    "zha": "ظ",
    "ain": "ع",
    "ghain": "غ",
    "fa": "ف",
    "qaf": "ق",
    "kaf": "ك",
    "lam": "ل",
    "mim": "م",
    "nun": "ن",
    "waw": "و",
    "haa": "هـ",
    "ya": "ي",
}

# ── Group accessor names ─────────────────────────────────────────

GROUP_NAMES: FrozenSet[str] = frozenset(
    {
        "N",
        "K",
        "Q",  # Primitive group vectors
        "n",
        "k",
        "q",  # lowercase aliases
        "v14",
        "v18",  # Full codex vectors
        "codex",  # Alias for v18
        "checksum",  # (AN, AK, AQ) tuple
        "nuqtah",
        "khatt",
        "qaws",  # Full Arabic names
    }
)

# Group name → slot indices mapping
GROUP_SLOTS: Dict[str, List[int]] = {
    "N": [1, 2, 3],
    "n": [1, 2, 3],
    "nuqtah": [1, 2, 3],
    "K": [4, 5, 6, 7, 8],
    "k": [4, 5, 6, 7, 8],
    "khatt": [4, 5, 6, 7, 8],
    "Q": [9, 10, 11, 12, 13],
    "q": [9, 10, 11, 12, 13],
    "qaws": [9, 10, 11, 12, 13],
    "v14": list(range(14)),
    "v18": list(range(18)),
    "codex": list(range(18)),
    "checksum": [14, 15, 16],
}


# ══════════════════════════════════════════════════════════════════
#  SECTION 3 — BUILT-IN METHOD REGISTRY
# ══════════════════════════════════════════════════════════════════

# Methods available on hybit objects (h.method_name)
HYBIT_METHODS: FrozenSet[str] = frozenset(
    {
        # Component access (also handled by SLOT_NAMES)
        "theta",
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
        "Hstar",
        # Structural
        "U",
        "rho",
        "total",
        "array",
        "guard",
        "guard_detail",
        # Algebraic
        "norm2",
        "norm",
        "dot",
        "cosine",
        # Metric
        "dist2",
        "dist",
        "manhattan",
        "hamming",
        # Projection
        "proj_theta",
        "proj_N",
        "proj_K",
        "proj_Q",
        # Ratios
        "r_N",
        "r_K",
        "r_Q",
        "r_U",
        "r_rho",
        "r_loop",
        # Compositional
        "alpha",
        # Exomatrix
        "exomatrix",
        "phi",
        # Crypto
        "hash",
    }
)

# Standard library module paths
STDLIB_MODULES: Dict[str, List[str]] = {
    "hm::vectronometry": [
        "project",
        "primitive_ratios",
        "turning_ratios",
        "comp_angle",
        "norm2",
        "norm",
        "inner",
        "cosine",
        "pythagorean_check",
        "full_table",
    ],
    "hm::differential": [
        "diff",
        "norm_decomposition",
        "diff_theta",
        "diff_N",
        "diff_K",
        "diff_Q",
        "dot_gradient",
        "u_gradient",
        "all_dot_variants",
        "second_diff",
        "distance_table",
    ],
    "hm::integral": [
        "string_integral",
        "add_codex",
        "layer_integrals",
        "layer_integrals_from_cod",
        "centroid",
        "cumulative",
        "energy_integral",
        "mean_theta",
        "min_component_theta",
        "max_component_theta",
    ],
    "hm::geometry": [
        "euclidean",
        "euclidean_sq",
        "manhattan",
        "hamming",
        "distance_decomposition",
        "gram_matrix",
        "is_orthogonal",
        "diameter_sq",
        "diameter",
        "alphabet_centroid",
        "nearest",
        "k_nearest",
        "polarization_check",
    ],
    "hm::exomatrix": [
        "build",
        "audit",
        "row_sums",
        "grand_sum",
        "phi",
        "phi_decomposition",
        "string_exomatrix",
        "rank_M14",
        "rank_M",
        "energy_table",
        "reconstruct",
    ],
}

# Built-in global functions
BUILTIN_FUNCTIONS: FrozenSet[str] = frozenset(
    {
        "println",
        "print",
        "assert",
        "assert_approx",
        "load",
        "load_id",
        "zero",
        "is_hijaiyyah",
        "identify",
        "abs",
        "sqrt",
        "len",
        "now",
    }
)


# ══════════════════════════════════════════════════════════════════
#  SECTION 4 — EXAMPLE PROGRAMS
# ══════════════════════════════════════════════════════════════════

EXAMPLES: List[Tuple[str, str, str]] = [
    # (name, description, source_code)
    (
        "hello",
        "Minimal HC program",
        """\
let h = 'ب';
println("Hello from HC v1.0!");
println("Letter Ba:", h.theta(), h.guard());
""",
    ),
    (
        "guard_all",
        "Verify all 28 letters pass guard",
        """\
for i in 1..=28 {
    let h = load_id(i);
    if !h.guard() {
        println("FAIL:", i);
    }
}
println("All guards verified.");
""",
    ),
    (
        "string_integral",
        "Compute string codex for بسم",
        """\
let cod = hm::integral::string_integral("بسم");
println("Cod18(bsm):", cod);
let layers = hm::integral::layer_integrals("بسم");
println("Theta:", layers);
""",
    ),
    (
        "five_fields",
        "Complete five-field analysis",
        """\
let h = 'ج';
println("=== Vectronometry ===");
println("Norm2:", hm::vectronometry::norm2(h));
println("Ratios:", hm::vectronometry::primitive_ratios(h));
println("Pythagorean:", hm::vectronometry::pythagorean_check(h));

println("=== Differential ===");
let ba = 'ب';
let delta = hm::differential::diff(h, ba);
println("Delta(Jim,Ba):", delta);

println("=== Integral ===");
let cod = hm::integral::string_integral("بسم");
println("Cod18:", cod);

println("=== Geometry ===");
println("Diameter:", hm::geometry::diameter());
println("Orthogonal(Alif,Ba):", hm::geometry::is_orthogonal('ا', 'ب'));

println("=== Exomatrix ===");
let E = hm::exomatrix::build('هـ');
println("Phi(Ha):", hm::exomatrix::phi(E));
println("Audit:", hm::exomatrix::audit(E));
println("=== DONE ===");
""",
    ),
    (
        "comparison",
        "Compare two strings",
        """\
let bsm = hm::integral::string_integral("بسم");
let allah = hm::integral::string_integral("اللہ");
println("bsm Theta:", bsm);
println("allah Theta:", allah);
println("Same total turning: both = 10 quadrants");
""",
    ),
    (
        "distance",
        "Compute distances between letters",
        """\
let alif = 'ا';
let ha = 'هـ';
let d = hm::geometry::euclidean(alif, ha);
println("d(Alif, Ha) =", d);
println("d^2 =", hm::geometry::euclidean_sq(alif, ha));
println("Diameter =", hm::geometry::diameter());
""",
    ),
    (
        "energy_table",
        "Display energy rankings",
        """\
let table = hm::exomatrix::energy_table();
println("Energy table (28 letters by Phi):");
println(table);
""",
    ),
    (
        "dot_variants",
        "Find all dot-variant pairs",
        """\
let pairs = hm::differential::all_dot_variants();
println("Dot-variant pairs:");
println(pairs);
""",
    ),
    (
        "banking",
        "Banking transaction integrity demo",
        """\
let text = "TX-001-BANK-A";
let seal = hm::integral::string_integral(text);
println("Transaction seal:", seal);
// Guard check on seal
println("Integrity:", seal);
""",
    ),
]

# Example lookup by name
EXAMPLE_BY_NAME: Dict[str, str] = {name: source for name, _desc, source in EXAMPLES}

# Example descriptions
EXAMPLE_DESCRIPTIONS: Dict[str, str] = {name: desc for name, desc, _source in EXAMPLES}


# ══════════════════════════════════════════════════════════════════
#  SECTION 5 — GRAMMAR VALIDATION HELPERS
# ══════════════════════════════════════════════════════════════════


def is_slot_name(name: str) -> bool:
    """Check if a name is a valid hybit component slot."""
    return name in SLOT_NAMES


def is_latin_name(name: str) -> bool:
    """Check if a name is a valid Latin transliteration of a Hijaiyyah letter."""
    return name.lower() in LATIN_NAMES


def is_group_name(name: str) -> bool:
    """Check if a name is a valid group accessor."""
    return name in GROUP_NAMES


def is_hybit_method(name: str) -> bool:
    """Check if a name is a valid hybit method."""
    return name in HYBIT_METHODS or name in SLOT_NAMES


def is_builtin(name: str) -> bool:
    """Check if a name is a built-in function."""
    return name in BUILTIN_FUNCTIONS


def get_module_functions(module_path: str) -> List[str]:
    """Get the list of functions in a standard library module."""
    return STDLIB_MODULES.get(module_path, [])


def latin_to_hijaiyyah(name: str) -> str:
    """Convert a Latin letter name to its Hijaiyyah character."""
    return LATIN_TO_CHAR.get(name.lower(), "")


def get_slot_index(name: str) -> int:
    """Get the v18 index for a slot name. Returns -1 if not found."""
    return SLOT_INDEX.get(name, -1)


def get_group_slots(name: str) -> List[int]:
    """Get the list of v18 indices for a group name."""
    return GROUP_SLOTS.get(name, [])
