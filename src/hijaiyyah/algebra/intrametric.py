"""Field 4: Hijaiyyah Intrametric (Bab II-D, Ch 29-31)."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

from ..core.master_table import MASTER_TABLE
from ._common import _n2, _v


def _ip(a: List[int], b: List[int]) -> int:
    """Inner product on v₁₄."""
    return sum(a[i] * b[i] for i in range(14))


def euclidean(h1: Any, h2: Any) -> float:
    """d(h₁, h₂) = ‖v₁₄(h₁) − v₁₄(h₂)‖  (Def 29.1.1)."""
    v1, v2 = _v(h1), _v(h2)
    return math.sqrt(sum((v1[i] - v2[i]) ** 2 for i in range(14)))


def euclidean_sq(h1: Any, h2: Any) -> int:
    """d(h₁,h₂)²  (integer form)."""
    v1, v2 = _v(h1), _v(h2)
    return sum((v1[i] - v2[i]) ** 2 for i in range(14))


def manhattan(h1: Any, h2: Any) -> int:
    """Manhattan / L₁ distance on v₁₄."""
    v1, v2 = _v(h1), _v(h2)
    return sum(abs(v1[i] - v2[i]) for i in range(14))


def hamming(h1: Any, h2: Any) -> int:
    """Hamming distance on v₁₄."""
    v1, v2 = _v(h1), _v(h2)
    return sum(1 for i in range(14) if v1[i] != v2[i])


def distance_decomposition(h1: Any, h2: Any) -> Dict[str, int]:
    """Layer-wise squared distance decomposition  (Def 30.1.1)."""
    v1, v2 = _v(h1), _v(h2)
    dt = (v1[0] - v2[0]) ** 2
    dn = sum((v1[k] - v2[k]) ** 2 for k in range(1, 4))
    dk = sum((v1[k] - v2[k]) ** 2 for k in range(4, 9))
    dq = sum((v1[k] - v2[k]) ** 2 for k in range(9, 14))
    return {"total": dt + dn + dk + dq, "theta": dt, "N": dn, "K": dk, "Q": dq}


def gram_matrix() -> List[List[int]]:
    """G[i][j] = ⟨v₁₄(hᵢ), v₁₄(hⱼ)⟩  (Ch 31)."""
    es = MASTER_TABLE.all_entries()
    n = len(es)
    G: List[List[int]] = [[0] * n for _ in range(n)]
    for i in range(n):
        v1 = list(es[i].vector)
        for j in range(i, n):
            val = _ip(v1, list(es[j].vector))
            G[i][j] = val
            G[j][i] = val
    return G


def is_orthogonal(h1: Any, h2: Any) -> bool:
    """True if support sets of h₁ and h₂ are disjoint."""
    v1, v2 = _v(h1), _v(h2)
    return all(not (v1[i] > 0 and v2[i] > 0) for i in range(14))


def diameter_sq() -> int:
    """max d(hᵢ,hⱼ)² over all pairs  (Theorem 31.1.1)."""
    es = MASTER_TABLE.all_entries()
    mx = 0
    for i in range(len(es)):
        v1 = list(es[i].vector)
        for j in range(i + 1, len(es)):
            v2 = list(es[j].vector)
            d = sum((v1[k] - v2[k]) ** 2 for k in range(14))
            if d > mx:
                mx = d
    return mx


def diameter() -> float:
    """max d(hᵢ,hⱼ) over all pairs."""
    return math.sqrt(diameter_sq())


def alphabet_centroid() -> List[float]:
    """Centroid of the 28 letter vectors."""
    es = MASTER_TABLE.all_entries()
    n = len(es)
    c = [0.0] * 14
    for e in es:
        for k in range(14):
            c[k] += e.vector[k]
    return [x / n for x in c]


def nearest(h: Any) -> Tuple[str, float]:
    """Nearest Hijaiyyah letter to h (excluding h itself)."""
    v = _v(h)
    best_d = float("inf")
    best = ""
    for e in MASTER_TABLE.all_entries():
        ev = list(e.vector)
        if ev == v:
            continue
        d = math.sqrt(sum((v[i] - ev[i]) ** 2 for i in range(14)))
        if d < best_d:
            best_d = d
            best = e.char
    return (best, best_d)


def k_nearest(h: Any, k: int) -> List[Tuple[str, float]]:
    """k nearest Hijaiyyah letters to h."""
    v = _v(h)
    ds: List[Tuple[str, float]] = []
    for e in MASTER_TABLE.all_entries():
        ev = list(e.vector)
        if ev == v:
            continue
        d = math.sqrt(sum((v[i] - ev[i]) ** 2 for i in range(14)))
        ds.append((e.char, d))
    ds.sort(key=lambda x: x[1])
    return [ds[i] for i in range(min(k, len(ds)))]


def polarization_check(h1: Any, h2: Any) -> Dict[str, Any]:
    """Polarization identity check  (Theorem 30.2.1)."""
    v1, v2 = _v(h1), _v(h2)
    d2 = sum((v1[i] - v2[i]) ** 2 for i in range(14))
    p = _n2(v1) + _n2(v2) - 2 * _ip(v1, v2)
    return {"d2_sq": d2, "polar": p, "pass": d2 == p}
