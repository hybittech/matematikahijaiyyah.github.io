#!/usr/bin/env python3
"""
gen_rom.py — Generate Verilog ROM initialization hex from hm28.json

Reads the Master Table JSON and outputs a hex file suitable for
$readmemh in testbenches or FPGA block RAMs.

Output format: One 36-hex-digit line per entry (144-bit vector),
               component[17] at MSB, component[0] at LSB.

Usage:
    python gen_rom.py > rom_init.hex
    python gen_rom.py --format verilog > hcpu_rom_data.vh

(c) 2026 HMCL
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Locate hm28.json relative to script
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_PATH = SCRIPT_DIR.parent.parent / "data" / "hm28.json"


def load_master_table(path: Path) -> list[list[int]]:
    """Load hm28.json and return list of vectors indexed 1–28."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    vectors = [None]  # Index 0 unused (letters are 1-based)
    for name, entry in data["data"].items():
        idx = entry["index"]
        vec = entry["vector"]
        assert len(vec) == 18, f"{name}: expected 18 components, got {len(vec)}"
        # Ensure list is at correct index
        while len(vectors) <= idx:
            vectors.append(None)
        vectors[idx] = vec

    return vectors


def vec_to_hex144(vec: list[int]) -> str:
    """Convert 18-component vector to 36 hex digits (144-bit).

    Layout: component[17] at MSB (leftmost), component[0] at LSB.
    This matches the Verilog concatenation {comp[17], ..., comp[0]}.
    """
    # Pack from MSB (comp[17]) to LSB (comp[0])
    hex_str = ""
    for i in range(17, -1, -1):
        hex_str += f"{vec[i]:02X}"
    return hex_str


def main():
    fmt = "hex"
    if "--format" in sys.argv:
        idx = sys.argv.index("--format")
        if idx + 1 < len(sys.argv):
            fmt = sys.argv[idx + 1]

    if not DATA_PATH.exists():
        print(f"ERROR: {DATA_PATH} not found", file=sys.stderr)
        sys.exit(1)

    vectors = load_master_table(DATA_PATH)

    if fmt == "hex":
        # $readmemh format: one hex number per line, address comments
        for i in range(1, 29):
            vec = vectors[i]
            print(f"{vec_to_hex144(vec)}  // Index {i}")

    elif fmt == "verilog":
        # Verilog case statement include file
        print("// Auto-generated from hm28.json — do not edit")
        print("// Include in hcpu_rom.v case statement")
        names = [
            "Alif", "Ba", "Ta", "Tsa", "Jim", "Ha", "Kha",
            "Dal", "Dzal", "Ra", "Zay", "Sin", "Syin",
            "Shad", "Dhad", "Tha", "Zha", "Ain", "Ghain",
            "Fa", "Qaf", "Kaf", "Lam", "Mim", "Nun",
            "Waw", "Haa", "Ya"
        ]
        for i in range(1, 29):
            vec = vectors[i]
            name = names[i - 1]
            concat = ", ".join(f"8'd{v}" for v in reversed(vec))
            print(f"5'd{i:2d}: data_out = {{{concat}}}; // {name} {vec}")

    else:
        print(f"Unknown format: {fmt}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
