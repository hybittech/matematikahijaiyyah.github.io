"""
The Tang Nano 9K board wrapper, simulated as the board would run it.

Simulating the core alone cannot catch a wrapper bug, because the core behaves
exactly as it is parameterised. The wrapper handed hcpu_top CLK_HZ = 50_000_000
while a placeholder PLL — whose body was `assign clkout = clkin` — passed the
27 MHz oscillator straight through. CLKS_PER_BIT was sized for a clock that did
not exist, putting the serial line at 62,212 baud instead of 115,200. That is
46% out, against the 2-3% a receiver tolerates, so nothing legible would ever
have reached the port.

tb_gowin_top.v runs the wrapper at the real 27 MHz and decodes uart_txd with a
receiver that times bits from the baud the board expects, independently of the
design. The program is rtl/programs/test_bsm.hasm, which prints the squared
norm of Ba + Sin + Mim.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from hijaiyyah.algebra import vektronometry as vtm
from hijaiyyah.core.master_table import MASTER_TABLE

ROOT = Path(__file__).resolve().parents[2]
GOWIN = ROOT / "rtl" / "fpga" / "gowin"

pytestmark = pytest.mark.skipif(
    shutil.which("iverilog") is None and os.environ.get("HOM_REQUIRE_IVERILOG") != "1",
    reason="Icarus Verilog is required to simulate the wrapper",
)


def _expected_norm() -> int:
    """‖Ba + Sin + Mim‖² over v14, from the Python side."""
    total = [0] * 18
    for char in ("ب", "س", "م"):
        entry = MASTER_TABLE.get_by_char(char)
        assert entry is not None
        for i, value in enumerate(entry.vector):
            total[i] += value
    return vtm.norm2(total)


@pytest.fixture(scope="module")
def simulation(tmp_path_factory: pytest.TempPathFactory) -> str:
    """Build and run the wrapper testbench, returning its stdout."""
    build = tmp_path_factory.mktemp("gowin")
    vvp = build / "tb_gowin_top.vvp"

    sources = [
        str(ROOT / "rtl" / "tb" / "tb_gowin_top.v"),
        str(GOWIN / "hcpu_gowin_top.v"),
        *sorted(str(p) for p in (ROOT / "rtl").glob("*.v")),
    ]
    compile_result = subprocess.run(
        ["iverilog", "-g2012", "-I", str(ROOT / "rtl"), "-o", str(vvp), *sources],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert compile_result.returncode == 0, f"iverilog failed:\n{compile_result.stderr}"

    # The wrapper reads program.hex relative to the working directory, exactly
    # as the FPGA build does.
    run = subprocess.run(
        ["vvp", str(vvp)],
        cwd=GOWIN,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert run.returncode == 0, f"simulation failed:\n{run.stdout}\n{run.stderr}"
    return run.stdout


def _characters(output: str) -> str:
    return "".join(
        chr(int(m.group(1), 16))
        for m in re.finditer(r"^\s+\[\d+\] 0x([0-9a-fA-F]{2})", output, re.M)
    )


# ── The serial line ──────────────────────────────────────────────

def test_something_reaches_the_serial_pin(simulation: str) -> None:
    match = re.search(r"Characters received: (\d+)", simulation)
    assert match, "the testbench did not report a character count"
    assert int(match.group(1)) > 0, "nothing came out of uart_txd"


def test_uart_output_decodes_at_the_boards_baud(simulation: str) -> None:
    """
    The receiver times bits from 115200, so this only passes if the design
    really transmits at that rate from a 27 MHz clock.
    """
    assert "PASS: UART emitted the expected characters" in simulation


def test_the_printed_value_matches_the_python_reference(simulation: str) -> None:
    text = _characters(simulation)
    assert text.strip() == str(_expected_norm()), (
        f"board printed {text.strip()!r}, Python computes {_expected_norm()}"
    )


def test_the_testbench_reports_no_failures(simulation: str) -> None:
    match = re.search(r"Gowin wrapper: (\d+) PASS, (\d+) FAIL", simulation)
    assert match, "no summary line"
    assert int(match.group(1)) > 0
    assert int(match.group(2)) == 0


# ── The wrapper's own consistency ────────────────────────────────

def test_the_clock_frequency_is_derived_not_repeated() -> None:
    """
    The original bug was two numbers that had to agree by hand and did not.
    SYS_HZ must be computed from the oscillator, never written as a literal.
    """
    source = (GOWIN / "hcpu_gowin_top.v").read_text(encoding="utf-8")
    match = re.search(r"localparam\s+SYS_HZ\s*=\s*([^;]+);", source)
    assert match, "SYS_HZ is not declared"
    assert "OSC_HZ" in match.group(1), (
        f"SYS_HZ = {match.group(1).strip()} — it must derive from OSC_HZ"
    )


def test_no_placeholder_pll_passes_the_clock_through() -> None:
    """
    A stub PLL whose body was `assign clkout = clkin` is what let the design
    claim 50 MHz while running at 27. With USE_PLL enabled the build should
    fail for want of real vendor IP, not quietly succeed.
    """
    source = (GOWIN / "hcpu_gowin_top.v").read_text(encoding="utf-8")
    assert "module Gowin_rPLL" not in source, "the placeholder PLL is back"


def test_program_hex_is_plain_ascii() -> None:
    """
    The Xilinx copy of this file was UTF-16; $readmemh rejects it outright and
    leaves the instruction memory uninitialised without failing the build.
    """
    for path in (
        GOWIN / "program.hex",
        ROOT / "rtl" / "fpga" / "xilinx" / "program.hex",
    ):
        assert path.exists(), f"missing {path}"
        data = path.read_bytes()
        assert data[:2] not in (b"\xff\xfe", b"\xfe\xff"), f"{path} has a UTF-16 BOM"
        data.decode("ascii")  # raises if anything is not ASCII


def test_program_hex_matches_its_assembly_source() -> None:
    """
    Both program.hex files are checked in, so they can go stale against the
    .hasm they came from — which is how the Xilinx copy ended up UTF-16 and
    unreadable while the build kept reporting success.
    """
    asm2hex = ROOT / "rtl" / "scripts" / "asm2hex.py"
    source = ROOT / "rtl" / "programs" / "test_bsm.hasm"

    result = subprocess.run(
        [sys.executable, str(asm2hex), str(source)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"asm2hex failed:\n{result.stderr}"

    def words(text: str) -> list:
        return [
            line.split()[0]
            for line in text.splitlines()
            if line.strip() and not line.strip().startswith("//")
        ]

    expected = words(result.stdout)
    assert expected, "asm2hex produced nothing"

    for path in (
        GOWIN / "program.hex",
        ROOT / "rtl" / "fpga" / "xilinx" / "program.hex",
    ):
        assert words(path.read_text(encoding="ascii")) == expected, (
            f"{path} is stale — regenerate it with "
            f"`python rtl/scripts/asm2hex.py {source.name}`"
        )
