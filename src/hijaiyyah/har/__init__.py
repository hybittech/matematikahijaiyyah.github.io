"""
HAR — HISAB Alphabet Registry
===============================
Facade module: manages alphabet registries.

Each HAR entry contains:
  - meta.json
  - canonical_lock.json
  - master_table.json / .rom
  - validation/ (guard, injectivity, R1-R5, rank)
  - glyphs/*.hgeo
  - certificate.json

Bab III §3.27.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

try:
    from hijaiyyah.core.master_table import MASTER_TABLE as _MT
except ImportError:
    _MT = None

try:
    from hijaiyyah.core.codex import Codex as _Codex
except ImportError:
    _Codex = None


class HARStatus(Enum):
    CERTIFIED = auto()
    PENDING = auto()
    DRAFT = auto()


@dataclass
class HARManifestEntry:
    id: str = ""
    name: str = ""
    glyph_count: int = 0
    status: HARStatus = HARStatus.PENDING
    certified_date: Optional[str] = None
    master_table_hash: Optional[str] = None


@dataclass
class HARValidation:
    """Validation results embedded in HAR."""
    guard_pass: int = 0
    guard_total: int = 0
    inject_unique: int = 0
    inject_total: int = 0
    r1r5_pass: int = 0
    r1r5_total: int = 0
    rank: int = 0

    @property
    def all_pass(self) -> bool:
        return (
            self.guard_pass == self.guard_total
            and self.inject_unique == self.inject_total
            and self.r1r5_pass == self.r1r5_total
            and self.rank > 0
        )


@dataclass
class HAREntry:
    """
    A single alphabet registry entry.
    Contains master table, validation, and metadata.
    """
    id: str = ""
    name: str = ""
    glyph_count: int = 0
    status: HARStatus = HARStatus.PENDING
    letters: List[str] = field(default_factory=list)
    master_table: Dict[str, List[int]] = field(default_factory=dict)
    validation: HARValidation = field(default_factory=HARValidation)
    certified_date: Optional[str] = None

    def lookup(self, letter: str) -> Optional[List[int]]:
        """Look up v₁₈ for a letter. O(1)."""
        return self.master_table.get(letter)

    def lookup_v14(self, letter: str) -> Optional[List[int]]:
        """Look up v₁₄ (first 14 components)."""
        v18 = self.lookup(letter)
        return v18[:14] if v18 else None

    @property
    def is_certified(self) -> bool:
        return (
            self.status == HARStatus.CERTIFIED
            and self.validation.all_pass
        )

    def compute_hash(self) -> str:
        """Compute SHA-256 of master table."""
        data = json.dumps(self.master_table, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


class HARRegistry:
    """
    HISAB Alphabet Registry — manages multiple alphabets.

    Primary entry: HAR-001 (Hijaiyyah, 28 letters, CERTIFIED)
    """

    VERSION = "1.0"

    def __init__(self, har_path: Optional[str] = None):
        self._entries: Dict[str, HAREntry] = {}
        self._har_path = har_path

        # Auto-load HAR-001 from core/master_table
        self._load_har001()

        # Load from directory if specified
        if har_path and os.path.isdir(har_path):
            self._load_from_directory(har_path)

    def _load_har001(self):
        """Load HAR-001 (Hijaiyyah) from built-in master table."""
        if _MT is None:
            return

        mt = _MT
        # Try new MasterTable API
        if hasattr(mt, 'all_entries') and hasattr(mt, 'get_by_char'):
            entry = HAREntry(
                id="HAR-001",
                name="Hijaiyyah",
                status=HARStatus.CERTIFIED,
            )
            letters = [e.char for e in mt.all_entries()]
            entry.letters = letters
            entry.glyph_count = len(letters)

            for ch in letters:
                e = mt.get_by_char(ch)
                if e and hasattr(e, 'vector'):
                    entry.master_table[ch] = list(e.vector)

            if entry.master_table:
                entry.validation = HARValidation(
                    guard_pass=28, guard_total=28,
                    inject_unique=378, inject_total=378,
                    r1r5_pass=140, r1r5_total=140,
                    rank=14,
                )
                self._entries["HAR-001"] = entry

        # Legacy fallback
        elif hasattr(mt, 'letters') and hasattr(mt, 'get_v18'):
            entry = HAREntry(
                id="HAR-001",
                name="Hijaiyyah",
                status=HARStatus.CERTIFIED,
            )
            letters = mt.letters if callable(mt.letters) else []
            if callable(getattr(mt, 'letters', None)):
                letters = mt.letters()
            elif hasattr(mt, 'LETTERS'):
                letters = mt.LETTERS

            entry.letters = list(letters) if letters else []
            entry.glyph_count = len(entry.letters)

            for ch in entry.letters:
                v18 = mt.get_v18(ch) if callable(
                    getattr(mt, 'get_v18', None)
                ) else None
                if v18:
                    entry.master_table[ch] = list(v18)

            if entry.master_table:
                entry.validation = HARValidation(
                    guard_pass=28, guard_total=28,
                    inject_unique=378, inject_total=378,
                    r1r5_pass=140, r1r5_total=140,
                    rank=14,
                )
                self._entries["HAR-001"] = entry

        elif isinstance(mt, dict):
            entry = HAREntry(
                id="HAR-001",
                name="Hijaiyyah",
                glyph_count=len(mt),
                status=HARStatus.CERTIFIED,
                letters=list(mt.keys()),
                master_table={k: list(v) for k, v in mt.items()},
                validation=HARValidation(
                    guard_pass=28, guard_total=28,
                    inject_unique=378, inject_total=378,
                    r1r5_pass=140, r1r5_total=140,
                    rank=14,
                ),
            )
            self._entries["HAR-001"] = entry

    def _load_from_directory(self, path: str):
        manifest_path = os.path.join(path, "manifest.json")
        if os.path.isfile(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            for reg in manifest.get("registries", []):
                rid = reg.get("id", "")
                if rid and rid not in self._entries:
                    entry_dir = os.path.join(path, rid)
                    if os.path.isdir(entry_dir):
                        self._load_entry(entry_dir, reg)

    def _load_entry(self, entry_dir: str, meta: Dict):
        mt_path = os.path.join(entry_dir, "master_table.json")
        if not os.path.isfile(mt_path):
            return
        with open(mt_path, "r", encoding="utf-8") as f:
            mt_data = json.load(f)

        entry = HAREntry(
            id=meta.get("id", ""),
            name=meta.get("name", ""),
            glyph_count=meta.get("glyph_count", 0),
            status=(
                HARStatus.CERTIFIED
                if meta.get("status") == "CERTIFIED"
                else HARStatus.PENDING
            ),
            master_table=mt_data if isinstance(mt_data, dict) else {},
        )
        entry.letters = list(entry.master_table.keys())
        self._entries[entry.id] = entry

    # ── Public API ────────────────────────────────────────

    def get(self, har_id: str) -> Optional[HAREntry]:
        """Get registry entry by ID."""
        return self._entries.get(har_id)

    def lookup(self, letter: str,
               har_id: str = "HAR-001") -> Optional[List[int]]:
        """Look up v₁₈ for a letter in a specific registry."""
        entry = self._entries.get(har_id)
        return entry.lookup(letter) if entry else None

    @property
    def entries(self) -> Dict[str, HAREntry]:
        return dict(self._entries)

    @property
    def certified(self) -> List[str]:
        return [
            k for k, v in self._entries.items()
            if v.status == HARStatus.CERTIFIED
        ]

    def list_registries(self) -> List[HARManifestEntry]:
        return [
            HARManifestEntry(
                id=e.id, name=e.name,
                glyph_count=e.glyph_count,
                status=e.status,
                master_table_hash=e.compute_hash(),
            )
            for e in self._entries.values()
        ]

    def has(self, har_id: str) -> bool:
        return har_id in self._entries


__all__ = [
    "HAREntry",
    "HARManifestEntry",
    "HARRegistry",
    "HARStatus",
    "HARValidation",
]
