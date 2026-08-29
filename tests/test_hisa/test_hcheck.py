"""Tests for HCHECK runtime integrity monitor — Bab III §3.31."""

from hijaiyyah.core.master_table import MASTER_TABLE
from hijaiyyah.hisa.hcheck import HCHECK


class TestHCHECK:
    def test_clean_state(self):
        """All-zero registers should pass."""
        checker = HCHECK(interval=10)
        hreg = [[0] * 18 for _ in range(16)]
        report = checker.scan(hreg)
        assert report.clean
        assert report.corruptions_found == 0

    def test_valid_register(self):
        """Valid hybit in register should pass."""
        checker = HCHECK()
        ba = MASTER_TABLE.get_by_char("ب")
        assert ba is not None
        hreg = [[0] * 18 for _ in range(16)]
        hreg[0] = list(ba.vector)
        report = checker.scan(hreg)
        assert report.clean

    def test_negative_component_detected(self):
        """Negative component (bit flip) should be caught."""
        checker = HCHECK()
        hreg = [[0] * 18 for _ in range(16)]
        hreg[3] = [-1] + [0] * 17  # Corrupted register
        report = checker.scan(hreg)
        assert not report.clean
        assert report.corruptions_found == 1
        assert "negative" in report.details[0].lower()

    def test_corrupted_guard_detected(self):
        """Register with broken guard should be caught."""
        checker = HCHECK()
        hreg = [[0] * 18 for _ in range(16)]
        # Create vector with valid aggregates but wrong guard
        hreg[5] = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 99, 0, 1, 0]
        # A_N(idx14)=99 but Na+Nb+Nd=0 → G1 fail
        report = checker.scan(hreg)
        assert not report.clean

    def test_should_scan_interval(self):
        checker = HCHECK(interval=100)
        assert not checker.should_scan(0)
        assert not checker.should_scan(50)
        assert checker.should_scan(100)
        assert not checker.should_scan(150)
        assert checker.should_scan(200)

    def test_disabled_scan(self):
        checker = HCHECK(interval=0)
        assert not checker.should_scan(100)

    def test_scan_count(self):
        checker = HCHECK()
        hreg = [[0] * 18 for _ in range(16)]
        checker.scan(hreg)
        checker.scan(hreg)
        assert checker.total_scans == 2
        assert checker.total_corruptions == 0
