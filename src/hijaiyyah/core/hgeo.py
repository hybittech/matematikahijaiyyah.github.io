"""
.hgeo — Hybit Geometry File.

Bab III §3.26: Stores geometry extraction results for one glyph.
Output of Ψ-Compiler, input to HAR assembly.

Provides full provenance chain: font → skeleton → measurement → v18.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class CanonicalLock:
    """Font provenance (§1.6.1 Bab I)."""
    font: str = ""
    font_hash: str = ""
    resolution_ppem: int = 256


@dataclass
class ExtractionParams:
    """CSGI algorithm parameters (§1.20.4 Bab I)."""
    algorithm: str = "zhang-suen"
    adjacency: str = "8-neighborhood"
    prune_length: int = 3
    corner_angle_deg: int = 60


@dataclass
class SkeletonNode:
    id: int = 0
    x: int = 0
    y: int = 0
    kind: str = "ENDPOINT"  # ENDPOINT, JUNCTION, BRANCH


@dataclass
class SkeletonEdge:
    id: int = 0
    u: int = 0
    v: int = 0
    type: str = "KHATT"     # KHATT or QAWS
    subtype: str = ""       # Kp, Kx, Ks, Ka, Kc / Qp, Qx, Qs, Qa, Qc


@dataclass
class DotInfo:
    id: int = 0
    centroid: List[int] = field(default_factory=lambda: [0, 0])
    zone: str = "above"     # above, below, descender


@dataclass
class MainPath:
    node_sequence: List[int] = field(default_factory=list)
    is_closed: bool = False
    total_pixels: int = 0


@dataclass
class Measurement:
    """All measurements from §1.3 Bab I."""
    theta_hat: int = 0
    N: List[int] = field(default_factory=lambda: [0, 0, 0])
    K: List[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    Q: List[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    U: int = 0
    rho: int = 0
    A_N: int = 0
    A_K: int = 0
    A_Q: int = 0
    H_star: int = 0


@dataclass
class HgeoFile:
    """
    Complete .hgeo file structure per §3.26.

    Provides full provenance chain:
      font (sealed) → Ψ-Compiler → skeleton → measurement → v18 → guard
    """
    hgeo_version: str = "1.0"
    har_id: str = "HAR-001"
    glyph_id: str = ""         # Unicode codepoint, e.g. "U+0628"
    glyph_name: str = ""       # Human name, e.g. "ب"

    canonical_lock: CanonicalLock = field(default_factory=CanonicalLock)
    extraction_params: ExtractionParams = field(default_factory=ExtractionParams)
    skeleton: Dict[str, Any] = field(default_factory=lambda: {"nodes": [], "edges": []})
    dots: List[Dict[str, Any]] = field(default_factory=list)
    mainpath: MainPath = field(default_factory=MainPath)
    measurement: Measurement = field(default_factory=Measurement)
    v18: List[int] = field(default_factory=lambda: [0] * 18)
    guard_status: Dict[str, str] = field(default_factory=dict)
    digest: str = ""

    def compute_digest(self) -> str:
        """Compute SHA-256 digest of the v18 vector."""
        data = json.dumps(self.v18, separators=(",", ":")).encode("utf-8")
        return f"sha256:{hashlib.sha256(data).hexdigest()}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        d: Dict[str, Any] = {
            "hgeo_version": self.hgeo_version,
            "har_id": self.har_id,
            "glyph_id": self.glyph_id,
            "glyph_name": self.glyph_name,
            "canonical_lock": asdict(self.canonical_lock),
            "extraction_params": asdict(self.extraction_params),
            "skeleton": self.skeleton,
            "dots": self.dots,
            "mainpath": asdict(self.mainpath),
            "measurement": asdict(self.measurement),
            "v18": self.v18,
            "guard_status": self.guard_status,
            "digest": self.digest,
        }
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> HgeoFile:
        """Create from parsed JSON dict."""
        hgeo = cls()
        hgeo.hgeo_version = d.get("hgeo_version", "1.0")
        hgeo.har_id = d.get("har_id", "HAR-001")
        hgeo.glyph_id = d.get("glyph_id", "")
        hgeo.glyph_name = d.get("glyph_name", "")

        cl = d.get("canonical_lock", {})
        hgeo.canonical_lock = CanonicalLock(
            font=cl.get("font", ""),
            font_hash=cl.get("font_hash", ""),
            resolution_ppem=cl.get("resolution_ppem", 256),
        )

        ep = d.get("extraction_params", {})
        hgeo.extraction_params = ExtractionParams(
            algorithm=ep.get("algorithm", "zhang-suen"),
            adjacency=ep.get("adjacency", "8-neighborhood"),
            prune_length=ep.get("prune_length", 3),
            corner_angle_deg=ep.get("corner_angle_deg", 60),
        )

        hgeo.skeleton = d.get("skeleton", {"nodes": [], "edges": []})
        hgeo.dots = d.get("dots", [])

        mp = d.get("mainpath", {})
        hgeo.mainpath = MainPath(
            node_sequence=mp.get("node_sequence", []),
            is_closed=mp.get("is_closed", False),
            total_pixels=mp.get("total_pixels", 0),
        )

        m = d.get("measurement", {})
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

        hgeo.v18 = d.get("v18", [0] * 18)
        hgeo.guard_status = d.get("guard_status", {})
        hgeo.digest = d.get("digest", "")

        return hgeo

    @classmethod
    def from_codex_entry(cls, entry: Any) -> HgeoFile:
        """
        Create .hgeo from a CodexEntry.
        Generates measurement from the v18 vector.
        """
        from .guards import compute_U, full_guard_check

        vec = list(entry.vector)
        U = compute_U(vec)
        rho = vec[0] - U

        guard_result = full_guard_check(vec)
        guard_status = {
            k: ("PASS" if v else "FAIL")
            for k, v in guard_result.items()
            if k != "all_pass"
        }

        hgeo = cls()
        hgeo.glyph_name = entry.char
        hgeo.measurement = Measurement(
            theta_hat=vec[0],
            N=vec[1:4],
            K=vec[4:9],
            Q=vec[9:14],
            U=U,
            rho=rho,
            A_N=vec[14],
            A_K=vec[15],
            A_Q=vec[16],
            H_star=vec[17],
        )
        hgeo.v18 = vec
        hgeo.guard_status = guard_status
        hgeo.digest = hgeo.compute_digest()

        return hgeo


def write_hgeo(path: str, hgeo: HgeoFile) -> None:
    """Write .hgeo file to disk (JSON format)."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(hgeo.to_dict(), f, ensure_ascii=False, indent=4)


def read_hgeo(path: str) -> HgeoFile:
    """Read .hgeo file from disk."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return HgeoFile.from_dict(data)
