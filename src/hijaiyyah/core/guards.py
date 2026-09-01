"""
Guard check and audit detail for hybit/codex vectors.

Structural Guards (on raw v18) — Definition 3.3.1, Bab III:
  G1: A_N = Na + Nb + Nd       (Sum-check zona — konsistensi distribusi titik)
  G2: A_K = Kp + Kx + Ks + Ka + Kc  (Sum-check garis — konsistensi count garis)
  G3: A_Q = Qp + Qx + Qs + Qa + Qc  (Sum-check lengkung — konsistensi count lengkung)
  G4: ρ = Θ̂ − U ≥ 0           (Cross-constraint — kekekalan turning)

Topological Guards — Definition 3.3.1, Bab III:
  T1: Ks > 0 ⇒ Qc ≥ 1         (S-curve implies loop presence)
  T2: Kc > 0 ⇒ Qc ≥ 1         (Closed curve implies loop presence)

Audit relations R1–R5 (Identity 33.1.1):
  R1: Θ̂ = U + ρ               (Proposition 11.3.1)
  R2: A_N = Na + Nb + Nd       (Definition 12.2.1)
  R3: A_K = ΣK_j               (Definition 12.2.1)
  R4: A_Q = ΣQ_j               (Definition 12.2.1)
  R5: U = Qx + Qs + Qa + 4Qc  (Definition 11.1.1)
"""

from __future__ import annotations

from typing import Any, Dict, List


def _to_vec(v: Any) -> List[int]:
    """
    Normalize input to a list of 18 integers.
    Accepts: CodexEntry (has .vector), list, or tuple.
    """
    if hasattr(v, "vector"):
        return list(v.vector)
    if isinstance(v, (list, tuple)):
        return list(v)
    raise TypeError(f"Expected vector-like, got {type(v).__name__}")


def compute_U(v: Any) -> int:
    """U(h) = Qx + Qs + Qa + 4·Qc  (Definition 11.1.1)."""
    vec = _to_vec(v)
    return vec[10] + vec[11] + vec[12] + 4 * vec[13]


def compute_rho(v: Any) -> int:
    """ρ(h) = Θ̂ − U  (Definition 11.2.1)."""
    vec = _to_vec(v)
    return vec[0] - compute_U(vec)


def guard_check(v: Any) -> bool:
    """
    Check all 6 guards (4 structural + 2 topological).
    Returns True if all pass.
    Complexity: O(1) — fixed number of additions + comparisons.

    Structural:
      G1: A_N = Na + Nb + Nd
      G2: A_K = Kp + Kx + Ks + Ka + Kc
      G3: A_Q = Qp + Qx + Qs + Qa + Qc
      G4: ρ = Θ̂ − (Qx + Qs + Qa + 4·Qc) ≥ 0

    Topological:
      T1: Ks > 0 ⇒ Qc ≥ 1
      T2: Kc > 0 ⇒ Qc ≥ 1
    """
    vec = _to_vec(v)

    # Structural guards
    U = compute_U(vec)
    rho = vec[0] - U

    g1 = vec[14] == vec[1] + vec[2] + vec[3]
    g2 = vec[15] == vec[4] + vec[5] + vec[6] + vec[7] + vec[8]
    g3 = vec[16] == vec[9] + vec[10] + vec[11] + vec[12] + vec[13]
    g4 = rho >= 0

    # Topological guards (Definition 3.3.1)
    # T1: v[6]=Ks > 0 ⇒ v[13]=Qc ≥ 1
    t1 = vec[13] >= 1 if vec[6] > 0 else True
    # T2: v[8]=Kc > 0 ⇒ v[13]=Qc ≥ 1
    t2 = vec[13] >= 1 if vec[8] > 0 else True

    return g1 and g2 and g3 and g4 and t1 and t2


def full_guard_check(v: Any) -> Dict[str, bool]:
    """
    Check all 6 guards with per-guard results.
    Returns dict with G1–G4, T1, T2, and overall status.
    Complexity: O(1).
    """
    vec = _to_vec(v)

    U = compute_U(vec)
    rho = vec[0] - U

    g1 = vec[14] == vec[1] + vec[2] + vec[3]
    g2 = vec[15] == vec[4] + vec[5] + vec[6] + vec[7] + vec[8]
    g3 = vec[16] == vec[9] + vec[10] + vec[11] + vec[12] + vec[13]
    g4 = rho >= 0
    t1 = vec[13] >= 1 if vec[6] > 0 else True
    t2 = vec[13] >= 1 if vec[8] > 0 else True

    return {
        "G1": g1,
        "G2": g2,
        "G3": g3,
        "G4": g4,
        "T1": t1,
        "T2": t2,
        "all_pass": g1 and g2 and g3 and g4 and t1 and t2,
    }


def guard_detail(v: Any) -> Dict[str, Any]:
    """
    Check all 5 audit relations (R1–R5) plus topological guards
    with detailed output.
    """
    vec = _to_vec(v)

    U = compute_U(vec)
    rho = vec[0] - U

    R1 = (vec[0] == U + rho) and (rho >= 0)
    R2 = vec[14] == vec[1] + vec[2] + vec[3]
    R3 = vec[15] == vec[4] + vec[5] + vec[6] + vec[7] + vec[8]
    R4 = vec[16] == vec[9] + vec[10] + vec[11] + vec[12] + vec[13]
    R5 = U == compute_U(vec)

    # Topological guards
    T1 = vec[13] >= 1 if vec[6] > 0 else True
    T2 = vec[13] >= 1 if vec[8] > 0 else True

    return {
        "R1": R1,
        "R2": R2,
        "R3": R3,
        "R4": R4,
        "R5": R5,
        "T1": T1,
        "T2": T2,
        "U": U,
        "rho": rho,
        "all_pass": R1 and R2 and R3 and R4 and R5 and T1 and T2,
    }
