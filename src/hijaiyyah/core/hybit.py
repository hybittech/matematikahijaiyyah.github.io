"""
Hybit: the formal unit of structured information.

Definition 3.1.1 (Bab III):
  A hybit is an element of the valid codex set:
    h* ∈ V ⊂ ℕ₀¹⁸
  where V satisfies guards G1–G4 and topological constraints T1–T2.

Proposition 3.2.1:
  (V, +) forms a constrained commutative monoid — closed under
  component-wise addition with identity 0⃗.

Proposition 3.4.1:
  Membership validation is O(1) — no lookup tables, no external
  authority, no cryptographic computation required.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .exomatrix import build_exomatrix
from .guards import compute_rho, compute_U, full_guard_check, guard_check


class Hybit:
    """
    Formal hybit unit — element of V ⊂ ℕ₀¹⁸.

    Each instance wraps an 18-component integer vector and guarantees
    that the vector satisfies all structural (G1–G4) and topological
    (T1–T2) guards at construction time.

    Attributes:
        v: The 18D codex vector (immutable tuple).
    """

    __slots__ = ("_v",)

    def __init__(self, v: List[int] | Tuple[int, ...], *, _skip_check: bool = False) -> None:
        """
        Create a Hybit from a raw 18D vector.

        Args:
            v: 18-component integer vector.
            _skip_check: Internal flag to skip validation (used by
                         trusted factory methods that already validated).

        Raises:
            ValueError: If the vector is invalid (fails guards).
        """
        if len(v) != 18:
            raise ValueError(f"Hybit requires 18 components, got {len(v)}")
        if not _skip_check:
            if any(x < 0 for x in v):
                raise ValueError("All components must be non-negative (ℕ₀)")
            if not guard_check(v):
                raise ValueError(f"Vector fails guard check: {full_guard_check(v)}")
        self._v: Tuple[int, ...] = tuple(v)

    # ── Factory methods ──────────────────────────────────────────

    @classmethod
    def from_vector(cls, v: List[int] | Tuple[int, ...]) -> Hybit:
        """Create a Hybit from a raw 18D vector with full validation."""
        return cls(v)

    @classmethod
    def from_char(cls, ch: str) -> Optional[Hybit]:
        """
        Create a Hybit from a Hijaiyyah character.
        Returns None if the character is not in the Master Table.
        """
        # Deferred import to avoid circular dependency
        from .master_table import MASTER_TABLE

        entry = MASTER_TABLE.get_by_char(ch)
        if entry is None:
            return None
        return cls(list(entry.vector), _skip_check=True)

    @classmethod
    def zero(cls) -> Hybit:
        """Identity element of the monoid (V, +)."""
        return cls([0] * 18, _skip_check=True)

    # ── Properties ───────────────────────────────────────────────

    @property
    def v(self) -> Tuple[int, ...]:
        """The 18D codex vector (read-only)."""
        return self._v

    @property
    def theta_hat(self) -> int:
        """Θ̂ — normalized turning number."""
        return self._v[0]

    @property
    def U(self) -> int:
        """U(h) = Qx + Qs + Qa + 4·Qc — curvature usage."""
        return compute_U(self._v)

    @property
    def rho(self) -> int:
        """ρ(h) = Θ̂ − U — turning residue."""
        return compute_rho(self._v)

    # ── Monoid operation (Proposition 3.2.1) ─────────────────────

    def cadd(self, other: Hybit) -> Hybit:
        """
        Codex addition — the native monoid operation.

        Proposition 3.9.1: All identities are preserved:
          - Θ̂ = U + ρ
          - ρ ≥ 0
          - G1–G4, T1–T2
        """
        result = [self._v[i] + other._v[i] for i in range(18)]
        # Closure guaranteed by Proposition 3.2.1:
        # G1–G3 linear, G4 preserved (ρ₁ + ρ₂ ≥ 0), T1/T2 preserved
        return Hybit(result, _skip_check=True)

    def __add__(self, other: Hybit) -> Hybit:
        """Operator form of CADD."""
        return self.cadd(other)

    # ── Validation (Proposition 3.4.1) ───────────────────────────

    def is_valid(self) -> bool:
        """O(1) membership check: h* ∈ V."""
        return guard_check(self._v)

    def guard_status(self) -> Dict[str, bool]:
        """Per-guard validation status: G1–G4, T1, T2."""
        return full_guard_check(self._v)

    # ── Projections (Definition 2.3.1) ───────────────────────────

    def project_theta(self) -> List[int]:
        """Π_Θ projection — turning layer."""
        r = [0] * 18
        r[0] = self._v[0]
        return r

    def project_N(self) -> List[int]:
        """Π_N projection — dot distribution layer."""
        r = [0] * 18
        r[1], r[2], r[3] = self._v[1], self._v[2], self._v[3]
        return r

    def project_K(self) -> List[int]:
        """Π_K projection — line type layer."""
        r = [0] * 18
        for i in range(4, 9):
            r[i] = self._v[i]
        return r

    def project_Q(self) -> List[int]:
        """Π_Q projection — curve type layer."""
        r = [0] * 18
        for i in range(9, 14):
            r[i] = self._v[i]
        return r

    def project(self, layer: str) -> List[int]:
        """
        Project to a named layer.

        Args:
            layer: One of 'theta', 'N', 'K', 'Q'.
        """
        projections = {
            "theta": self.project_theta,
            "N": self.project_N,
            "K": self.project_K,
            "Q": self.project_Q,
        }
        fn = projections.get(layer)
        if fn is None:
            raise ValueError(f"Unknown layer '{layer}', expected: theta, N, K, Q")
        return fn()

    # ── Decomposition ────────────────────────────────────────────

    def decompose(self) -> Tuple[int, int]:
        """Decompose Θ̂ into (U, ρ)."""
        U = self.U
        return (U, self._v[0] - U)

    # ── Metrics ──────────────────────────────────────────────────

    def norm_squared(self) -> int:
        """‖v₁₄‖² — squared norm of the 14 independent components."""
        return sum(x * x for x in self._v[:14])

    def distance_squared(self, other: Hybit) -> int:
        """‖Δ(h₁, h₂)‖² — squared Euclidean distance (14D)."""
        return sum((self._v[i] - other._v[i]) ** 2 for i in range(14))

    def layered_distance(self, other: Hybit) -> Dict[str, int]:
        """
        Per-layer squared distance (Keuntungan 2, §3.11).

        Returns dict with Δ_Θ², ‖Δ_N‖², ‖Δ_K‖², ‖Δ_Q‖², and total.
        """
        d_theta = (self._v[0] - other._v[0]) ** 2
        d_N = sum((self._v[i] - other._v[i]) ** 2 for i in range(1, 4))
        d_K = sum((self._v[i] - other._v[i]) ** 2 for i in range(4, 9))
        d_Q = sum((self._v[i] - other._v[i]) ** 2 for i in range(9, 14))
        return {
            "delta_theta_sq": d_theta,
            "delta_N_sq": d_N,
            "delta_K_sq": d_K,
            "delta_Q_sq": d_Q,
            "total_sq": d_theta + d_N + d_K + d_Q,
        }

    # ── Exomatrix ────────────────────────────────────────────────

    def exomatrix(self) -> List[List[int]]:
        """Build 5×5 exomatrix (Definition 2.44.1)."""
        return build_exomatrix(self._v)

    # ── Display ──────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"Hybit({list(self._v)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Hybit):
            return NotImplemented
        return self._v == other._v

    def __hash__(self) -> int:
        return hash(self._v)

    def to_list(self) -> List[int]:
        """Return the vector as a plain list."""
        return list(self._v)
