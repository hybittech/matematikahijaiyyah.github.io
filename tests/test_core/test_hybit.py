"""Tests for the Hybit class — Bab III §3.1–3.9."""

import pytest

from hijaiyyah.core.hybit import Hybit
from hijaiyyah.core.master_table import MASTER_TABLE


class TestHybitCreation:
    """Definition 3.1.1: Hybit as element of V ⊂ ℕ₀¹⁸."""

    def test_from_char_ba(self):
        h = Hybit.from_char("ب")
        assert h is not None
        assert h.theta_hat == 2
        assert h.v == (2, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0)

    def test_from_char_invalid(self):
        assert Hybit.from_char("X") is None

    def test_from_vector_valid(self):
        v = [2, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0]
        h = Hybit.from_vector(v)
        assert h.is_valid()

    def test_from_vector_invalid_rejects(self):
        bad = [0] * 18
        bad[14] = 99  # A_N mismatch
        with pytest.raises(ValueError, match="guard check"):
            Hybit.from_vector(bad)

    def test_from_vector_negative_rejects(self):
        bad = [-1] + [0] * 17
        with pytest.raises(ValueError, match="non-negative"):
            Hybit.from_vector(bad)

    def test_from_vector_wrong_length(self):
        with pytest.raises(ValueError, match="18 components"):
            Hybit.from_vector([0] * 10)

    def test_zero(self):
        z = Hybit.zero()
        assert z.v == tuple([0] * 18)
        assert z.is_valid()

    def test_all_28_letters(self):
        for entry in MASTER_TABLE.all_entries():
            h = Hybit.from_char(entry.char)
            assert h is not None, f"Failed for {entry.char}"
            assert h.is_valid(), f"Invalid hybit for {entry.char}"


class TestMonoidCADD:
    """Proposition 3.2.1: (V, +) is a constrained commutative monoid."""

    def test_closure(self):
        """h₁ + h₂ ∈ V for all valid hybits."""
        h1 = Hybit.from_char("ب")
        h2 = Hybit.from_char("س")
        assert h1 is not None and h2 is not None
        result = h1 + h2
        assert result.is_valid()

    def test_identity(self):
        """0⃗ + h = h for identity element."""
        h = Hybit.from_char("ب")
        z = Hybit.zero()
        assert h is not None
        assert (z + h) == h
        assert (h + z) == h

    def test_associative(self):
        """(h₁ + h₂) + h₃ = h₁ + (h₂ + h₃)."""
        h1 = Hybit.from_char("ب")
        h2 = Hybit.from_char("س")
        h3 = Hybit.from_char("م")
        assert h1 is not None and h2 is not None and h3 is not None
        assert (h1 + h2) + h3 == h1 + (h2 + h3)

    def test_commutative(self):
        """h₁ + h₂ = h₂ + h₁."""
        h1 = Hybit.from_char("ب")
        h2 = Hybit.from_char("م")
        assert h1 is not None and h2 is not None
        assert h1 + h2 == h2 + h1

    def test_preserves_theta_identity(self):
        """Θ̂ = U + ρ preserved under addition (Theorem 3.9.1)."""
        h1 = Hybit.from_char("ب")
        h2 = Hybit.from_char("س")
        h3 = Hybit.from_char("م")
        assert h1 is not None and h2 is not None and h3 is not None

        agg = h1 + h2 + h3
        U, rho = agg.decompose()
        assert agg.theta_hat == U + rho
        assert rho >= 0

    def test_string_bismi(self):
        """Cod₁₈(بسم) = v₁₈(ب) + v₁₈(س) + v₁₈(م) — §3.11 example."""
        h_ba = Hybit.from_char("ب")
        h_sin = Hybit.from_char("س")
        h_mim = Hybit.from_char("م")
        assert h_ba is not None and h_sin is not None and h_mim is not None

        cod = h_ba + h_sin + h_mim
        # Θ̂ = 2 + 4 + 4 = 10
        assert cod.theta_hat == 10
        U, rho = cod.decompose()
        # U(بسم) = U(ب)+U(س)+U(م) = 0+2+4 = 6
        assert U == 6
        # ρ = 10 - 6 = 4
        assert rho == 4
        assert cod.theta_hat == U + rho


class TestProjections:
    def test_project_theta(self):
        h = Hybit.from_char("ب")
        assert h is not None
        proj = h.project("theta")
        assert proj[0] == 2
        assert all(proj[i] == 0 for i in range(1, 18))

    def test_project_N(self):
        h = Hybit.from_char("ب")
        assert h is not None
        proj = h.project("N")
        assert proj[3] == 1  # Nd=1 for ب
        assert proj[0] == 0  # theta not in N

    def test_project_K(self):
        h = Hybit.from_char("ب")
        assert h is not None
        proj = h.project("K")
        assert proj[5] == 1  # Kx=1 for ب

    def test_project_Q(self):
        h = Hybit.from_char("ب")
        assert h is not None
        proj = h.project("Q")
        assert proj[9] == 1  # Qp=1 for ب


class TestMetrics:
    def test_norm_squared(self):
        h = Hybit.from_char("ب")
        assert h is not None
        n2 = h.norm_squared()
        v = list(h.v[:14])
        assert n2 == sum(x * x for x in v)

    def test_distance_symmetry(self):
        h1 = Hybit.from_char("ب")
        h2 = Hybit.from_char("ت")
        assert h1 is not None and h2 is not None
        assert h1.distance_squared(h2) == h2.distance_squared(h1)

    def test_layered_distance(self):
        h1 = Hybit.from_char("ب")
        h2 = Hybit.from_char("ت")
        assert h1 is not None and h2 is not None
        ld = h1.layered_distance(h2)
        assert ld["total_sq"] == h1.distance_squared(h2)
        assert ld["total_sq"] == (
            ld["delta_theta_sq"] + ld["delta_N_sq"] + ld["delta_K_sq"] + ld["delta_Q_sq"]
        )


class TestExomatrix:
    def test_exomatrix_shape(self):
        h = Hybit.from_char("ب")
        assert h is not None
        exo = h.exomatrix()
        assert len(exo) == 5
        assert all(len(row) == 5 for row in exo)

    def test_exomatrix_theta_row(self):
        h = Hybit.from_char("ب")
        assert h is not None
        exo = h.exomatrix()
        # Row 0: [Θ̂, U, ρ, 0, 0]
        assert exo[0][0] == 2  # Θ̂
        assert exo[0][1] == 0  # U
        assert exo[0][2] == 2  # ρ


class TestEquality:
    def test_equal(self):
        h1 = Hybit.from_char("ب")
        h2 = Hybit.from_char("ب")
        assert h1 == h2

    def test_not_equal(self):
        h1 = Hybit.from_char("ب")
        h2 = Hybit.from_char("ت")
        assert h1 != h2

    def test_hashable(self):
        h1 = Hybit.from_char("ب")
        h2 = Hybit.from_char("ب")
        assert h1 is not None and h2 is not None
        s = {h1, h2}
        assert len(s) == 1
