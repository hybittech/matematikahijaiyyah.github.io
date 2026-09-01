"""Tests for HAR registry — Bab III §3.27."""

import os
import tempfile

from hijaiyyah.core.har import HARRegistry


class TestHARRegistry:
    def test_generate_har001(self):
        registry = HARRegistry()
        data = registry.generate_har001()

        assert data["meta"]["har_id"] == "HAR-001"
        assert data["meta"]["name"] == "Hijaiyyah"
        assert data["meta"]["letter_count"] == 28
        assert data["meta"]["status"] == "CERTIFIED"

    def test_guard_report_all_pass(self):
        registry = HARRegistry()
        data = registry.generate_har001()

        gr = data["guard_report"]
        assert gr["total_checks"] == 28
        assert gr["passed"] == 28
        assert gr["failed"] == 0
        assert gr["all_pass"] is True

    def test_inject_report(self):
        registry = HARRegistry()
        data = registry.generate_har001()

        ir = data["inject_report"]
        assert ir["total_pairs"] == 378  # C(28,2)
        assert ir["unique_vectors"] == 28
        assert ir["is_injective"] is True

    def test_certificate(self):
        registry = HARRegistry()
        data = registry.generate_har001()

        cert = data["certificate"]
        assert cert["har_id"] == "HAR-001"
        assert cert["guard_report_pass"] is True
        assert cert["inject_report_pass"] is True
        assert len(cert["certificate_sha256"]) == 64  # SHA-256 hex
        assert len(cert["master_table_sha256"]) == 64
        assert len(cert["rom_sha256"]) == 64

    def test_write_to_directory(self):
        registry = HARRegistry()
        with tempfile.TemporaryDirectory() as tmpdir:
            har_dir = os.path.join(tmpdir, "har")
            os.makedirs(har_dir)
            registry.write_to_directory(har_dir)

            assert os.path.exists(os.path.join(har_dir, "manifest.json"))
            assert os.path.exists(os.path.join(har_dir, "HAR-001", "meta.json"))
            assert os.path.exists(os.path.join(har_dir, "HAR-001", "master_table.json"))
            assert os.path.exists(os.path.join(har_dir, "HAR-001", "master_table.rom"))
            assert os.path.exists(os.path.join(har_dir, "HAR-001", "certificate.json"))
            validation = os.path.join(har_dir, "HAR-001", "validation")
            assert os.path.exists(os.path.join(validation, "guard_report.json"))
            assert os.path.exists(os.path.join(validation, "inject_report.json"))

            # Verify ROM size
            rom_path = os.path.join(har_dir, "HAR-001", "master_table.rom")
            assert os.path.getsize(rom_path) == 252
