#!/usr/bin/env python3
"""
cross_verify_rom.py — Cross-verify hcpu_rom.v encoding against hm28.json

This script parses the Verilog ROM case statements and compares them
against the golden hm28.json data to catch any encoding errors.

Usage: python cross_verify_rom.py
"""

import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent  # hijaiyyah-mathematics/
DATA_PATH = ROOT_DIR / "data" / "hm28.json"
ROM_PATH = ROOT_DIR / "rtl" / "hcpu_rom.v"

# Component names for readable output
COMP_NAMES = [
    "Θ̂", "Na", "Nb", "Nd", "Kp", "Kx", "Ks", "Ka", "Kc",
    "Qp", "Qx", "Qs", "Qa", "Qc", "AN", "AK", "AQ", "Ψ"
]


def load_golden() -> dict[int, list[int]]:
    """Load golden vectors from hm28.json."""
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    
    vectors = {}
    for entry in data["data"].values():
        idx = entry["index"]
        vec = entry["vector"]
        assert len(vec) == 18
        vectors[idx] = vec
    return vectors


def parse_rom_verilog() -> dict[int, list[int]]:
    """Parse hcpu_rom.v and extract vectors from case statements.
    
    The format is: {8'd<comp17>, 8'd<comp16>, ..., 8'd<comp1>, 8'd<comp0>}
    So the concatenation is MSB-first: comp[17] at left, comp[0] at right.
    """
    rom_text = ROM_PATH.read_text(encoding="utf-8")
    
    vectors = {}
    
    # Match case entries like: 5'd1: data_out = {8'd0,8'd0,...};
    pattern = r"5'd(\d+):\s*data_out\s*=\s*\{([^}]+)\};"
    
    for match in re.finditer(pattern, rom_text):
        idx = int(match.group(1))
        values_str = match.group(2)
        
        # Extract all 8'd<N> values
        vals = re.findall(r"8'd(\d+)", values_str)
        vals = [int(v) for v in vals]
        
        assert len(vals) == 18, f"Index {idx}: expected 18 values, got {len(vals)}"
        
        # The concatenation is {comp[17], comp[16], ..., comp[1], comp[0]}
        # So vals[0] = comp[17], vals[1] = comp[16], ..., vals[17] = comp[0]
        # We need to reverse to get comp[0], comp[1], ..., comp[17]
        vec = list(reversed(vals))
        
        vectors[idx] = vec
    
    return vectors


def main():
    print("=" * 60)
    print("HCPU ROM Cross-Verification against hm28.json")
    print("=" * 60)
    
    golden = load_golden()
    rom = parse_rom_verilog()
    
    pass_count = 0
    fail_count = 0
    
    letter_names = [
        None,  # index 0 unused
        "Alif", "Ba", "Ta", "Tsa", "Jim", "Ha", "Kha",
        "Dal", "Dzal", "Ra", "Zay", "Sin", "Syin",
        "Shad", "Dhad", "Tha", "Zha", "Ain", "Ghain",
        "Fa", "Qaf", "Kaf", "Lam", "Mim", "Nun",
        "Waw", "Haa", "Ya"
    ]
    
    for idx in range(1, 29):
        name = letter_names[idx]
        g = golden[idx]
        
        if idx not in rom:
            print(f"FAIL [{idx:2d}] {name:6s}: NOT FOUND in ROM")
            fail_count += 1
            continue
        
        r = rom[idx]
        
        if g == r:
            print(f"PASS [{idx:2d}] {name:6s}: {g}")
            pass_count += 1
        else:
            print(f"FAIL [{idx:2d}] {name:6s}:")
            print(f"  Golden: {g}")
            print(f"  ROM:    {r}")
            # Show which components differ
            diffs = []
            for i in range(18):
                if g[i] != r[i]:
                    diffs.append(f"  comp[{i}] ({COMP_NAMES[i]}): golden={g[i]}, rom={r[i]}")
            for d in diffs:
                print(d)
            fail_count += 1
    
    # Check coverage
    missing = set(range(1, 29)) - set(rom.keys())
    extra = set(rom.keys()) - set(range(1, 29))
    
    print()
    print("=" * 60)
    print(f"Results: {pass_count} PASS, {fail_count} FAIL")
    if missing:
        print(f"Missing indices: {sorted(missing)}")
    if extra:
        print(f"Extra indices: {sorted(extra)}")
    print("=" * 60)
    
    return fail_count


if __name__ == "__main__":
    exit(main())
