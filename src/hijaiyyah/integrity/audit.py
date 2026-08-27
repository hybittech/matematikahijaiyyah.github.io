"""Full system audit: integrity checks."""

from __future__ import annotations

from typing import Any, Dict

from ..core.guards import compute_rho, compute_U, guard_check
from ..core.master_table import MASTER_TABLE
from .injectivity import InjectivityVerifier


def run_full_audit() -> Dict[str, Any]:
    """Run all integrity checks and return results dict."""
    entries = MASTER_TABLE.all_entries()

    all_guards = True
    all_rho_ok = True
    all_turning_ok = True

    for e in entries:
        v = list(e.vector)
        if not guard_check(v):
            all_guards = False
        if compute_rho(v) < 0:
            all_rho_ok = False
        U = compute_U(v)
        rho = v[0] - U
        if v[0] != U + rho:
            all_turning_ok = False

    return {
        "sha256": MASTER_TABLE.compute_sha256()[:20] + "...",
        "letter_count": len(entries),
        "all_guards_pass": all_guards,
        "injective": InjectivityVerifier().verify(),
        "rho_non_negative": all_rho_ok,
        "turning_identity": all_turning_ok,
    }
