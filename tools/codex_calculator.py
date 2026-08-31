#!/usr/bin/env python3
"""CLI codex computation tool."""

from __future__ import annotations

import os
import sys
from typing import List

# Runtime path setup
_src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

from hijaiyyah.algebra.aggregametric import string_integral  # noqa: E402
from hijaiyyah.core.guards import compute_U  # noqa: E402


def main() -> None:
    """Compute and display the string codex for input text."""
    args: List[str] = sys.argv
    if len(args) > 1:
        text = " ".join(args[1:])
    else:
        text = "بسم"

    result = string_integral(text)
    print(f"Text:    {text}")
    print(f"Length:  {result['length']} Hijaiyyah letters")
    print(f"Cod₁₈:  {result['cod18']}")

    # Show turning decomposition
    v = result["cod18"]
    U = compute_U(v)
    rho = v[0] - U
    print(f"Θ̂={v[0]}  U={U}  ρ={rho}  (Θ̂=U+ρ: {v[0]==U+rho})")


if __name__ == "__main__":
    main()
