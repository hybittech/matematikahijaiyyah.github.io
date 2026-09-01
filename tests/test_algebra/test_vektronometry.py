"""Tests for Field 1: Vectronometry (Bab II-A, Ch 17-21)."""



class TestPrimitiveRatios:
    def test_sum_equals_one(self, hm, all_entries):
        pr = hm["vectronometry"]["primitive_ratios"]
        for e in all_entries:
            v = list(e.vector)
            if v[14] + v[15] + v[16] == 0:
                continue
            r = pr(e)
            total = r["r_N"] + r["r_K"] + r["r_Q"]
            assert abs(total - 1.0) < 1e-9, f"{e.char}: sum={total}"


class TestPythagorean:
    def test_all_28(self, hm, all_entries):
        pc = hm["vectronometry"]["pythagorean_check"]
        for e in all_entries:
            r = pc(e)
            assert r["pass"], f"{e.char}: lhs={r['lhs']} rhs={r['rhs']}"


class TestNorm:
    def test_alif_norm_is_one(self, hm, alif):
        assert hm["vectronometry"]["norm2"](alif) == 1

    def test_haa_norm_is_69(self, hm, haa):
        assert hm["vectronometry"]["norm2"](haa) == 69


class TestCosine:
    def test_non_negative(self, hm, all_entries):
        cos = hm["vectronometry"]["cosine"]
        for i, e1 in enumerate(all_entries):
            for e2 in all_entries[i:]:
                assert cos(e1, e2) >= 0
