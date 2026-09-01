"""Tests for HAR — Alphabet Registry."""

import pytest

from hijaiyyah.har import (
    HAREntry,
    HARRegistry,
    HARStatus,
    HARValidation,
)


class TestHARImport:

    def test_import_registry(self):
        assert HARRegistry is not None

    def test_import_entry(self):
        assert HAREntry is not None

    def test_import_status(self):
        assert HARStatus.CERTIFIED is not None
        assert HARStatus.PENDING is not None


class TestHAREntry:
    """Test HAREntry dataclass."""

    def test_create(self):
        entry = HAREntry(id="HAR-001", name="Hijaiyyah")
        assert entry.id == "HAR-001"

    def test_lookup(self):
        entry = HAREntry(
            id="HAR-001",
            master_table={"ا": [0]*18, "ب": [2]+[0]*17},
        )
        assert entry.lookup("ا") == [0]*18
        assert entry.lookup("ب")[0] == 2
        assert entry.lookup("X") is None

    def test_v14(self):
        v18 = [2, 0,0,1, 0,1,0,0,0, 1,0,0,0,0, 1,1,1, 0]
        entry = HAREntry(master_table={"ب": v18})
        v14 = entry.lookup_v14("ب")
        assert len(v14) == 14
        assert v14[0] == 2

    def test_hash(self):
        entry = HAREntry(master_table={"ا": [0]*18})
        h = entry.compute_hash()
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256 hex


class TestHARValidation:

    def test_all_pass(self):
        v = HARValidation(
            guard_pass=28, guard_total=28,
            inject_unique=378, inject_total=378,
            r1r5_pass=140, r1r5_total=140,
            rank=14,
        )
        assert v.all_pass is True

    def test_fail_guard(self):
        v = HARValidation(
            guard_pass=27, guard_total=28,
            inject_unique=378, inject_total=378,
            r1r5_pass=140, r1r5_total=140,
            rank=14,
        )
        assert v.all_pass is False


class TestHARRegistry:
    """Test registry management."""

    def test_init(self):
        reg = HARRegistry()
        assert isinstance(reg, HARRegistry)

    def test_har001_loaded(self):
        """HAR-001 should auto-load from master_table."""
        reg = HARRegistry()
        if reg.has("HAR-001"):
            entry = reg.get("HAR-001")
            assert entry.name == "Hijaiyyah"
            assert entry.status == HARStatus.CERTIFIED
        else:
            pytest.skip("Master table not available for auto-load")

    def test_lookup(self):
        reg = HARRegistry()
        if reg.has("HAR-001"):
            v = reg.lookup("ا")
            assert v is not None
            assert len(v) == 18
        else:
            pytest.skip("HAR-001 not loaded")

    def test_list_registries(self):
        reg = HARRegistry()
        entries = reg.list_registries()
        assert isinstance(entries, list)

    def test_certified_list(self):
        reg = HARRegistry()
        certs = reg.certified
        assert isinstance(certs, list)

    def test_nonexistent_har(self):
        reg = HARRegistry()
        assert reg.get("HAR-999") is None
        assert reg.lookup("ا", "HAR-999") is None
