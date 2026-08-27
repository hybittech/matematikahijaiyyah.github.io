"""Field 2: Hijaiyyah Normivektor (Bab II-B, Ch 22-24)."""

from __future__ import annotations
import math
from typing import Any, Dict, List, Tuple
from ..core.codex_entry import CodexEntry
from ..core.master_table import MASTER_TABLE
from ._common import _v


def diff(h1, h2) -> List[int]:
    v1, v2 = _v(h1), _v(h2)
    return [v1[i] - v2[i] for i in range(14)]


def norm_decomposition(h1, h2) -> Dict[str, Any]:
    v1, v2 = _v(h1), _v(h2)
    dt = (v1[0] - v2[0]) ** 2
    dn = sum((v1[k] - v2[k]) ** 2 for k in range(1, 4))
    dk = sum((v1[k] - v2[k]) ** 2 for k in range(4, 9))
    dq = sum((v1[k] - v2[k]) ** 2 for k in range(9, 14))
    t = dt + dn + dk + dq
    return {
        "total": t,
        "theta": dt,
        "N": dn,
        "K": dk,
        "Q": dq,
        "pct_turning": (dt / t * 100) if t else 0.0,
    }


def diff_theta(h1, h2) -> int:
    return _v(h1)[0] - _v(h2)[0]


def diff_N(h1, h2) -> List[int]:
    v1, v2 = _v(h1), _v(h2)
    return [v1[k] - v2[k] for k in range(1, 4)]


def diff_K(h1, h2) -> List[int]:
    v1, v2 = _v(h1), _v(h2)
    return [v1[k] - v2[k] for k in range(4, 9)]


def diff_Q(h1, h2) -> List[int]:
    v1, v2 = _v(h1), _v(h2)
    return [v1[k] - v2[k] for k in range(9, 14)]


def dot_gradient(h1, h2) -> List[int]:
    return diff_N(h1, h2)


def u_gradient() -> List[int]:
    return [0, 1, 1, 1, 4]


def all_dot_variants() -> List[Tuple[str, str, List[int]]]:
    entries = MASTER_TABLE.all_entries()
    result = []
    for i, e1 in enumerate(entries):
        for j, e2 in enumerate(entries):
            if i >= j:
                continue
            v1, v2 = list(e1.vector), list(e2.vector)
            if (
                v1[0] == v2[0]
                and all(v1[k] == v2[k] for k in range(4, 14))
                and any(v1[k] != v2[k] for k in range(1, 4))
            ):
                result.append((e1.char, e2.char, [v2[k] - v1[k] for k in range(1, 4)]))
    return result


def second_diff(h1, h2, h3) -> List[int]:
    d32, d21 = diff(h3, h2), diff(h2, h1)
    return [d32[i] - d21[i] for i in range(14)]


def distance_table() -> List[Dict]:
    pairs = [
        ("ص", "ض"),
        ("د", "ذ"),
        ("ح", "خ"),
        ("ع", "غ"),
        ("ط", "ظ"),
        ("د", "ر"),
        ("ب", "ج"),
        ("ب", "ت"),
        ("ا", "ب"),
        ("س", "ش"),
        ("م", "هـ"),
        ("ب", "هـ"),
        ("ا", "هـ"),
    ]
    rows = []
    for c1, c2 in pairs:
        e1, e2 = MASTER_TABLE.get_by_char(c1), MASTER_TABLE.get_by_char(c2)
        if e1 and e2:
            d = norm_decomposition(e1, e2)
            rows.append(
                {"h1": c1, "h2": c2, "dist2_sq": d["total"], "d2": math.sqrt(d["total"]), **d}
            )
    return rows
