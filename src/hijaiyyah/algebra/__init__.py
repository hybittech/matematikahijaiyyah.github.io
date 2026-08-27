"""
Bab II: Sistem Operasi Metrik-Vektorial Hijaiyah.

  vektronometry      — VTM (Bab II-A)
  normivektor        — NMV (Bab II-B)
  aggregametric      — AGM (Bab II-C)
  intrametric        — ITM (Bab II-D)
  exometric          — EXM (Bab II-E)

Backward-compatible aliases are provided for the old names.
"""

from . import (
    aggregametric,
    exometric,
    intrametric,
    normivektor,
    vektronometry,
)
from . import aggregametric as integral
from . import exometric as exomatrix_analysis
from . import intrametric as geometry
from . import normivektor as differential

# ── Backward-compatible aliases (v1.0 → v1.2) ──
from . import vektronometry as vectronometry
