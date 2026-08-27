"""
Master Table: the sealed 28×18 dataset.
Single source of truth for all codex vectors.
"""

from __future__ import annotations

import hashlib
import json
from typing import Dict, List, Optional

from .codex_entry import CodexEntry
from .constants import H28_ALPHABET

# ── Authoritative data ───────────────────────────────────────────
# Each row: [Θ̂, Na,Nb,Nd, Kp,Kx,Ks,Ka,Kc, Qp,Qx,Qs,Qa,Qc, AN,AK,AQ, H*]

_NAMES = [
    "Alif","Ba","Ta","Tsa","Jim","Ha","Kha","Dal","Dzal","Ra","Zay",
    "Sin","Syin","Shad","Dhad","Tha","Zha","Ain","Ghain","Fa","Qaf",
    "Kaf","Lam","Mim","Nun","Waw","Haa","Ya",
]

_RAW: List[List[int]] = [
    [0, 0,0,0, 1,0,0,0,0, 0,0,0,0,0, 0,1,0, 0],  # ا (Alif)
    [2, 0,0,1, 0,1,0,0,0, 1,0,0,0,0, 1,1,1, 0],  # ب (Ba)
    [2, 2,0,0, 0,1,0,0,0, 1,0,0,0,0, 2,1,1, 0],  # ت (Ta)
    [2, 3,0,0, 0,1,0,0,0, 1,0,0,0,0, 3,1,1, 0],  # ث (Tsa)
    [3, 0,1,0, 0,1,0,0,0, 1,0,0,0,0, 1,1,1, 0],  # ج (Jim)
    [3, 0,0,0, 0,1,0,0,0, 1,0,0,0,0, 0,1,1, 0],  # ح (Ha)
    [3, 1,0,0, 0,1,0,0,0, 1,0,0,0,0, 1,1,1, 0],  # خ (Kha)
    [1, 0,0,0, 0,0,0,0,0, 0,0,0,1,0, 0,0,1, 0],  # د (Dal)
    [1, 1,0,0, 0,0,0,0,0, 0,0,0,1,0, 1,0,1, 0],  # ذ (Dzal)
    [1, 0,0,0, 0,0,0,0,0, 0,0,1,0,0, 0,0,1, 0],  # ر (Ra)
    [1, 1,0,0, 0,0,0,0,0, 0,0,1,0,0, 1,0,1, 0],  # ز (Zay)
    [4, 0,0,0, 0,0,0,0,0, 1,2,0,0,0, 0,0,3, 0],  # س (Sin)
    [4, 3,0,0, 0,0,0,0,0, 1,2,0,0,0, 3,0,3, 0],  # ش (Syin)
    [6, 0,0,0, 0,0,0,0,0, 1,0,0,0,1, 0,0,2, 0],  # ص (Shad)
    [6, 1,0,0, 0,0,0,0,0, 1,0,0,0,1, 1,0,2, 0],  # ض (Dhad)
    [4, 0,0,0, 0,0,1,0,0, 0,0,0,0,1, 0,1,1, 0],  # ط (Tha)
    [4, 1,0,0, 0,0,1,0,0, 0,0,0,0,1, 1,1,1, 0],  # ظ (Zha)
    [3, 0,0,0, 0,0,0,0,0, 1,1,0,0,0, 0,0,2, 0],  # ع (Ain)
    [3, 1,0,0, 0,0,0,0,0, 1,1,0,0,0, 1,0,2, 0],  # غ (Ghain)
    [5, 1,0,0, 0,1,0,0,0, 1,0,0,0,1, 1,1,2, 0],  # ف (Fa)
    [6, 2,0,0, 0,0,0,0,0, 1,0,0,0,1, 2,0,2, 0],  # ق (Qaf)
    [2, 0,0,0, 0,0,0,1,0, 0,0,0,0,0, 0,1,0, 1],  # ك (Kaf)
    [1, 0,0,0, 0,1,0,0,0, 1,0,0,0,0, 0,1,1, 0],  # ل (Lam)
    [4, 0,0,0, 0,0,0,0,1, 0,0,0,0,1, 0,1,1, 0],  # م (Mim)
    [2, 1,0,0, 0,0,0,0,0, 1,0,0,0,0, 1,0,1, 0],  # ن (Nun)
    [5, 0,0,0, 0,0,0,0,0, 0,0,1,0,1, 0,0,2, 0],  # و (Waw)
    [8, 0,0,0, 0,0,0,0,1, 0,0,0,0,2, 0,1,2, 0],  # هـ (Haa)
    [3, 0,0,2, 0,0,0,0,0, 1,1,0,0,0, 2,0,2, 0],  # ي (Ya)
]


class MasterTable:
    """Sealed 28×18 Master Table with integrity verification."""

    def __init__(self) -> None:
        self._entries: List[CodexEntry] = []
        self._by_char: Dict[str, CodexEntry] = {}
        self._by_index: Dict[int, CodexEntry] = {}
        self._load()

    def _load(self) -> None:
        chars = list(H28_ALPHABET)
        # strict=True: a length mismatch between the alphabet, the names, and
        # _RAW must fail loudly, not silently load a shorter table.
        for i, (ch, name, vec) in enumerate(zip(chars, _NAMES, _RAW, strict=True)):
            entry = CodexEntry(
                index=i + 1,
                char=ch,
                name=name,
                vector=tuple(vec),
            )
            self._entries.append(entry)
            self._by_char[ch] = entry
            self._by_index[i + 1] = entry

    def all_entries(self) -> List[CodexEntry]:
        return list(self._entries)

    def get_by_char(self, ch: str) -> Optional[CodexEntry]:
        return self._by_char.get(ch)

    def get_by_index(self, idx: int) -> Optional[CodexEntry]:
        return self._by_index.get(idx)

    def get_by_name(self, name: str) -> Optional[CodexEntry]:
        for e in self._entries:
            if e.name.lower() == name.lower():
                return e
        return None

    def compute_sha256(self) -> str:
        data = json.dumps(
            [list(e.vector) for e in self._entries],
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def to_json(self) -> str:
        return json.dumps({
            "version": "HM-28-v1.0-HC18D",
            "letters": [
                {
                    "id": e.index,
                    "letter": e.char,
                    "name": e.name,
                    "v18": list(e.vector),
                }
                for e in self._entries
            ],
        }, ensure_ascii=False, indent=2)

    def to_csv(self) -> str:
        from .constants import V18_SLOTS
        header = "index,char,name," + ",".join(V18_SLOTS)
        lines = [header]
        for e in self._entries:
            vals = ",".join(str(x) for x in e.vector)
            lines.append(f"{e.index},{e.char},{e.name},{vals}")
        return "\n".join(lines)


# Singleton instance
MASTER_TABLE = MasterTable()
