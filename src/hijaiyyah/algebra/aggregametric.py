"""Field 3: Hijaiyyah Aggregametric (Bab II-C, Ch 25-28)."""

from __future__ import annotations

from typing import Any, Dict, List

from ..core.exomatrix import build_exomatrix
from ..core.guards import compute_U
from ..core.master_table import MASTER_TABLE


def string_integral(text: str) -> Dict[str, Any]:
    """Cod₁₈(w) = Σ v₁₈(xᵢ)  (Def 25.1.1)."""
    total: List[int] = [0] * 18
    length = 0
    trajectory: List[List[int]] = [[0] * 18]

    for ch in text:
        entry = MASTER_TABLE.get_by_char(ch)
        if entry is None:
            continue
        v = list(entry.vector)
        total = [total[i] + v[i] for i in range(18)]
        length += 1
        trajectory.append(list(total))

    return {"cod18": total, "length": length, "trajectory": trajectory}


def add_codex(c1: Any, c2: Any) -> Dict[str, Any]:
    """∫_{uv} = ∫_u + ∫_v  (Theorem 25.2.1)."""
    a: List[int] = c1["cod18"] if isinstance(c1, dict) else c1
    b: List[int] = c2["cod18"] if isinstance(c2, dict) else c2
    merged = [a[i] + b[i] for i in range(18)]
    return {"cod18": merged, "length": 0, "trajectory": []}


def layer_integrals(text: str) -> Dict[str, Any]:
    """Layer-wise integrals (Ch 26)."""
    cod = string_integral(text)
    v = cod["cod18"]
    U = compute_U(v)
    return {
        "theta": v[0],
        "N": [v[1], v[2], v[3]],
        "K": [v[4], v[5], v[6], v[7], v[8]],
        "Q": [v[9], v[10], v[11], v[12], v[13]],
        "U": U,
        "rho": v[0] - U,
    }


def layer_integrals_from_cod(cod: Any) -> Dict[str, Any]:
    """Layer integrals from pre-computed codex."""
    v: List[int] = cod["cod18"] if isinstance(cod, dict) else cod
    U = compute_U(v)
    return {
        "theta": v[0],
        "N": [v[1], v[2], v[3]],
        "K": [v[4], v[5], v[6], v[7], v[8]],
        "Q": [v[9], v[10], v[11], v[12], v[13]],
        "U": U,
        "rho": v[0] - U,
    }


def centroid(text: str) -> List[float]:
    """v̄(w) = (1/n) Σ v₁₈(xᵢ)  (Def 27.1.1)."""
    cod = string_integral(text)
    n = cod["length"]
    if n == 0:
        return [0.0] * 18
    v = cod["cod18"]
    return [v[i] / n for i in range(18)]


def cumulative(text: str) -> List[List[int]]:
    """Cumulative trajectory S₀, S₁, …, Sₙ  (Def 27.2.1)."""
    return string_integral(text)["trajectory"]


def energy_integral(text: str) -> int:
    """∫_w Φ = Σ Φ(xᵢ)  (Def 27.3.1)."""
    total = 0
    for ch in text:
        entry = MASTER_TABLE.get_by_char(ch)
        if entry is not None:
            E = build_exomatrix(entry)
            phi_val: int = int(sum(E[r][c] ** 2 for r in range(5) for c in range(5)))
            total = total + phi_val
    return total


def mean_theta(text: str) -> float:
    """Mean turning: (1/n) ∫_w Θ̂  (Thm 26.1.1)."""
    li = layer_integrals(text)
    cod = string_integral(text)
    n = cod["length"]
    return li["theta"] / n if n else 0.0


def min_component_theta(text: str) -> int:
    """Minimum Θ̂ among letters in text."""
    values: List[int] = []
    for ch in text:
        entry = MASTER_TABLE.get_by_char(ch)
        if entry is not None:
            values.append(entry.vector[0])
    return min(values) if values else 0


def max_component_theta(text: str) -> int:
    """Maximum Θ̂ among letters in text."""
    values: List[int] = []
    for ch in text:
        entry = MASTER_TABLE.get_by_char(ch)
        if entry is not None:
            values.append(entry.vector[0])
    return max(values) if values else 0
