"""Test guard checks and audit detail for all 28 letters."""

from hijaiyyah.core.guards import compute_rho, compute_U, guard_check, guard_detail


class TestGuardCheck:
    def test_all_28_pass(self, all_entries):
        for e in all_entries:
            assert guard_check(e), f"Guard FAIL: {e.char} ({e.name})"

    def test_invalid_vector_rejected(self):
        bad = [0] * 18
        bad[14] = 99  # A_N = 99 but Na+Nb+Nd = 0
        assert not guard_check(bad)

    def test_negative_rho_rejected(self):
        bad = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0]
        # theta=1, Qc=1 → U=4, rho=1-4=-3 < 0
        assert not guard_check(bad)


class TestGuardDetail:
    def test_all_28_R1_through_R5(self, all_entries):
        for e in all_entries:
            d = guard_detail(e)
            for key in ("R1", "R2", "R3", "R4", "R5"):
                assert d[key], f"{e.char}: {key} failed"
            assert d["all_pass"]

    def test_detail_includes_U_and_rho(self, ba):
        d = guard_detail(ba)
        assert "U" in d
        assert "rho" in d
        assert d["rho"] == ba.theta_hat - d["U"]


class TestComputeU:
    def test_alif(self, alif):
        assert compute_U(list(alif.vector)) == 0

    def test_haa(self, haa):
        assert compute_U(list(haa.vector)) == 8  # 4*Qc = 4*2 = 8


class TestComputeRho:
    def test_non_negative_all_28(self, all_entries):
        for e in all_entries:
            rho = compute_rho(list(e.vector))
            assert rho >= 0, f"{e.char}: rho={rho}"
