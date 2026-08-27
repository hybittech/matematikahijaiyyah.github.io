"""Every shipped copy of the Master Table must agree with the canonical one.

The Master Table lives in several places so that Python, the hardware ROM and
the web GUI can each read it natively. They are copies, not caches, so nothing
stops them drifting apart — and once they do, each side keeps passing its own
tests while validating a different alphabet.

That is exactly what happened: data/hm28.json disagreed with the canonical table
on Tha, Zha, Kaf and Nun. The HCPU ROM is generated from that JSON, so silicon
ran a different alphabet than the test suite, and Kaf's corrupted entry violated
guard T2 — which was then masked by an is_kaf override in rtl/hcpu_guard.v.

These tests pin every copy to core.master_table so the drift cannot recur.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Dict, List

import pytest

from hijaiyyah.core.guards import full_guard_check
from hijaiyyah.core.master_table import MASTER_TABLE

ROOT = Path(__file__).resolve().parents[2]

CSV_COLUMNS = [
    "Theta_Hat", "Na", "Nb", "Nd",
    "Kp", "Kx", "Ks", "Ka", "Kc",
    "Qp", "Qx", "Qs", "Qa", "Qc",
    "An", "Ak", "Aq", "H_Star",
]


def canonical() -> Dict[int, List[int]]:
    """The single source of truth: {letter index -> 18D vector}."""
    return {e.index: list(e.vector) for e in MASTER_TABLE.all_entries()}


# ── data/hm28.csv ────────────────────────────────────────────────

def test_csv_matches_canonical() -> None:
    with open(ROOT / "data" / "hm28.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 28
    expected = canonical()
    for row in rows:
        idx = int(row["#"])
        vector = [int(row[c]) for c in CSV_COLUMNS]
        assert vector == expected[idx], f"hm28.csv row {idx} ({row['Huruf']}) drifted"


def test_csv_derived_columns_follow_the_formula() -> None:
    """U and rho are derived, so a hand-edited CSV must not contradict them."""
    with open(ROOT / "data" / "hm28.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        v = [int(row[c]) for c in CSV_COLUMNS]
        u = v[10] + v[11] + v[12] + 4 * v[13]
        assert int(row["U_Value"]) == u, f"{row['Huruf']}: U column contradicts U=Qx+Qs+Qa+4Qc"
        assert int(row["Rho"]) == v[0] - u, f"{row['Huruf']}: Rho column contradicts rho=theta-U"


# ── data/hm28.json (source of the HCPU ROM) ──────────────────────

def json_document() -> dict:
    with open(ROOT / "data" / "hm28.json", encoding="utf-8") as f:
        return json.load(f)


def test_json_matches_canonical() -> None:
    doc = json_document()
    expected = canonical()

    assert doc["letter_count"] == 28
    assert doc["dimensions"] == 18
    assert len(doc["data"]) == 28

    for name, entry in doc["data"].items():
        idx = entry["index"]
        assert entry["vector"] == expected[idx], f"hm28.json entry {name} drifted"


def test_json_seal_matches_computed_seal() -> None:
    """A stale seal means the file was edited without regenerating it."""
    assert json_document()["sha256"] == MASTER_TABLE.compute_sha256()


def test_json_agrees_with_manifest_hash() -> None:
    with open(ROOT / "data" / "hm28_manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["dataset_hash"] == MASTER_TABLE.compute_sha256()


# ── rtl/hcpu_rom.v (what the silicon actually reads) ─────────────

ROM_ENTRY = re.compile(r"5'd(\d+):\s*data_out\s*=\s*\{(.*?)\};", re.S)


def verilog_rom() -> Dict[int, List[int]]:
    text = (ROOT / "rtl" / "hcpu_rom.v").read_text(encoding="utf-8")
    rom: Dict[int, List[int]] = {}
    for addr, body in ROM_ENTRY.findall(text):
        words = re.findall(r"8'd(\d+)", body)
        # Verilog packs {comp[17], ..., comp[0]}, so unpack in reverse.
        rom[int(addr)] = [int(w) for w in reversed(words)]
    return rom


def test_verilog_rom_matches_canonical() -> None:
    rom = verilog_rom()
    for idx, vector in canonical().items():
        assert idx in rom, f"hcpu_rom.v is missing letter {idx}"
        assert rom[idx] == vector, f"hcpu_rom.v entry {idx} drifted"


def test_verilog_rom_holds_no_undeclared_letters() -> None:
    """Index 31 is a deliberate guard-failure vector; nothing else may hide here."""
    extra = set(verilog_rom()) - set(canonical())
    assert extra == {31}, f"unexpected ROM addresses: {sorted(extra - {31})}"


# ── hm28.rom (nibble-packed binary) ──────────────────────────────

def test_binary_rom_matches_canonical() -> None:
    from hijaiyyah.core.rom import pack_rom

    packed = pack_rom([list(e.vector) for e in MASTER_TABLE.all_entries()])
    assert (ROOT / "hm28.rom").read_bytes() == packed


# ── hom-gui/src/engine/masterTable.js ────────────────────────────

GUI_ROW = re.compile(r"v18:\s*\[([0-9,\s]+)\]")


def test_gui_table_matches_canonical() -> None:
    """The GUI must use the canonical ordering [.., Qc, AN, AK, AQ, H*]."""
    path = ROOT / "hom-gui" / "src" / "engine" / "masterTable.js"
    if not path.exists():                                     # pragma: no cover
        pytest.skip("hom-gui not present")

    rows = GUI_ROW.findall(path.read_text(encoding="utf-8"))
    assert len(rows) == 28, f"expected 28 GUI rows, found {len(rows)}"

    expected = canonical()
    for i, row in enumerate(rows, start=1):
        vector = [int(x) for x in row.split(",")]
        assert vector == expected[i], f"masterTable.js row {i} drifted"


# ── guards hold everywhere, with no per-letter exceptions ────────

def test_every_letter_passes_every_guard() -> None:
    for entry in MASTER_TABLE.all_entries():
        status = full_guard_check(list(entry.vector))
        failed = [k for k, ok in status.items() if k != "all_pass" and not ok]
        assert not failed, f"{entry.name} ({entry.char}) fails {failed}"


def test_kaf_satisfies_t2_without_an_exception() -> None:
    """Kaf is Angular Khatt (Ka), not Closed-Loop (Kc), so T2 is vacuous.

    Guards against reintroducing the corrupted Kc=1 encoding that once forced
    an is_kaf override into the hardware guard checker.
    """
    kaf = MASTER_TABLE.get_by_char("ك")
    assert kaf is not None
    assert kaf.vector[7] == 1, "Kaf must carry Ka=1 (Angular Khatt)"
    assert kaf.vector[8] == 0, "Kaf must carry Kc=0 — Kc belongs to Mim and Haa"
    assert full_guard_check(list(kaf.vector))["T2"]


def test_hardware_guard_has_no_letter_specific_override() -> None:
    """No guard may be special-cased for one letter — that hides bad data."""
    source = (ROOT / "rtl" / "hcpu_guard.v").read_text(encoding="utf-8")
    for line in source.splitlines():
        code = line.split("//", 1)[0]
        assert "is_kaf" not in code, "letter-specific guard override reintroduced"
