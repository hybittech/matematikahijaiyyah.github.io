"""CodexEntry: the fundamental data type for a single letter's codex."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True, slots=True)
class CodexEntry:
    """
    Immutable representation of one letter's 18D codex vector.

    Fields:
      index:  0-based position in H28 (0 = Alif, 27 = Ya)
      char:   Hijaiyyah character (e.g., 'ب')
      name:   Latin transliteration (e.g., 'Ba')
      vector: 18-element tuple of non-negative integers
    """

    index: int
    char: str
    name: str
    vector: Tuple[int, ...]

    def __post_init__(self) -> None:
        assert len(self.vector) == 18, f"Vector must have 18 components, got {len(self.vector)}"
        assert all(v >= 0 for v in self.vector), "All components must be non-negative"

    # ── Component access ─────────────────────────────────────────

    @property
    def theta_hat(self) -> int:
        return self.vector[0]

    @property
    def na(self) -> int:
        return self.vector[1]

    @property
    def nb(self) -> int:
        return self.vector[2]

    @property
    def nd(self) -> int:
        return self.vector[3]

    @property
    def kp(self) -> int:
        return self.vector[4]

    @property
    def kx(self) -> int:
        return self.vector[5]

    @property
    def ks(self) -> int:
        return self.vector[6]

    @property
    def ka(self) -> int:
        return self.vector[7]

    @property
    def kc(self) -> int:
        return self.vector[8]

    @property
    def qp(self) -> int:
        return self.vector[9]

    @property
    def qx(self) -> int:
        return self.vector[10]

    @property
    def qs(self) -> int:
        return self.vector[11]

    @property
    def qa(self) -> int:
        return self.vector[12]

    @property
    def qc(self) -> int:
        return self.vector[13]

    @property
    def a_n(self) -> int:
        return self.vector[14]

    @property
    def a_k(self) -> int:
        return self.vector[15]

    @property
    def a_q(self) -> int:
        return self.vector[16]

    @property
    def h_star(self) -> int:
        return self.vector[17]

    # ── Derived quantities ───────────────────────────────────────

    @property
    def U(self) -> int:
        """U(h) = Qx + Qs + Qa + 4·Qc"""
        return self.qx + self.qs + self.qa + 4 * self.qc

    @property
    def rho(self) -> int:
        """ρ(h) = Θ̂ − U"""
        return self.theta_hat - self.U
