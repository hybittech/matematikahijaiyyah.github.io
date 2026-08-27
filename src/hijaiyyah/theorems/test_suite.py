"""Complete 13-test theorem suite (HC Spec v1.0)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ..algebra import aggregametric, exometric, intrametric, vektronometry
from ..core.guards import compute_U, guard_check, guard_detail
from ..core.master_table import MASTER_TABLE


@dataclass
class TestResult:
    ref: str
    name: str
    passed: bool
    message: str = ""


class TheoremTestSuite:
    def run_all(self) -> List[TestResult]:
        tests = [
            ("Axiom 9.4", "Guard check 28", self._guard),
            ("Thm 11.1", "Injectivity", self._inject),
            ("Ch 12", "Θ̂=U+ρ, ρ≥0", self._turning),
            ("Thm 25.2.1", "∫(uv)=∫u+∫v", self._integral_add),
            ("Thm 20.2.1", "Pythagorean", self._pyth),
            ("Thm 34.3.1", "Φ>‖v₁₄‖²", self._phi),
            ("Prop 31.1.1", "diam²=70", self._diam),
            ("Thm 18.2.1", "rN+rK+rQ=1", self._ratios),
            ("Thm 29.3.1", "Polarization", self._polar),
            ("Id 33.1.1", "Exomatrix R1-R5", self._exo),
            ("Thm 36.2.1", "Reconstruction", self._recon),
            ("Commut.", "Anagram", self._anagram),
            ("Axiom 9.4+", "Guard detail", self._guard_d),
        ]
        results = []
        for ref, name, fn in tests:
            try:
                fn()
                results.append(TestResult(ref, name, True))
            except AssertionError as e:
                results.append(TestResult(ref, name, False, str(e)))
            except Exception as e:
                results.append(TestResult(ref, name, False, f"ERROR: {e}"))
        return results

    def _entries(self):
        return MASTER_TABLE.all_entries()

    def _guard(self):
        for e in self._entries():
            assert guard_check(e), f"FAIL: {e.char}"

    def _inject(self):
        seen = {}
        for e in self._entries():
            k = tuple(e.vector)
            assert k not in seen, f"Collision: {e.char}"
            seen[k] = e.char

    def _turning(self):
        for e in self._entries():
            v = list(e.vector)
            U = compute_U(v)
            rho = v[0] - U
            assert rho >= 0 and v[0] == U + rho

    def _integral_add(self):
        bs = aggregametric.string_integral("بس")
        m = aggregametric.string_integral("م")
        bsm = aggregametric.string_integral("بسم")
        assert aggregametric.add_codex(bs, m)["cod18"] == bsm["cod18"]

    def _pyth(self):
        for e in self._entries():
            assert vektronometry.pythagorean_check(e)["pass"]

    def _phi(self):
        for e in self._entries():
            E = exometric.build(e)
            assert exometric.phi(E) > vektronometry.norm2(e)

    def _diam(self):
        assert intrametric.diameter_sq() == 70

    def _ratios(self):
        for e in self._entries():
            v = list(e.vector)
            if v[14] + v[15] + v[16] == 0:
                continue
            r = vektronometry.primitive_ratios(e)
            assert abs(r["r_N"] + r["r_K"] + r["r_Q"] - 1.0) < 1e-9

    def _polar(self):
        es = self._entries()
        for i, e1 in enumerate(es):
            for e2 in es[i + 1 :]:
                assert intrametric.polarization_check(e1, e2)["pass"]

    def _exo(self):
        for e in self._entries():
            assert exometric.audit(exometric.build(e))["all_pass"]

    def _recon(self):
        for e in self._entries():
            v = list(e.vector)
            v2 = exometric.reconstruct(exometric.build(e))
            assert v == v2, f"{e.char}"

    def _anagram(self):
        bsm = aggregametric.string_integral("بسم")["cod18"]
        sbm = aggregametric.string_integral("سبم")["cod18"]
        assert bsm == sbm

    def _guard_d(self):
        for e in self._entries():
            d = guard_detail(e)
            assert d["all_pass"], f"{e.char}"
