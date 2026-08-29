#!/usr/bin/env python3
"""Verify Master Table integrity."""

from __future__ import annotations

import os
import sys

# Runtime path setup
_src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

from hijaiyyah.core.guards import guard_check  # noqa: E402
from hijaiyyah.core.master_table import MASTER_TABLE  # noqa: E402
from hijaiyyah.integrity.injectivity import InjectivityVerifier  # noqa: E402


def main() -> None:
    """Run integrity checks on the Master Table."""
    entries = MASTER_TABLE.all_entries()

    print(f"Letters:     {len(entries)}/28")
    print(f"SHA-256:     {MASTER_TABLE.compute_sha256()[:20]}...")

    all_guards = all(guard_check(e) for e in entries)
    print(f"Guards:      {'[OK]' if all_guards else '[FAIL]'}")

    injective = InjectivityVerifier().verify()
    print(f"Injectivity: {'[OK]' if injective else '[FAIL]'}")

    if all_guards and injective:
        print("\nAll checks passed. Dataset integrity confirmed.")
    else:
        print("\nWARNING: Some checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
