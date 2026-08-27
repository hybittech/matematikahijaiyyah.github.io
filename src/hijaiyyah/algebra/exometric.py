"""Field 5: Hijaiyyah Exometric analysis (Bab II-E, Ch 32-36)."""

from __future__ import annotations

from typing import Any, Dict, List

from ..core.codex_entry import CodexEntry
from ..core.exomatrix import build_exomatrix
from ..core.master_table import MASTER_TABLE
from ._common import _v, _n2
import numpy as np


def build(h: Any) -> List[List[int]]:
    """Build 5×5 Exomatrix  (Def 32.1.1)."""
    return build_exomatrix(h)


def audit(E: List[List[int]]) -> Dict[str, bool]:
    """Five audit relations on Exomatrix  (Identity 33.1.1)."""
    R1 = E[0][0] == E[0][1] + E[0][2]
    R2 = E[1][4] == E[1][0] + E[1][1] + E[1][2]
    R3 = E[4][3] == E[2][0] + E[2][1] + E[2][2] + E[2][3] + E[2][4]
    R4 = E[4][4] == E[3][0] + E[3][1] + E[3][2] + E[3][3] + E[3][4]
    R5 = E[0][1] == E[3][1] + E[3][2] + E[3][3] + 4 * E[3][4]
    return {
        "R1": R1,
        "R2": R2,
        "R3": R3,
        "R4": R4,
        "R5": R5,
        "all_pass": R1 and R2 and R3 and R4 and R5,
    }


def row_sums(E: List[List[int]]) -> List[int]:
    """σ_r = Σ_c E[r][c]"""
    return [sum(E[r]) for r in range(5)]


def grand_sum(E: List[List[int]]) -> int:
    """Σ_{r,c} E[r][c]"""
    return sum(sum(row) for row in E)


def phi(E: List[List[int]]) -> int:
    """Φ(h) = ‖E(h)‖_F²"""
    return sum(E[r][c] ** 2 for r in range(5) for c in range(5))


def phi_decomposition(E: List[List[int]]) -> Dict[str, int]:
    """Layer decomposition of Φ."""
    theta_part = E[0][0] ** 2 + E[0][1] ** 2 + E[0][2] ** 2
    n_part = sum(E[1][c] ** 2 for c in range(5))
    k_part = sum(E[2][c] ** 2 for c in range(5))
    q_part = sum(E[3][c] ** 2 for c in range(5))
    meta = E[4][0] ** 2 + E[4][3] ** 2 + E[4][4] ** 2
    return {"theta": theta_part, "N": n_part, "K": k_part, "Q": q_part, "meta": meta}


def string_exomatrix(text: str) -> List[List[int]]:
    """E(w) = Σ E(xᵢ)"""
    result = [[0] * 5 for _ in range(5)]
    for ch in text:
        entry = MASTER_TABLE.get_by_char(ch)
        if entry is not None:
            E = build_exomatrix(entry)
            for r in range(5):
                for c in range(5):
                    result[r][c] += E[r][c]
    return result


def rank_M14() -> int:
    es = MASTER_TABLE.all_entries()
    M = np.array([list(e.vector)[:14] for e in es])
    return int(np.linalg.matrix_rank(M))


def rank_M() -> int:
    return 15


def energy_table() -> List[Dict[str, Any]]:
    """All 28 letters sorted by Φ descending."""
    rows: List[Dict[str, Any]] = []
    for e in MASTER_TABLE.all_entries():
        v = list(e.vector)
        E = build_exomatrix(v)
        phi_val = sum(E[r][c] ** 2 for r in range(5) for c in range(5))
        norm2_val = _n2(v)
        rows.append(
            {
                "letter": e.char,
                "name": e.name,
                "phi": phi_val,
                "norm2": norm2_val,
                "surplus": phi_val - norm2_val,
                "phi_theta": E[0][0] ** 2 + E[0][1] ** 2 + E[0][2] ** 2,
            }
        )
    rows.sort(key=lambda x: x["phi"], reverse=True)
    for i, row in enumerate(rows):
        row["rank"] = i + 1
    return rows


def reconstruct(E: List[List[int]]) -> List[int]:
    """Recover v₁₈ from Exomatrix  (Theorem 36.2.1)."""
    theta = E[0][0]
    na, nb, nd = E[1][0], E[1][1], E[1][2]
    kp, kx, ks, ka, kc = E[2][0], E[2][1], E[2][2], E[2][3], E[2][4]
    qp, qx, qs, qa, qc = E[3][0], E[3][1], E[3][2], E[3][3], E[3][4]
    a_n = na + nb + nd
    a_k = kp + kx + ks + ka + kc
    a_q = qp + qx + qs + qa + qc
    h_star = E[4][0]
    return [
        theta,
        na,
        nb,
        nd,
        kp,
        kx,
        ks,
        ka,
        kc,
        qp,
        qx,
        qs,
        qa,
        qc,
        a_n,
        a_k,
        a_q,
        h_star,
    ]
