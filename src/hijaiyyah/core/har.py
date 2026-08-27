"""
HAR — HISAB Alphabet Registry.

Bab III §3.27: Database of alphabet data with validation,
provenance chain, and certificate.

Structure:
  har/
  ├── manifest.json
  ├── HAR-001/          ← Hijaiyyah
  │   ├── meta.json
  │   ├── canonical_lock.json
  │   ├── master_table.json
  │   ├── master_table.rom
  │   ├── validation/
  │   │   ├── guard_report.json
  │   │   └── inject_report.json
  │   └── certificate.json
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .guards import full_guard_check
from .master_table import MASTER_TABLE
from .rom import pack_rom, rom_sha256


@dataclass
class HARMeta:
    """Metadata for one alphabet entry."""
    har_id: str = "HAR-001"
    name: str = "Hijaiyyah"
    version: str = "1.0"
    letter_count: int = 28
    codex_dim: int = 18
    status: str = "CERTIFIED"  # CERTIFIED | PENDING | DRAFT


@dataclass
class GuardReport:
    """Validation report: guard check on all letters."""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    details: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def all_pass(self) -> bool:
        return self.failed == 0 and self.total_checks > 0


@dataclass
class InjectReport:
    """Validation report: injectivity of v18 mapping."""
    total_pairs: int = 0
    unique_vectors: int = 0
    is_injective: bool = False


@dataclass
class HARCertificate:
    """Release certificate with SHA-256 chain."""
    har_id: str = ""
    version: str = ""
    master_table_sha256: str = ""
    rom_sha256: str = ""
    guard_report_pass: bool = False
    inject_report_pass: bool = False
    certificate_sha256: str = ""


class HARRegistry:
    """
    HISAB Alphabet Registry manager.

    Generates HAR-001 (Hijaiyyah) from the sealed Master Table.
    Rigidly restricted to strictly scriptural kanonik alphabets.
    """

    def __init__(self) -> None:
        self.entries: Dict[str, HARMeta] = {}

    def generate_har001(self) -> Dict[str, Any]:
        """Generate complete HAR-001 (Hijaiyyah) data package."""
        meta = HARMeta()
        self.entries["HAR-001"] = meta

        # Master table data
        all_entries = MASTER_TABLE.all_entries()
        master_data = {
            "version": "HM-28-v1.0-HC18D",
            "letters": [
                {
                    "id": e.index,
                    "letter": e.char,
                    "name": e.name,
                    "v18": list(e.vector),
                }
                for e in all_entries
            ],
        }

        # Guard report
        guard_report = self._generate_guard_report(all_entries)

        # Injectivity report
        inject_report = self._generate_inject_report(all_entries)

        # ROM
        vectors = [list(e.vector) for e in all_entries]
        rom_data = pack_rom(vectors)
        rom_hash = rom_sha256(rom_data)

        # Certificate
        mt_sha256 = MASTER_TABLE.compute_sha256()
        cert = HARCertificate(
            har_id="HAR-001",
            version="1.0",
            master_table_sha256=mt_sha256,
            rom_sha256=rom_hash,
            guard_report_pass=guard_report.all_pass,
            inject_report_pass=inject_report.is_injective,
        )
        # Compute certificate hash
        cert_data = json.dumps({
            "har_id": cert.har_id,
            "mt_sha256": cert.master_table_sha256,
            "rom_sha256": cert.rom_sha256,
            "guards": cert.guard_report_pass,
            "inject": cert.inject_report_pass,
        }, separators=(",", ":")).encode("utf-8")
        cert.certificate_sha256 = hashlib.sha256(cert_data).hexdigest()

        return {
            "meta": {
                "har_id": meta.har_id,
                "name": meta.name,
                "version": meta.version,
                "letter_count": meta.letter_count,
                "codex_dim": meta.codex_dim,
                "status": meta.status,
            },
            "master_table": master_data,
            "guard_report": {
                "total_checks": guard_report.total_checks,
                "passed": guard_report.passed,
                "failed": guard_report.failed,
                "all_pass": guard_report.all_pass,
                "details": guard_report.details,
            },
            "inject_report": {
                "total_pairs": inject_report.total_pairs,
                "unique_vectors": inject_report.unique_vectors,
                "is_injective": inject_report.is_injective,
            },
            "rom_sha256": rom_hash,
            "certificate": {
                "har_id": cert.har_id,
                "version": cert.version,
                "master_table_sha256": cert.master_table_sha256,
                "rom_sha256": cert.rom_sha256,
                "guard_report_pass": cert.guard_report_pass,
                "inject_report_pass": cert.inject_report_pass,
                "certificate_sha256": cert.certificate_sha256,
            },
        }

    def _generate_guard_report(self, entries: List[Any]) -> GuardReport:
        """Run guard check on all letters (G1–G4 + T1–T2)."""
        report = GuardReport()
        for e in entries:
            detail = full_guard_check(e)
            report.total_checks += 1
            if detail["all_pass"]:
                report.passed += 1
            else:
                report.failed += 1
            report.details.append({
                "letter": e.char,
                "name": e.name,
                **{k: v for k, v in detail.items() if k != "all_pass"},
                "status": "PASS" if detail["all_pass"] else "FAIL",
            })
        return report

    def _generate_inject_report(self, entries: List[Any]) -> InjectReport:
        """Check injectivity: all v18 vectors must be unique."""
        vectors = [tuple(e.vector) for e in entries]
        unique = set(vectors)
        n = len(vectors)
        pairs = n * (n - 1) // 2

        return InjectReport(
            total_pairs=pairs,
            unique_vectors=len(unique),
            is_injective=len(unique) == n,
        )

    def write_to_directory(self, base_dir: str) -> None:
        """Write HAR-001 to directory structure."""
        har_data = self.generate_har001()
        har_dir = os.path.join(base_dir, "HAR-001")
        val_dir = os.path.join(har_dir, "validation")
        os.makedirs(val_dir, exist_ok=True)

        # meta.json
        with open(os.path.join(har_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(har_data["meta"], f, ensure_ascii=False, indent=2)

        # master_table.json
        with open(os.path.join(har_dir, "master_table.json"), "w", encoding="utf-8") as f:
            json.dump(har_data["master_table"], f, ensure_ascii=False, indent=2)

        # master_table.rom
        all_entries = MASTER_TABLE.all_entries()
        vectors = [list(e.vector) for e in all_entries]
        rom_data = pack_rom(vectors)
        with open(os.path.join(har_dir, "master_table.rom"), "wb") as f:
            f.write(rom_data)

        # validation/guard_report.json
        with open(os.path.join(val_dir, "guard_report.json"), "w", encoding="utf-8") as f:
            json.dump(har_data["guard_report"], f, ensure_ascii=False, indent=2)

        # validation/inject_report.json
        with open(os.path.join(val_dir, "inject_report.json"), "w", encoding="utf-8") as f:
            json.dump(har_data["inject_report"], f, ensure_ascii=False, indent=2)

        # certificate.json
        with open(os.path.join(har_dir, "certificate.json"), "w", encoding="utf-8") as f:
            json.dump(har_data["certificate"], f, ensure_ascii=False, indent=2)

        # manifest.json (at base level)
        manifest = {
            "registries": [
                {
                    "id": "HAR-001",
                    "name": "Hijaiyyah",
                    "status": "CERTIFIED",
                    "path": "HAR-001/",
                }
            ]
        }
        with open(os.path.join(base_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
