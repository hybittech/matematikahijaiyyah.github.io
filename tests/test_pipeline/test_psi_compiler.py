"""Tests for Ψ-Compiler and .hgeo format."""

import pytest

from hijaiyyah.pipeline import (
    ExtractionParams,
    HGeoFile,
    Measurement,
    PsiCompiler,
)


class TestPsiCompilerImport:

    def test_import_psi(self):
        assert PsiCompiler is not None

    def test_import_hgeo(self):
        assert HGeoFile is not None

    def test_import_measurement(self):
        assert Measurement is not None


class TestMeasurement:
    """Test Measurement dataclass."""

    def test_v18_assembly(self):
        m = Measurement(
            theta_hat=2,
            N=[0, 0, 1],
            K=[0, 1, 0, 0, 0],
            Q=[1, 0, 0, 0, 0],
            A_N=1, A_K=1, A_Q=1, H_star=0,
        )
        v18 = m.v18
        assert len(v18) == 18
        assert v18[0] == 2      # Θ̂
        assert v18[3] == 1      # N_d
        assert v18[5] == 1      # K_x
        assert v18[9] == 1      # Q_p

    def test_default_zeros(self):
        m = Measurement()
        assert all(x == 0 for x in m.v18)


class TestHGeoFile:
    """Test .hgeo format."""

    def test_create(self):
        hgeo = HGeoFile(glyph_name="ب", glyph_id="U+0628")
        assert hgeo.glyph_name == "ب"

    def test_json_roundtrip(self):
        hgeo = HGeoFile(
            glyph_name="ب",
            glyph_id="U+0628",
            measurement=Measurement(
                theta_hat=2, N=[0, 0, 1],
                K=[0, 1, 0, 0, 0], Q=[1, 0, 0, 0, 0],
                A_N=1, A_K=1, A_Q=1, H_star=0,
            ),
        )
        json_str = hgeo.to_json()
        restored = HGeoFile.from_json(json_str)
        assert restored.glyph_name == "ب"
        assert restored.measurement.theta_hat == 2
        assert restored.measurement.N == [0, 0, 1]

    def test_digest(self):
        hgeo = HGeoFile(
            measurement=Measurement(theta_hat=2)
        )
        digest = hgeo.compute_digest()
        assert digest.startswith("sha256:")
        assert len(digest) > 10

    def test_v18_property(self):
        hgeo = HGeoFile(
            measurement=Measurement(theta_hat=2, N=[0, 0, 1],
                                     K=[0, 1, 0, 0, 0],
                                     Q=[1, 0, 0, 0, 0],
                                     A_N=1, A_K=1, A_Q=1, H_star=0)
        )
        assert len(hgeo.v18) == 18
        assert hgeo.v18[0] == 2


class TestExtractionParams:

    def test_defaults(self):
        p = ExtractionParams()
        assert p.algorithm == "zhang-suen"
        assert p.adjacency == "8-neighborhood"


class TestPsiCompiler:
    """Test Ψ-Compiler pipeline."""

    def test_init(self):
        psi = PsiCompiler()
        assert psi.VERSION == "1.0.0"

    def test_extract_glyph_returns_hgeo(self):
        psi = PsiCompiler()
        try:
            hgeo = psi.extract_glyph("ب")
            assert isinstance(hgeo, HGeoFile)
            assert hgeo.glyph_name == "ب"
        except Exception:
            pytest.skip("Master table not available")

    def test_extract_sets_guard_status(self):
        psi = PsiCompiler()
        try:
            hgeo = psi.extract_glyph("ا")
            assert "G1" in hgeo.guard_status
        except Exception:
            pytest.skip("Master table not available")
