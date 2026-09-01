"""Tests for .hgeo format — Bab III §3.26."""

import os
import tempfile

from hijaiyyah.core.hgeo import HgeoFile, read_hgeo, write_hgeo
from hijaiyyah.core.master_table import MASTER_TABLE


class TestHgeoFile:
    def test_from_codex_entry_ba(self):
        entry = MASTER_TABLE.get_by_char("ب")
        assert entry is not None
        hgeo = HgeoFile.from_codex_entry(entry)
        assert hgeo.v18 == list(entry.vector)
        assert hgeo.measurement.theta_hat == 2
        assert hgeo.guard_status["G1"] == "PASS"
        assert hgeo.guard_status["G4"] == "PASS"
        assert hgeo.guard_status["T1"] == "PASS"
        assert hgeo.guard_status["T2"] == "PASS"
        assert hgeo.digest.startswith("sha256:")

    def test_all_28_letters(self):
        for entry in MASTER_TABLE.all_entries():
            hgeo = HgeoFile.from_codex_entry(entry)
            assert all(v == "PASS" for v in hgeo.guard_status.values()), \
                f"Guard FAIL for {entry.char}"

    def test_roundtrip_dict(self):
        entry = MASTER_TABLE.get_by_char("ب")
        assert entry is not None
        hgeo = HgeoFile.from_codex_entry(entry)
        d = hgeo.to_dict()
        restored = HgeoFile.from_dict(d)
        assert restored.v18 == hgeo.v18
        assert restored.measurement.theta_hat == hgeo.measurement.theta_hat

    def test_roundtrip_file(self):
        entry = MASTER_TABLE.get_by_char("ب")
        assert entry is not None
        hgeo = HgeoFile.from_codex_entry(entry)

        with tempfile.NamedTemporaryFile(suffix=".hgeo", delete=False, mode="w") as f:
            path = f.name

        try:
            write_hgeo(path, hgeo)
            restored = read_hgeo(path)
            assert restored.v18 == hgeo.v18
            assert restored.glyph_name == "ب"
        finally:
            os.unlink(path)
