"""
Immutable constants for the Hijaiyyah Mathematics system.
All values are derived from the Master Table HM-28-v1.0-HC18D.
"""

from __future__ import annotations

from typing import Dict, FrozenSet, Tuple

# ── Alphabet ─────────────────────────────────────────────────────

H28_ALPHABET: Tuple[str, ...] = (
    "ا",
    "ب",
    "ت",
    "ث",
    "ج",
    "ح",
    "خ",
    "د",
    "ذ",
    "ر",
    "ز",
    "س",
    "ش",
    "ص",
    "ض",
    "ط",
    "ظ",
    "ع",
    "غ",
    "ف",
    "ق",
    "ك",
    "ل",
    "م",
    "ن",
    "و",
    "هـ",
    "ي",
)

ALPHABET_SIZE: int = 28
CODEX_DIM: int = 18
INDEPENDENT_DIM: int = 14
MASTER_TABLE_BYTES: int = 252  # 28 × 9 (nibble-packed)

# ── Slot names (v18 component labels) ────────────────────────────

V18_SLOTS: Tuple[str, ...] = (
    "Θ̂",
    "Na",
    "Nb",
    "Nd",
    "Kp",
    "Kx",
    "Ks",
    "Ka",
    "Kc",
    "Qp",
    "Qx",
    "Qs",
    "Qa",
    "Qc",
    "AN",
    "AK",
    "AQ",
    "H*",
)

V14_SLOTS: Tuple[str, ...] = V18_SLOTS[:14]

# ── Slot index mapping ───────────────────────────────────────────

SLOT_INDEX: Dict[str, int] = {
    "theta": 0,
    "Na": 1,
    "Nb": 2,
    "Nd": 3,
    "Kp": 4,
    "Kx": 5,
    "Ks": 6,
    "Ka": 7,
    "Kc": 8,
    "Qp": 9,
    "Qx": 10,
    "Qs": 11,
    "Qa": 12,
    "Qc": 13,
    "AN": 14,
    "AK": 15,
    "AQ": 16,
    "Hstar": 17,
    # lowercase aliases
    "na": 1,
    "nb": 2,
    "nd": 3,
    "kp": 4,
    "kx": 5,
    "ks": 6,
    "ka": 7,
    "kc": 8,
    "qp": 9,
    "qx": 10,
    "qs": 11,
    "qa": 12,
    "qc": 13,
    "an": 14,
    "ak": 15,
    "aq": 16,
    "hstar": 17,
}

# ── Hijaiyyah character sets ─────────────────────────────────────

H28_SINGLE_CHARS: FrozenSet[str] = frozenset("ابتثجحخدذرزسشصضطظعغفقكلمنوي")

HAA_SEQUENCE: str = "هـ"  # U+0647 + U+0640
HAA_FIRST: str = "ه"  # U+0647
HAA_SECOND: str = "ـ"  # U+0640 (tatweel)

# ── Max component values (from Master Table) ─────────────────────

MAX_THETA: int = 8  # هـ
MAX_NA: int = 3  # ث
MAX_NB: int = 1  # ج
MAX_ND: int = 2  # ي
MAX_QC: int = 2  # هـ
