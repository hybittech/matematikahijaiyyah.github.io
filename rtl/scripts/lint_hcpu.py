#!/usr/bin/env python3
"""
HCPU Verilator Lint Runner — lint_hcpu.py
Runs Verilator --lint-only on the full HCPU RTL design.
(c) 2026 HMCL — Hybit Technology

Usage:
    python lint_hcpu.py                # Auto-detect verilator
    python lint_hcpu.py --verilator /path/to/verilator
    python lint_hcpu.py --top hcpu_xilinx_top  # Lint FPGA wrapper

Output:
    - Exit code 0: lint clean
    - Exit code 1: lint errors found
    - Writes lint_report.txt
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# ── RTL source files (relative to rtl/) ────────────────────────
CORE_SOURCES = [
    "hcpu_pkg.vh",
    "hcpu_top.v",
    "hcpu_fetch.v",
    "hcpu_decode.v",
    "hcpu_execute.v",
    "hcpu_mul.v",
    "hcpu_memory.v",
    "hcpu_writeback.v",
    "hcpu_regfile.v",
    "hcpu_forward.v",
    "hcpu_controller.v",
    "hcpu_rom.v",
    "hcpu_guard.v",
    "hcpu_codex_alu.v",
    "hcpu_dataram.v",
    "hcpu_uart_tx.v",
]

FPGA_SOURCES = [
    *CORE_SOURCES,
    "fpga/xilinx/hcpu_xilinx_top.v",
]

MPW_SOURCES = [
    *CORE_SOURCES,
    "mpw/hcpu_wb_adapter.v",
    "mpw/hcpu_mpw_top.v",
]


def find_verilator():
    """Try to find verilator in PATH."""
    for name in ["verilator", "verilator.exe"]:
        try:
            result = subprocess.run(
                [name, "--version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return name
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None


def run_lint(verilator_bin, top_module, sources, rtl_dir, report_file):
    """Run Verilator lint and return (returncode, stdout, stderr)."""
    cmd = [
        verilator_bin,
        "--lint-only",
        "-Wall",
        "--top-module", top_module,
        f"-I{rtl_dir}",
    ]

    # Add all source files with absolute paths
    for src in sources:
        src_path = os.path.join(rtl_dir, src)
        if os.path.exists(src_path):
            cmd.append(src_path)
        else:
            print(f"WARNING: Source file not found: {src_path}")

    print(f"Running: {' '.join(cmd[:6])} ... ({len(sources)} files)")
    print(f"Top module: {top_module}")
    print()

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120
    )

    # Write report
    with open(report_file, "w") as f:
        f.write("HCPU Verilator Lint Report\n")
        f.write(f"{'=' * 60}\n")
        f.write(f"Top module: {top_module}\n")
        f.write(f"Sources: {len(sources)} files\n")
        f.write(f"Exit code: {result.returncode}\n")
        f.write(f"{'=' * 60}\n\n")
        if result.stdout:
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n")
        if result.stderr:
            f.write("STDERR:\n")
            f.write(result.stderr)
            f.write("\n")

        # Count warnings/errors
        warnings = result.stderr.count("%Warning")
        errors = result.stderr.count("%Error")
        f.write(f"\n{'=' * 60}\n")
        f.write(f"Summary: {errors} errors, {warnings} warnings\n")

        if errors == 0 and warnings == 0:
            f.write("STATUS: LINT CLEAN ✅\n")
        elif errors == 0:
            f.write(f"STATUS: {warnings} WARNINGS (no errors) ⚠️\n")
        else:
            f.write(f"STATUS: {errors} ERRORS ❌\n")

    return result


def main():
    parser = argparse.ArgumentParser(description="HCPU Verilator Lint Runner")
    parser.add_argument("--verilator", default=None, help="Path to verilator binary")
    parser.add_argument("--top", default="hcpu_top",
                        choices=["hcpu_top", "hcpu_xilinx_top", "hcpu_mpw_top"],
                        help="Top module to lint")
    parser.add_argument("--report", default=None, help="Output report file")
    args = parser.parse_args()

    # Find verilator
    verilator_bin = args.verilator or find_verilator()
    if not verilator_bin:
        print("ERROR: verilator not found in PATH.")
        print("Install with: sudo apt install verilator  (Linux)")
        print("          or: choco install verilator      (Windows)")
        print("          or: brew install verilator        (macOS)")
        sys.exit(1)

    # Determine RTL directory
    script_dir = Path(__file__).parent
    rtl_dir = str(script_dir.parent)

    # Select sources based on top module
    if args.top == "hcpu_xilinx_top":
        sources = FPGA_SOURCES
    elif args.top == "hcpu_mpw_top":
        sources = MPW_SOURCES
    else:
        sources = CORE_SOURCES

    report_file = args.report or os.path.join(rtl_dir, f"lint_report_{args.top}.txt")

    # Run lint
    result = run_lint(verilator_bin, args.top, sources, rtl_dir, report_file)

    # Print summary
    print(result.stderr if result.stderr else "(no output)")
    print()
    errors = result.stderr.count("%Error")
    warnings = result.stderr.count("%Warning")

    if errors == 0 and warnings == 0:
        print("✅ LINT CLEAN — no errors, no warnings")
    elif errors == 0:
        print(f"⚠️  {warnings} warnings (no errors)")
    else:
        print(f"❌ {errors} errors, {warnings} warnings")

    print(f"Report written to: {report_file}")
    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
