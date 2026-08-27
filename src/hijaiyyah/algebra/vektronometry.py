"""Field 1: Hijaiyyah Vektronometry (Bab II-A, Ch 17-21)."""

from __future__ import annotations

import math
from typing import Any, Dict, List

from ..core.guards import compute_U
from ..core.master_table import MASTER_TABLE
from ._common import _n2, _v


def _ip(a: List[int], b: List[int]) -> int:
    return sum(a[i] * b[i] for i in range(14))


def primitive_ratios(h) -> Dict[str, float]:
    v = _v(h)
    t = v[14] + v[15] + v[16]
    if t == 0:
        return {"r_N": 0.0, "r_K": 0.0, "r_Q": 0.0}
    return {"r_N": v[14] / t, "r_K": v[15] / t, "r_Q": v[16] / t}


def turning_ratios(h) -> Dict[str, float]:
    v = _v(h)
    th = v[0]
    U = compute_U(v)
    rho = th - U
    if th == 0:
        return {"r_U": 0.0, "r_rho": 0.0, "r_loop": 0.0}
    return {"r_U": U / th, "r_rho": rho / th, "r_loop": (4 * v[13]) / th}


def comp_angle(h) -> float:
    v = _v(h)
    ak = v[15]
    aq = v[16]
    if ak > 0:
        return math.atan(aq / ak)
    elif aq > 0:
        return math.pi / 2
    return 0.0


def norm2(h) -> int:
    return _n2(_v(h))


def norm(h) -> float:
    return math.sqrt(norm2(h))


def inner(h1, h2) -> int:
    return _ip(_v(h1), _v(h2))


def cosine(h1, h2) -> float:
    v1, v2 = _v(h1), _v(h2)
    n1, n2_ = math.sqrt(_n2(v1)), math.sqrt(_n2(v2))
    if n1 == 0 or n2_ == 0:
        return 0.0
    return max(0.0, _ip(v1, v2) / (n1 * n2_))


def pythagorean_check(h) -> Dict[str, Any]:
    v = _v(h)
    lhs = _n2(v)
    sq = [sum(v[k] ** 2 for k in s) for s in [[0], [1, 2, 3], [4, 5, 6, 7, 8], [9, 10, 11, 12, 13]]]
    return {
        "lhs": lhs,
        "rhs": sum(sq),
        "theta": sq[0],
        "N": sq[1],
        "K": sq[2],
        "Q": sq[3],
        "pass": lhs == sum(sq),
    }


def full_table() -> List[Dict]:
    rows = []
    for e in MASTER_TABLE.all_entries():
        v = list(e.vector)
        pr = primitive_ratios(e)
        tr = turning_ratios(e)
        rows.append(
            {
                "letter": e.char,
                "name": e.name,
                "norm2": _n2(v),
                "norm": math.sqrt(_n2(v)),
                "r_N": pr["r_N"],
                "r_K": pr["r_K"],
                "r_Q": pr["r_Q"],
                "alpha_deg": math.degrees(comp_angle(e)),
                "U": compute_U(v),
                "rho": v[0] - compute_U(v),
                "r_U": tr["r_U"],
                "r_rho": tr["r_rho"],
                "r_loop": tr["r_loop"],
            }
        )
    return rows
