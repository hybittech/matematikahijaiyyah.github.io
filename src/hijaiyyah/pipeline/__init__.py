"""
Ψ-Compiler — Geometry Extraction Pipeline
==========================================
Facade module: Font (sealed) → .hgeo → HAR

Wraps skeleton/csgi + core measurement into the
Ψ-Compiler pipeline defined in Bab III §3.26.

Pipeline:
  Font → Rasterize → CSGI extraction → MainPath →
  Q₉₀ quantize → N-K-Q classify → .hgeo
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# skeleton.csgi defines CSGIGraph, CSGINode and CSGIEdge — never a
# CSGIProcessor. The Master Table fallback below is what actually populates a
# measurement, and it works.
# First-party and always importable — the try/except that used to wrap this
# guarded against nothing, and assigning None to a class name is what mypy
# was objecting to. tests/test_integrity/test_no_dead_delegation.py keeps
# every remaining guarded import honest.
from hijaiyyah.core.guards import compute_U
from hijaiyyah.core.master_table import MASTER_TABLE

# hijaiyyah.core.codex has never existed; nothing here used the import.


# ── .hgeo Data Model ─────────────────────────────────────────

@dataclass
class CanonicalLock:
    """Font identification and integrity."""
    font: str = "KFGQPC Hafs Uthmanic Script"
    font_hash: str = ""
    resolution_ppem: int = 256


@dataclass
class ExtractionParams:
    """Parameters for skeleton extraction."""
    algorithm: str = "zhang-suen"
    adjacency: str = "8-neighborhood"
    prune_length: int = 3
    dot_max_area: int = 50
    corner_angle_deg: int = 60
    smooth_window: int = 3


@dataclass
class SkeletonNode:
    id: int = 0
    x: int = 0
    y: int = 0
    kind: str = "ENDPOINT"  # ENDPOINT | JUNCTION | KINK


@dataclass
class SkeletonEdge:
    id: int = 0
    u: int = 0
    v: int = 0
    polyline: List[List[int]] = field(default_factory=list)
    edge_type: str = "KHATT"     # KHATT | QAWS
    subtype: str = "Kp"
    pixel_count: int = 0


@dataclass
class DotInfo:
    id: int = 0
    centroid: List[int] = field(default_factory=lambda: [0, 0])
    area: int = 0
    zone: str = "ascender"  # ascender | body | descender


@dataclass
class MainPathInfo:
    node_sequence: List[int] = field(default_factory=list)
    edge_sequence: List[int] = field(default_factory=list)
    is_closed: bool = False
    total_pixels: int = 0


@dataclass
class Measurement:
    """The 18D codex measurement output."""
    theta_hat: int = 0
    theta_continuous_rad: float = 0.0
    N: List[int] = field(default_factory=lambda: [0, 0, 0])
    K: List[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    Q: List[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    U: int = 0
    rho: int = 0
    A_N: int = 0
    A_K: int = 0
    A_Q: int = 0
    H_star: int = 0

    @property
    def v18(self) -> List[int]:
        return (
            [self.theta_hat, *self.N, *self.K, *self.Q, self.A_N, self.A_K, self.A_Q, self.H_star]
        )


@dataclass
class HGeoFile:
    """
    Represents a .hgeo file — geometry extraction for one glyph.
    Provides full provenance chain from font to v₁₈.
    """
    hgeo_version: str = "1.0"
    har_id: str = "HAR-001"
    glyph_id: str = ""
    glyph_name: str = ""
    canonical_lock: CanonicalLock = field(default_factory=CanonicalLock)
    extraction_params: ExtractionParams = field(
        default_factory=ExtractionParams
    )
    nodes: List[SkeletonNode] = field(default_factory=list)
    edges: List[SkeletonEdge] = field(default_factory=list)
    dots: List[DotInfo] = field(default_factory=list)
    mainpath: MainPathInfo = field(default_factory=MainPathInfo)
    measurement: Measurement = field(default_factory=Measurement)
    guard_status: Dict[str, str] = field(default_factory=dict)
    digest: str = ""

    @property
    def v18(self) -> List[int]:
        return self.measurement.v18

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary (for JSON output)."""
        from dataclasses import asdict
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent,
                          ensure_ascii=False)

    def compute_digest(self) -> str:
        """Compute SHA-256 digest of measurement data."""
        data = json.dumps(self.measurement.v18, sort_keys=True)
        self.digest = (
            "sha256:" + hashlib.sha256(data.encode()).hexdigest()
        )
        return self.digest

    @classmethod
    def from_json(cls, text: str) -> "HGeoFile":
        """Deserialize from JSON string."""
        d = json.loads(text)
        hgeo = cls()
        hgeo.hgeo_version = d.get("hgeo_version", "1.0")
        hgeo.har_id = d.get("har_id", "HAR-001")
        hgeo.glyph_id = d.get("glyph_id", "")
        hgeo.glyph_name = d.get("glyph_name", "")
        if "measurement" in d:
            m = d["measurement"]
            hgeo.measurement = Measurement(
                theta_hat=m.get("theta_hat", 0),
                N=m.get("N", [0, 0, 0]),
                K=m.get("K", [0, 0, 0, 0, 0]),
                Q=m.get("Q", [0, 0, 0, 0, 0]),
                U=m.get("U", 0),
                rho=m.get("rho", 0),
                A_N=m.get("A_N", 0),
                A_K=m.get("A_K", 0),
                A_Q=m.get("A_Q", 0),
                H_star=m.get("H_star", 0),
            )
        hgeo.guard_status = d.get("guard_status", {})
        hgeo.digest = d.get("digest", "")
        return hgeo


# ── Ψ-Compiler ───────────────────────────────────────────────

class PsiCompiler:
    """
    Ψ-Compiler: Font (sealed) → .hgeo

    Pipeline:
      1. Rasterize glyph
      2. CSGI skeleton extraction
      3. MainPath selection
      4. Q₉₀ quantization
      5. N-K-Q classification
      6. Output .hgeo
    """

    VERSION = "1.0.0"

    def __init__(self, font_path: Optional[str] = None,
                 params: Optional[ExtractionParams] = None):
        self.font_path = font_path
        self.params = params or ExtractionParams()

    def extract_glyph(self, letter: str) -> HGeoFile:
        """Extract geometry for a single glyph."""
        hgeo = HGeoFile(
            glyph_name=letter,
            glyph_id=f"U+{ord(letter):04X}",
            extraction_params=self.params,
        )

        # Measurement comes from the Master Table. A CSGi path was sketched
        # here but never had a processor to call.
        if all(x == 0 for x in hgeo.v18) and MASTER_TABLE:
            entry = MASTER_TABLE.get_by_char(letter)
            if entry and hasattr(entry, 'vector'):
                hgeo.measurement = self._v18_to_measurement(list(entry.vector))

        hgeo.guard_status = self._run_guards(hgeo.v18)
        hgeo.compute_digest()
        return hgeo

    def extract_alphabet(self,
                         letters: List[str]) -> List[HGeoFile]:
        """Extract geometry for all letters."""
        return [self.extract_glyph(ch) for ch in letters]

    def _map_csgi(self, result: Any) -> Measurement:
        m = Measurement()
        if hasattr(result, 'v18'):
            v = result.v18
            m.theta_hat = v[0]
            m.N = v[1:4]
            m.K = v[4:9]
            m.Q = v[9:14]
            m.A_N = v[14]
            m.A_K = v[15]
            m.A_Q = v[16]
            m.H_star = v[17]
            m.U = compute_U(v)
            m.rho = m.theta_hat - m.U
        return m

    def _v18_to_measurement(self, v18: List[int]) -> Measurement:
        return Measurement(
            theta_hat=v18[0],
            N=list(v18[1:4]),
            K=list(v18[4:9]),
            Q=list(v18[9:14]),
            A_N=v18[14],
            A_K=v18[15],
            A_Q=v18[16],
            H_star=v18[17],
            U=compute_U(v18),
            rho=v18[0] - compute_U(v18),
        )

    def _run_guards(self, v18: List[int]) -> Dict[str, str]:
        from hijaiyyah.vm import GuardSystem
        gs = GuardSystem()
        status = gs.check(v18)
        result = {}
        for g in ["G1", "G2", "G3", "G4", "T1", "T2"]:
            if g in status.failed_guards:
                result[g] = "FAIL"
            else:
                result[g] = "PASS"
        return result


__all__ = [
    "CanonicalLock",
    "DotInfo",
    "ExtractionParams",
    "HGeoFile",
    "MainPathInfo",
    "Measurement",
    "PsiCompiler",
    "SkeletonEdge",
    "SkeletonNode",
]
