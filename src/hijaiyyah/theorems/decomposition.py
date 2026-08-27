"""Quadrant decomposition: Θ̂ = U + ρ (Proposition 11.3.1)."""

from ..core.guards import compute_rho, compute_U
from ..core.master_table import MASTER_TABLE


class QuadrantDecomposer:
    def decompose(self, h) -> dict:
        v = list(h.vector) if hasattr(h, "vector") else h
        U = compute_U(v)
        rho = compute_rho(v)
        return {
            "theta": v[0],
            "U": U,
            "rho": rho,
            "valid": rho >= 0,
            "identity_holds": v[0] == U + rho,
        }

    def verify_all(self) -> bool:
        return all(self.decompose(e)["valid"] for e in MASTER_TABLE.all_entries())
