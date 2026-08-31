"""
HC EVALUATOR v1.0 — CORRECTED
==============================
Full implementation of HC Language Specification v1.0 standard library.
Aligned with Matematika Hijaiyyah Chapters I–III.

Five Fields:
  hm::vectronometry  — Bab II-A (Ch 17-21)
  hm::differential   — Bab II-B (Ch 22-24)
  hm::integral       — Bab II-C (Ch 25-28)
  hm::geometry       — Bab II-D (Ch 29-31)
  hm::exomatrix      — Bab II-E (Ch 32-36)
"""

from __future__ import annotations

import hashlib
import math
from typing import Any, Callable, ClassVar, Dict, List, Optional

from hijaiyyah.core.exceptions import EBNFSemanticError
from hijaiyyah.core.master_table import MASTER_TABLE, CodexEntry
from hijaiyyah.language.ast_nodes import (
    ArrayLiteral,
    AssignStmt,
    ASTNode,
    BinaryExpr,
    Block,
    CallExpr,
    ConstStmt,
    ExpressedStmt,
    FnDecl,
    IfExpr,
    LetStmt,
    Literal,
    MatchExpr,
    MethodCall,
    ModuleAccess,
    Program,
    RangeExpr,
    ReturnStmt,
    VarRef,
)

# ══════════════════════════════════════════════════════════════════
#  SECTION 1 — VECTOR PRIMITIVES
# ══════════════════════════════════════════════════════════════════


def _vec(obj: Any) -> List[int]:
    """Extract 18-component integer vector from CodexEntry or list."""
    if isinstance(obj, CodexEntry):
        return list(obj.vector)
    if isinstance(obj, (list, tuple)):
        return list(obj)
    raise EBNFSemanticError(f"Expected hybit/vector, got {type(obj).__name__}")


def _v14(obj: Any) -> List[int]:
    """Return the 14D codex subvector (slots 0..13)."""
    v = _vec(obj)
    # Using comprehension to satisfy linter that doesn't like slices
    return [v[i] for i in range(14)]


def _U(vec: List[int]) -> int:
    """U(h) = Qx + Qs + Qa + 4·Qc  (Definition 11.1.1)."""
    return vec[10] + vec[11] + vec[12] + 4 * vec[13]


def _rho(vec: List[int]) -> int:
    """ρ(h) = Θ̂ − U  (Definition 11.2.1)."""
    return vec[0] - _U(vec)


def _norm2_v14(vec: List[int]) -> int:
    """‖v₁₄‖² = Σ v[k]² for k=0..13."""
    v14 = [vec[i] for i in range(14)]
    return sum(v * v for v in v14)


def _inner_v14(v1: List[int], v2: List[int]) -> int:
    """⟨v₁, v₂⟩ = Σ v1[k]·v2[k] for k=0..13."""
    return sum(v1[i] * v2[i] for i in range(14))


def _proj(vec: List[int], slots: List[int]) -> List[int]:
    """Projection: keep only named slots, zero the rest. Returns 18D."""
    p = [0] * 18
    for s in slots:
        p[s] = vec[s]
    return p


# ── Component slot name → index mapping ──────────────────────────

_SLOT_MAP: Dict[str, int] = {
    # Primary names (matching book notation)
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
    # Lowercase aliases
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


# ══════════════════════════════════════════════════════════════════
#  SECTION 2 — GUARD CHECKS (aligned with book R1–R5)
# ══════════════════════════════════════════════════════════════════


def _guard_check(vec: List[int]) -> bool:
    """
    Four structural guards on a raw v₁₈ vector.
    Returns True if all pass.

    Guards (on raw vector):
      G1: ρ ≥ 0           (Axiom 11.3.2)
      G2: A_N = Na+Nb+Nd  (Definition 12.2.1)
      G3: A_K = ΣK_j      (Definition 12.2.1)
      G4: A_Q = ΣQ_j      (Definition 12.2.1)
    """
    U = _U(vec)
    rho = vec[0] - U

    g1 = rho >= 0
    g2 = vec[14] == vec[1] + vec[2] + vec[3]
    g3 = vec[15] == vec[4] + vec[5] + vec[6] + vec[7] + vec[8]
    g4 = vec[16] == vec[9] + vec[10] + vec[11] + vec[12] + vec[13]

    return g1 and g2 and g3 and g4


def _guard_detail(vec: List[int]) -> Dict[str, Any]:
    """
    Five audit relations (Identity 33.1.1) checked on raw vector.

    R1: Θ̂ = U + ρ              (Proposition 11.3.1)
    R2: A_N = Na + Nb + Nd      (Definition 12.2.1)
    R3: A_K = ΣK_j              (Definition 12.2.1)
    R4: A_Q = ΣQ_j              (Definition 12.2.1)
    R5: U = Qx + Qs + Qa + 4Qc (Definition 11.1.1)
    """
    U = _U(vec)
    rho = vec[0] - U

    # R1: Θ̂ = U + ρ (equivalent to ρ ≥ 0 on raw vectors)
    R1 = (vec[0] == U + rho) and (rho >= 0)

    # R2: A_N = Na + Nb + Nd
    R2 = vec[14] == vec[1] + vec[2] + vec[3]

    # R3: A_K = Kp + Kx + Ks + Ka + Kc
    R3 = vec[15] == vec[4] + vec[5] + vec[6] + vec[7] + vec[8]

    # R4: A_Q = Qp + Qx + Qs + Qa + Qc
    R4 = vec[16] == vec[9] + vec[10] + vec[11] + vec[12] + vec[13]

    # R5: U = Qx + Qs + Qa + 4·Qc
    R5 = U == vec[10] + vec[11] + vec[12] + 4 * vec[13]

    return {
        "R1": R1,
        "R2": R2,
        "R3": R3,
        "R4": R4,
        "R5": R5,
        "rho": rho,
        "U": U,
        "all_pass": R1 and R2 and R3 and R4 and R5,
    }


# ══════════════════════════════════════════════════════════════════
#  SECTION 3 — EXOMATRIX BUILDER
# ══════════════════════════════════════════════════════════════════


def _build_exomatrix(v: List[int]) -> List[List[int]]:
    """
    Build 5×5 Exomatrix from v₁₈ (Definition 32.1.1).

    Row 0: [Θ̂,  U,    ρ,   0,   0  ]
    Row 1: [Na,  Nb,   Nd,  0,   A_N]
    Row 2: [Kp,  Kx,   Ks,  Ka,  Kc ]
    Row 3: [Qp,  Qx,   Qs,  Qa,  Qc ]
    Row 4: [H*,  0,    0,   A_K, A_Q]
    """
    theta = v[0]
    U = _U(v)
    rho = theta - U
    # A_N/A_K/A_Q are read from v₁₈, not recomputed from the components they
    # summarise. Recomputing them makes audit() tautological: R2–R4 compare a
    # matrix cell against the very sum that produced it, so a vector whose
    # stored checksum disagrees with its components would still audit clean.
    # For canonical letters the two are equal — guards G1–G3 enforce that — so
    # this only changes behaviour on the corrupt input the audit exists to catch.
    AN = v[14]
    AK = v[15]
    AQ = v[16]

    return [
        [theta, U, rho, 0, 0],
        [v[1], v[2], v[3], 0, AN],
        [v[4], v[5], v[6], v[7], v[8]],
        [v[9], v[10], v[11], v[12], v[13]],
        [v[17], 0, 0, AK, AQ],
    ]


# ══════════════════════════════════════════════════════════════════
#  SECTION 4 — MASTER TABLE ACCESS
# ══════════════════════════════════════════════════════════════════


def _all_entries() -> List[CodexEntry]:
    """Return all 28 CodexEntry objects from the sealed Master Table."""
    return list(MASTER_TABLE.all_entries())


def _all_vectors() -> List[List[int]]:
    """Return all 28 vectors as lists."""
    return [list(e.vector) for e in MASTER_TABLE.all_entries()]


# ══════════════════════════════════════════════════════════════════
#  SECTION 5 — CONTROL FLOW EXCEPTIONS
# ══════════════════════════════════════════════════════════════════


class ReturnException(Exception):
    """Raised by return statements to unwind the call stack."""

    def __init__(self, value: Any):
        self.value = value


class BreakException(Exception):
    """Raised by break statements."""

    pass


class ContinueException(Exception):
    """Raised by continue statements."""

    pass


# ══════════════════════════════════════════════════════════════════
#  SECTION 6 — ENVIRONMENT (scoped variable storage)
# ══════════════════════════════════════════════════════════════════


class Environment:
    """Lexically scoped variable and function storage."""

    def __init__(self, parent: Optional[Environment] = None):
        self._values: Dict[str, Any] = {}
        # name -> the keyword it was declared with, for bindings that cannot be
        # reassigned. Kept so the error can suggest the right fix: `let mut`
        # rescues a `let`, but nothing rescues a `const`.
        self._frozen: Dict[str, str] = {}
        self._parent = parent

    def define(
        self, name: str, value: Any, *, mutable: bool = True, kind: str = "let"
    ) -> None:
        self._values[name] = value
        self._frozen.pop(name, None)
        if not mutable:
            self._frozen[name] = kind

    def get(self, name: str) -> Any:
        if name in self._values:
            return self._values[name]
        parent = self._parent
        if isinstance(parent, Environment):
            return parent.get(name)
        raise EBNFSemanticError(f"Undefined variable: '{name}'")

    def assign(self, name: str, value: Any) -> None:
        if name in self._values:
            kind = self._frozen.get(name)
            if kind == "const":
                raise EBNFSemanticError(
                    f"Cannot assign to constant '{name}' — "
                    "declare it with `let mut` if it needs to change"
                )
            if kind is not None:
                # `let` binds immutably, as docs/hc_language.md §5.1 specifies;
                # `let mut` is the mutable form.
                raise EBNFSemanticError(
                    f"Cannot assign to immutable binding '{name}' — "
                    f"declare it as `let mut {name}`"
                )
            self._values[name] = value
            return
        parent = self._parent
        if isinstance(parent, Environment):
            parent.assign(name, value)
            return
        raise EBNFSemanticError(f"Cannot assign to undefined variable: '{name}'")


# ══════════════════════════════════════════════════════════════════
#  SECTION 7 — HC EVALUATOR
# ══════════════════════════════════════════════════════════════════


class HCEvaluator:
    """
    HC v1.0 Evaluator with complete five-field standard library.

    Corrections in this version:
      - comp_angle uses arctan(A_Q/A_K) per Definition 19.3.1
      - all_dot_variants checks theta equality
      - Duplicate method dispatch removed
      - Guard detail aligned with R1–R5
      - Index expression support
      - Hash method support
    """

    def __init__(self, print_func: Callable = print):
        self.table = MASTER_TABLE
        self.globals = Environment()
        self._print = print_func
        self.current_env = self.globals
        self._setup_builtins()

    # ── Built-in registration ────────────────────────────────────

    def _setup_builtins(self) -> None:
        g = self.globals

        # I/O
        g.define("println", lambda *a: self._print(" ".join(str(x) for x in a)))
        g.define("print", lambda *a: self._print(" ".join(str(x) for x in a)))

        # Assertions
        g.define("assert", self._bi_assert)
        g.define("assert_approx", self._bi_assert_approx)

        # Hybit constructors
        g.define("load", self._bi_load)
        g.define("load_id", self._bi_load_id)
        g.define("zero", lambda: [0] * 18)
        g.define("is_hijaiyyah", self._bi_is_hijaiyyah)
        g.define("identify", self._bi_identify)

        # Utility
        g.define("now", lambda: 0)
        g.define("abs", abs)
        g.define("sqrt", math.sqrt)
        g.define("len", len)

        # hm module namespace — the five fields
        g.define(
            "hm",
            self._build_stdlib(),
        )

    # ── Built-in implementations ─────────────────────────────────

    def _bi_assert(self, cond: bool, msg: str = "Assertion failed") -> None:
        if not cond:
            raise EBNFSemanticError(msg)

    def _bi_assert_approx(self, a: float, b: float, eps: float = 1e-9) -> None:
        if abs(a - b) > eps:
            raise EBNFSemanticError(f"assert_approx failed: |{a} - {b}| = {abs(a - b)} > {eps}")

    def _bi_load(self, ch: Any) -> Any:
        """Load a CodexEntry by character. Raises on unknown letter."""
        if isinstance(ch, CodexEntry):
            return ch
        if isinstance(ch, str):
            entry = self.table.get_by_char(ch)
            if entry is None:
                raise EBNFSemanticError(f"Unknown Hijaiyyah character: '{ch}'")
            return entry
        raise EBNFSemanticError(f"load() expects char, got {type(ch).__name__}")

    def _bi_load_id(self, idx: int) -> CodexEntry:
        entries = _all_entries()
        if 0 <= idx < len(entries):
            return entries[idx]
        raise EBNFSemanticError(f"load_id({idx}): out of range 0..{len(entries) - 1}")

    def _bi_is_hijaiyyah(self, ch: Any) -> bool:
        if not isinstance(ch, str):
            return False
        return self.table.get_by_char(ch) is not None

    def _bi_identify(self, vec: Any) -> Optional[str]:
        v = _vec(vec)
        for entry in _all_entries():
            if list(entry.vector) == v:
                return entry.char
        return None

    # ══════════════════════════════════════════════════════════════
    #  AST NODE EVALUATION
    # ══════════════════════════════════════════════════════════════

    def evaluate(self, node: ASTNode) -> Any:
        method_name = f"_eval_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise EBNFSemanticError(f"No evaluator for AST node: {type(node).__name__}")
        return method(node)

    def _eval_Program(self, node: Program) -> Any:
        result = None
        for stmt in node.body:
            result = self.evaluate(stmt)
        return result

    def _eval_LetStmt(self, node: LetStmt) -> Any:
        val = self.evaluate(node.value)
        self.current_env.define(node.name, val, mutable=node.mutable)
        return val

    def _eval_AssignStmt(self, node: AssignStmt) -> Any:
        val = self.evaluate(node.value)
        self.current_env.assign(node.name, val)
        return val

    def _eval_ConstStmt(self, node: ConstStmt) -> Any:
        val = self.evaluate(node.value)
        self.current_env.define(node.name, val, mutable=False, kind="const")
        return val

    def _eval_ExpressedStmt(self, node: ExpressedStmt) -> Any:
        return self.evaluate(node.expr)

    def _eval_ReturnStmt(self, node: ReturnStmt) -> None:
        val = self.evaluate(node.value) if node.value else None
        raise ReturnException(val)

    def _eval_Block(self, node: Block) -> Any:
        prev = self.current_env
        self.current_env = Environment(prev)
        try:
            result = None
            for stmt in node.statements:
                result = self.evaluate(stmt)
            return result
        finally:
            self.current_env = prev

    def _eval_FnDecl(self, node: FnDecl) -> None:
        def hc_func(*args):
            fn_env = Environment(self.globals)
            for i, (pname, _ptype) in enumerate(node.params):
                if i < len(args):
                    fn_env.define(pname, args[i])
            old = self.current_env
            self.current_env = fn_env
            try:
                self.evaluate(node.body)
            except ReturnException as rx:
                return rx.value
            finally:
                self.current_env = old
            return None

        self.current_env.define(node.name, hc_func)

    def _eval_Literal(self, node: Literal) -> Any:
        if node.lit_type == "hybit_ref":
            entry = self.table.get_by_char(node.value)
            if entry is None:
                raise EBNFSemanticError(f"Unknown Hijaiyyah character: '{node.value}'")
            return entry
        return node.value

    def _eval_VarRef(self, node: VarRef) -> Any:
        return self.current_env.get(node.name)

    # ── Binary expressions ───────────────────────────────────────

    def _eval_BinaryExpr(self, node: BinaryExpr) -> Any:
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        op = node.op

        # Hybit vector operations
        if isinstance(left, (CodexEntry, list)) and isinstance(right, (CodexEntry, list)):
            lv, rv = _vec(left), _vec(right)
            if op == "+":
                return [lv[i] + rv[i] for i in range(18)]
            if op == "-":
                return [lv[i] - rv[i] for i in range(14)]  # Delta ∈ ℤ¹⁴
            if op == "==":
                return lv == rv
            if op == "!=":
                return lv != rv

        # Scalar operations
        _ops = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b,
            "%": lambda a, b: a % b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            "<": lambda a, b: a < b,
            ">": lambda a, b: a > b,
            "<=": lambda a, b: a <= b,
            ">=": lambda a, b: a >= b,
            "&&": lambda a, b: bool(a) and bool(b),
            "||": lambda a, b: bool(a) or bool(b),
        }

        if op in _ops:
            return _ops[op](left, right)

        raise EBNFSemanticError(f"Unknown operator: {op}")

    # ── Method calls (h.method(args)) ────────────────────────────

    def _eval_MethodCall(self, node: MethodCall) -> Any:
        obj = self.evaluate(node.obj)
        args = [self.evaluate(a) for a in node.args]
        m = node.method

        # ── Hybit / vector method dispatch ──
        if isinstance(obj, (CodexEntry, list)):
            return self._dispatch_hybit_method(obj, m, args)

        # ── Dict key access ──
        if isinstance(obj, dict):
            if m in obj:
                val = obj[m]
                if callable(val) and args:
                    return val(*args)
                return val
            raise EBNFSemanticError(f"Key '{m}' not found in dict")

        # ── String methods ──
        if isinstance(obj, str):
            if m == "chars":
                return list(obj)
            if m == "len":
                return len(obj)
            if m == "to_string":
                return obj
            if hasattr(obj, m):
                return getattr(obj, m)(*args)

        # ── Generic attribute ──
        if hasattr(obj, m):
            attr = getattr(obj, m)
            if callable(attr):
                return attr(*args)
            return attr

        raise EBNFSemanticError(f"Unknown method '{m}' on {type(obj).__name__}")

    def _dispatch_hybit_method(self, obj: Any, method: str, args: List[Any]) -> Any:
        """Central dispatch for all hybit/vector methods."""
        vec = _vec(obj)

        # ── [A] Component field access ──
        if method in _SLOT_MAP:
            return vec[_SLOT_MAP[method]]

        # ── [B] Structural ──
        if method == "U":
            return _U(vec)
        if method == "rho":
            return _rho(vec)
        if method == "total":
            return (vec[14], vec[15], vec[16])
        if method == "array":
            return list(vec)
        if method == "guard":
            return _guard_check(vec)
        if method == "guard_detail":
            return _guard_detail(vec)

        # ── [C] Algebraic ──
        if method == "norm2":
            return _norm2_v14(vec)
        if method == "norm":
            return math.sqrt(_norm2_v14(vec))
        if method == "dot":
            return _inner_v14(vec, _vec(args[0])) if args else 0
        if method == "cosine":
            if not args:
                return 0.0
            other = _vec(args[0])
            n1 = math.sqrt(_norm2_v14(vec))
            n2 = math.sqrt(_norm2_v14(other))
            if n1 == 0 or n2 == 0:
                return 0.0
            return max(0.0, _inner_v14(vec, other) / (n1 * n2))

        # ── [D] Metric ──
        if method == "dist2":
            other = _vec(args[0]) if args else [0] * 18
            return sum((vec[i] - other[i]) ** 2 for i in range(14))
        if method == "dist":
            other = _vec(args[0]) if args else [0] * 18
            return math.sqrt(sum((vec[i] - other[i]) ** 2 for i in range(14)))
        if method == "manhattan":
            other = _vec(args[0]) if args else [0] * 18
            return sum(abs(vec[i] - other[i]) for i in range(14))
        if method == "hamming":
            other = _vec(args[0]) if args else [0] * 18
            return sum(1 for i in range(14) if vec[i] != other[i])

        # ── [E] Projection ──
        if method == "proj_theta":
            return _proj(vec, [0])
        if method == "proj_N":
            return _proj(vec, [1, 2, 3])
        if method == "proj_K":
            return _proj(vec, [4, 5, 6, 7, 8])
        if method == "proj_Q":
            return _proj(vec, [9, 10, 11, 12, 13])

        # ── [F] Ratios (Ch 18-19) ──
        if method == "r_N":
            total = vec[14] + vec[15] + vec[16]
            return vec[14] / total if total else 0.0
        if method == "r_K":
            total = vec[14] + vec[15] + vec[16]
            return vec[15] / total if total else 0.0
        if method == "r_Q":
            total = vec[14] + vec[15] + vec[16]
            return vec[16] / total if total else 0.0
        if method == "r_U":
            return _U(vec) / vec[0] if vec[0] else 0.0
        if method == "r_rho":
            return _rho(vec) / vec[0] if vec[0] else 0.0
        if method == "r_loop":
            return (4 * vec[13]) / vec[0] if vec[0] else 0.0

        # ── [G] Compositional angle (Def 19.3.1) ──
        if method == "alpha":
            ak = vec[15]  # A_K
            aq = vec[16]  # A_Q
            if ak > 0:
                return math.atan(aq / ak)
            elif aq > 0:
                return math.pi / 2
            else:
                return 0.0

        # ── [H] Exomatrix ──
        if method == "exomatrix":
            return _build_exomatrix(vec)
        if method == "phi":
            E = _build_exomatrix(vec)
            return sum(E[r][c] ** 2 for r in range(5) for c in range(5))

        # ── [I] Cryptographic ──
        if method == "hash":
            v18 = [vec[i] for i in range(18)]
            data = bytes(v18)
            return hashlib.sha256(data).hexdigest()

        raise EBNFSemanticError(f"Unknown hybit method: '{method}'")

    # ── Index expressions (h[0], arr[i]) ─────────────────────────

    def _eval_ArrayLiteral(self, node: ArrayLiteral) -> List[Any]:
        """
        Build a list from `[a, b, c]`.

        The lexer, parser and IndexExpr all handled arrays; only this was
        missing, so an array literal parsed cleanly and then raised
        "No evaluator for AST node" the moment it was evaluated.
        """
        return [self.evaluate(element) for element in node.elements]

    def _eval_IndexExpr(self, node) -> Any:
        """Handle h[0], arr[i], etc."""
        obj = self.evaluate(node.obj)
        index = self.evaluate(node.index)

        if isinstance(obj, (CodexEntry, list)):
            vec = _vec(obj)
            if isinstance(index, int) and 0 <= index < len(vec):
                return vec[index]
            raise EBNFSemanticError(f"Index {index} out of range for vector of length {len(vec)}")
        if isinstance(obj, dict) and index in obj:
            return obj[index]

        raise EBNFSemanticError(f"Cannot index {type(obj).__name__} with {index}")

    # ── Function / module calls ──────────────────────────────────

    def _eval_CallExpr(self, node: CallExpr) -> Any:
        # Module-path call: hm::vectronometry::norm2(h)
        if "::" in node.callee:
            parts = node.callee.split("::")
            val = self.globals.get(parts[0])
            for part in parts[1:]:
                if isinstance(val, dict) and part in val:
                    val = val[part]
                else:
                    raise EBNFSemanticError(f"Module member '{part}' not found in '{node.callee}'")
            func = val
        else:
            func = self.current_env.get(node.callee)

        args = [self.evaluate(a) for a in node.args]

        if callable(func):
            return func(*args)
        return func

    def _eval_ModuleAccess(self, node: ModuleAccess) -> Any:
        val = self.globals.get(node.path[0])
        for part in node.path[1:]:
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                raise EBNFSemanticError(f"Module member '{part}' not found")
        return val

    # ── Control flow ─────────────────────────────────────────────

    def _eval_IfExpr(self, node: IfExpr) -> Any:
        if self.evaluate(node.condition):
            return self.evaluate(node.then_branch)
        elif node.else_branch:
            return self.evaluate(node.else_branch)
        return None

    def _eval_UnaryExpr(self, node):
        operand = self.evaluate(node.operand)
        if node.op == "-":
            return -operand
        if node.op == "!":
            return not operand
        if node.op == "*":
            # Dereference (for future pointers/refs)
            return operand
        return operand

    def _eval_RangeExpr(self, node: RangeExpr) -> range:
        start = self.evaluate(node.start)
        end = self.evaluate(node.end)
        if node.inclusive:
            return range(start, end + 1)
        return range(start, end)

    def _eval_MatchExpr(self, node: MatchExpr) -> Any:
        val = self.evaluate(node.condition)
        for arm in node.arms:
            if isinstance(arm.pattern, VarRef) and arm.pattern.name == "_":
                return self.evaluate(arm.body)
            pat = self.evaluate(arm.pattern)
            if isinstance(pat, range) and val in pat:
                return self.evaluate(arm.body)
            if val == pat:
                return self.evaluate(arm.body)
        return None

    def _eval_ForStmt(self, node) -> None:
        iterable = self.evaluate(node.iterable)
        prev = self.current_env
        self.current_env = Environment(prev)
        try:
            for item in iterable:
                self.current_env.define(node.var, item)
                try:
                    self.evaluate(node.body)
                except BreakException:
                    break
                except ContinueException:
                    continue
        finally:
            self.current_env = prev

    def _eval_WhileStmt(self, node) -> None:
        while self.evaluate(node.condition):
            try:
                self.evaluate(node.body)
            except BreakException:
                break
            except ContinueException:
                continue

    def _eval_BreakStmt(self, node) -> None:
        raise BreakException()

    def _eval_ContinueStmt(self, node) -> None:
        raise ContinueException()

    # ══════════════════════════════════════════════════════════════
    #  STANDARD LIBRARY MODULES
    # ══════════════════════════════════════════════════════════════

    # ── Field 1: hm::vectronometry (Bab II-A, Ch 17–21) ─────────

    # ══════════════════════════════════════════════════════════════
    #  Standard library
    # ══════════════════════════════════════════════════════════════
    #
    # Each hm:: module forwards to the corresponding package under
    # hijaiyyah.algebra rather than reimplementing it.
    #
    # These builders used to hold their own copies of the maths, which made the
    # evaluator a third implementation alongside the Python packages and the
    # JavaScript engine — and it had drifted: 27 of the 55 functions the grammar
    # advertises had no implementation at all here, so half of hm::geometry
    # raised "Module member not found" when called.
    #
    # Names come from grammar.STDLIB_MODULES, so the advertised surface and the
    # callable surface cannot disagree; anything listed there and missing from
    # its package fails loudly at construction instead of at the call site.

    _STDLIB_SOURCES: ClassVar[Dict[str, str]] = {
        "vectronometry": "hijaiyyah.algebra.vektronometry",
        "differential": "hijaiyyah.algebra.normivektor",
        "integral": "hijaiyyah.algebra.aggregametric",
        "geometry": "hijaiyyah.algebra.intrametric",
        "exomatrix": "hijaiyyah.algebra.exometric",
    }

    def _build_stdlib(self) -> Dict[str, Dict[str, Callable]]:
        from importlib import import_module

        from .grammar import STDLIB_MODULES

        modules: Dict[str, Dict[str, Callable]] = {}
        for short, dotted in self._STDLIB_SOURCES.items():
            package = import_module(dotted)
            declared = STDLIB_MODULES[f"hm::{short}"]
            names = list(declared)  # a dict yields its keys, a list its items

            table: Dict[str, Callable] = {}
            missing: List[str] = []
            for name in names:
                fn = getattr(package, name, None)
                if callable(fn):
                    table[name] = fn
                else:
                    missing.append(name)

            if missing:
                raise EBNFSemanticError(
                    f"hm::{short} advertises {missing} but {dotted} does not "
                    "define them"
                )
            modules[short] = table
        return modules
