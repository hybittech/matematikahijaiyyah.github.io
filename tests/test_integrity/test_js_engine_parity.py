"""
Parity between the JS engine and the Python implementation.

hom-gui/src/engine/ is a hand-written re-implementation of
src/hijaiyyah/algebra/ and src/hijaiyyah/core/guards.py, shipped to the public
site. test_dataset_consistency.py already pins the *table* the two share; this
module pins the *formulas*. Without it, a fix applied to the Python side can
silently miss the JS side and nothing turns red.

The JS half runs under node via js_parity_driver.mjs, which dumps every value
the engine computes as JSON. Everything here is a diff against that dump.
"""

from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List

import pytest

from hijaiyyah.algebra import aggregametric as agm
from hijaiyyah.algebra import exometric as exm
from hijaiyyah.algebra import intrametric as itm
from hijaiyyah.algebra import vektronometry as vtm
from hijaiyyah.core.exomatrix import build_exomatrix
from hijaiyyah.core.guards import compute_rho, compute_U, guard_check, guard_detail
from hijaiyyah.core.master_table import MASTER_TABLE

ROOT = Path(__file__).resolve().parents[2]
DRIVER = Path(__file__).parent / "js_parity_driver.mjs"

TOL = 1e-9

# Every canonical letter passes every guard, so the 28 real rows cannot
# distinguish a correct guard from one hardwired to `true`. These vectors
# each break exactly one rule, which is what makes the guard diff meaningful.
#   slots: [Θ̂, Na,Nb,Nd, Kp,Kx,Ks,Ka,Kc, Qp,Qx,Qs,Qa,Qc, AN,AK,AQ, H*]
_VALID = [4, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 2, 0]


def _mutate(**slots: int) -> List[int]:
    v = list(_VALID)
    for name, value in slots.items():
        v[_SLOT[name]] = value
    return v


_SLOT = {
    "theta": 0, "Na": 1, "Nb": 2, "Nd": 3,
    "Kp": 4, "Kx": 5, "Ks": 6, "Ka": 7, "Kc": 8,
    "Qp": 9, "Qx": 10, "Qs": 11, "Qa": 12, "Qc": 13,
    "AN": 14, "AK": 15, "AQ": 16, "Hstar": 17,
}

PROBES: List[List[int]] = [
    _VALID,                                              # nothing broken
    _mutate(AN=5),                                       # G1 / R2
    _mutate(AK=5),                                       # G2 / R3
    _mutate(AQ=5),                                       # G3 / R4
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0],   # G4: ρ = 1−8 < 0
    [4, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0],   # T1: Ks>0, Qc=0
    [4, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0],   # T2: Kc>0, Qc=0
    _mutate(AN=9, AK=9, AQ=9),                           # several at once
    [0] * 18,                                            # degenerate
]

# Locally, no node means these tests skip rather than block anyone. CI sets
# HOM_REQUIRE_NODE=1 so a runner without node fails loudly instead of quietly
# skipping the only check that pins the JS engine to the Python one.
pytestmark = pytest.mark.skipif(
    shutil.which("node") is None and os.environ.get("HOM_REQUIRE_NODE") != "1",
    reason="node is required to execute the JS engine",
)


@pytest.fixture(scope="module")
def js() -> Dict[str, Any]:
    """Run the JS engine once and hand back everything it computed."""
    proc = subprocess.run(
        ["node", str(DRIVER)],
        cwd=ROOT,
        input=json.dumps(PROBES),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, f"js_parity_driver.mjs failed:\n{proc.stderr}"
    return json.loads(proc.stdout)


def _entries() -> List[Any]:
    return MASTER_TABLE.all_entries()


def _v18(entry: Any) -> List[int]:
    return list(entry.vector)


# ── Master Table ─────────────────────────────────────────────────

def test_letter_order_and_vectors_agree(js: Dict[str, Any]) -> None:
    """The pairwise/per-letter diffs below only mean anything if the rows line up."""
    entries = _entries()
    assert len(js["letters"]) == len(entries) == 28
    for py_entry, js_letter in zip(js["letters"], entries, strict=True):
        assert py_entry["char"] == js_letter.char
        assert py_entry["v18"] == _v18(js_letter)


# ── guards.js vs core/guards.py ──────────────────────────────────

def test_guards_agree(js: Dict[str, Any]) -> None:
    """
    The two sides name the same checks differently. guards.js labels the
    sum-checks G1–G3 and the ρ≥0 cross-constraint G4; guard_detail() reports
    the same three sum-checks as audit relations R2–R4 and folds ρ≥0 into
    compute_rho(). T1/T2 are named alike on both sides.
    """
    for entry, js_letter in zip(_entries(), js["letters"], strict=True):
        v = _v18(entry)
        detail = guard_detail(v)
        expected = {
            "G1": detail["R2"],
            "G2": detail["R3"],
            "G3": detail["R4"],
            "G4": compute_rho(v) >= 0,
            "T1": detail["T1"],
            "T2": detail["T2"],
        }
        for gid, want in expected.items():
            assert js_letter["guards"][gid] == want, (
                f"{entry.char}: guard {gid} — python={want} "
                f"js={js_letter['guards'][gid]}"
            )
        assert all(js_letter["guards"].values()) == guard_check(v), (
            f"{entry.char}: overall guard verdict"
        )


# ── vektronometry.js vs algebra/vektronometry.py ─────────────────

def test_vektronometry_agrees(js: Dict[str, Any]) -> None:
    for entry, js_letter in zip(_entries(), js["letters"], strict=True):
        v = _v18(entry)
        r = js_letter["vtm"]
        pyth = vtm.pythagorean_check(entry)
        ratios = vtm.primitive_ratios(entry)

        assert r["norm2"] == vtm.norm2(entry), f"{entry.char}: norm2"
        assert r["theta"] == v[0], f"{entry.char}: theta"
        assert r["U"] == compute_U(v), f"{entry.char}: U"
        assert r["rho"] == compute_rho(v), f"{entry.char}: rho"
        assert [r["AN"], r["AK"], r["AQ"]] == v[14:17], f"{entry.char}: A-slots"

        assert r["normTheta"] == pyth["theta"], f"{entry.char}: normTheta"
        assert r["normN"] == pyth["N"], f"{entry.char}: normN"
        assert r["normK"] == pyth["K"], f"{entry.char}: normK"
        assert r["normQ"] == pyth["Q"], f"{entry.char}: normQ"
        assert r["pythagoras"] == pyth["pass"], f"{entry.char}: pythagoras"

        assert math.isclose(r["rN"], ratios["r_N"], abs_tol=TOL), f"{entry.char}: r_N"
        assert math.isclose(r["rK"], ratios["r_K"], abs_tol=TOL), f"{entry.char}: r_K"
        assert math.isclose(r["rQ"], ratios["r_Q"], abs_tol=TOL), f"{entry.char}: r_Q"


def test_composition_angle_agrees_after_unit_conversion(js: Dict[str, Any]) -> None:
    """Python returns radians, the GUI renders degrees — same angle either way."""
    for entry, js_letter in zip(_entries(), js["letters"], strict=True):
        py_deg = math.degrees(vtm.comp_angle(entry))
        assert math.isclose(js_letter["vtm"]["alpha"], py_deg, abs_tol=1e-9), (
            f"{entry.char}: alpha — python={py_deg}° js={js_letter['vtm']['alpha']}°"
        )


# ── exometric.js vs core/exomatrix.py + algebra/exometric.py ─────

def test_exomatrix_and_phi_agree(js: Dict[str, Any]) -> None:
    for entry, js_letter in zip(_entries(), js["letters"], strict=True):
        expected = build_exomatrix(entry)
        assert js_letter["exo"] == expected, f"{entry.char}: exomatrix"
        assert js_letter["phi"] == exm.phi(expected), f"{entry.char}: phi"


def test_audit_relations_agree(js: Dict[str, Any]) -> None:
    for entry, js_letter in zip(_entries(), js["letters"], strict=True):
        py_audit = exm.audit(build_exomatrix(entry))
        for rid in ("R1", "R2", "R3", "R4", "R5"):
            assert js_letter["audit"][rid] == py_audit[rid], f"{entry.char}: {rid}"


# ── intrametric.js / normivektor.js vs their Python twins ────────

def test_pairwise_metrics_agree(js: Dict[str, Any]) -> None:
    """All 378 unordered pairs, both distance modules at once."""
    entries = _entries()
    by_char = {e.char: e for e in entries}
    expected_pairs = list(combinations(entries, 2))
    assert len(js["pairs"]) == len(expected_pairs) == 378

    for js_pair, (pa, pb) in zip(js["pairs"], expected_pairs, strict=True):
        a, b = by_char[js_pair["a"]], by_char[js_pair["b"]]
        assert (a.char, b.char) == (pa.char, pb.char), "pair ordering drifted"

        assert js_pair["d2sq"] == itm.euclidean_sq(a, b), f"{a.char}-{b.char}: d2sq"
        assert js_pair["d1"] == itm.manhattan(a, b), f"{a.char}-{b.char}: d1"
        assert js_pair["dH"] == itm.hamming(a, b), f"{a.char}-{b.char}: dH"
        assert js_pair["inner"] == vtm.inner(a, b), f"{a.char}-{b.char}: inner"
        assert js_pair["polarization"], f"{a.char}-{b.char}: polarization identity"

        decomp = itm.distance_decomposition(a, b)
        assert js_pair["deltaTheta2"] == decomp["theta"], f"{a.char}-{b.char}: Δθ²"
        assert js_pair["deltaN2"] == decomp["N"], f"{a.char}-{b.char}: ΔN²"
        assert js_pair["deltaK2"] == decomp["K"], f"{a.char}-{b.char}: ΔK²"
        assert js_pair["deltaQ2"] == decomp["Q"], f"{a.char}-{b.char}: ΔQ²"
        assert js_pair["totalNorm2"] == decomp["total"], f"{a.char}-{b.char}: total"
        assert js_pair["decompValid"], f"{a.char}-{b.char}: decomposition"


def test_diameter_agrees(js: Dict[str, Any]) -> None:
    entries = _entries()
    py_diameter = max(itm.euclidean_sq(a, b) for a, b in combinations(entries, 2))
    assert math.isclose(js["diameter"], math.sqrt(py_diameter), abs_tol=TOL)

    a, b = js["diameterPair"]
    realized = itm.euclidean_sq(
        MASTER_TABLE.get_by_char(a), MASTER_TABLE.get_by_char(b)
    )
    assert realized == py_diameter, f"js diameter pair {a}-{b} is not a maximiser"


# ── synthetic violations ─────────────────────────────────────────

def test_guards_agree_on_synthetic_violations(js: Dict[str, Any]) -> None:
    """The canonical 28 all pass; these vectors are built to fail."""
    assert len(js["probes"]) == len(PROBES)
    for probe, v in zip(js["probes"], PROBES, strict=True):
        assert probe["v18"] == v, "probe ordering drifted"
        detail = guard_detail(v)
        expected = {
            "G1": detail["R2"],
            "G2": detail["R3"],
            "G3": detail["R4"],
            "G4": compute_rho(v) >= 0,
            "T1": detail["T1"],
            "T2": detail["T2"],
        }
        for gid, want in expected.items():
            assert probe["guards"][gid] == want, (
                f"{v}: guard {gid} — python={want} js={probe['guards'][gid]}"
            )
        assert all(probe["guards"].values()) == guard_check(v), f"{v}: verdict"


def test_probes_actually_exercise_every_guard() -> None:
    """Guard against the probe set going stale: each rule must fail somewhere."""
    failed: Dict[str, bool] = {g: False for g in ("G1", "G2", "G3", "G4", "T1", "T2")}
    for v in PROBES:
        detail = guard_detail(v)
        failed["G1"] |= not detail["R2"]
        failed["G2"] |= not detail["R3"]
        failed["G3"] |= not detail["R4"]
        failed["G4"] |= compute_rho(v) < 0
        failed["T1"] |= not detail["T1"]
        failed["T2"] |= not detail["T2"]
    unexercised = sorted(g for g, hit in failed.items() if not hit)
    assert not unexercised, f"no probe violates {unexercised}"


def test_derived_values_agree_on_synthetic_vectors(js: Dict[str, Any]) -> None:
    for probe, v in zip(js["probes"], PROBES, strict=True):
        assert probe["U"] == compute_U(v), f"{v}: U"
        assert probe["rho"] == compute_rho(v), f"{v}: rho"
        assert probe["norm2"] == sum(x * x for x in v[:14]), f"{v}: norm2"
        assert probe["exo"] == build_exomatrix(v), f"{v}: exomatrix"
        assert probe["phi"] == exm.phi(build_exomatrix(v)), f"{v}: phi"
        py_audit = exm.audit(build_exomatrix(v))
        for rid in ("R1", "R2", "R3", "R4", "R5"):
            assert probe["audit"][rid] == py_audit[rid], f"{v}: {rid}"


# ── aggregametric.js vs algebra/aggregametric.py ─────────────────

def test_string_integrals_agree(js: Dict[str, Any]) -> None:
    for js_str in js["strings"]:
        text = js_str["text"]
        cod = agm.string_integral(text)["cod18"]
        assert js_str["codex"] == cod, f"{text}: cod18"
        # Both engines key on the table's own glyph, so a character absent
        # from the table (plain ه, U+0647, vs the table's هـ) is skipped by
        # both. Compare the counts they actually agree on, not the raw length.
        assert js_str["letterCount"] == agm.string_integral(text)["length"], (
            f"{text}: letter count"
        )
        assert js_str["theta"] == cod[0], f"{text}: theta"
        assert js_str["U"] == compute_U(cod), f"{text}: U"
        assert js_str["rho"] == compute_rho(cod), f"{text}: rho"
        assert js_str["allPreserved"], f"{text}: identities not preserved"
