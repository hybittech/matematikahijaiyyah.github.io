"""
Execution parity: the Python HVM against the HCPU RTL.

test_isa_parity.py pins the numbers. This pins the behaviour — and the two are
not the same guarantee. HLOAD is the case that proves it: both sides agreed the
opcode was 0x40 and still disagreed about what it did, because the HVM indexed
the letter table from 0 while the ROM numbers letters from 1. `HLOAD H0, #2`
loaded Ba on hardware and Ta in software. Nothing crashed and no guard failed,
because every canonical letter passes every guard; the program simply computed
with the wrong letter.

Each program below is assembled once and run twice — through HISAMachine, and
through hcpu_top under Icarus Verilog via rtl/tb/tb_parity.v — then the final
architectural state is compared register by register.

Only opcodes both machines implement can appear here. RTL_IMPLEMENTED lists
what the hardware executes; anything outside it would halt the HCPU with
HALT_ERR and prove nothing.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, NamedTuple, Tuple

import pytest

from hijaiyyah.core.master_table import MASTER_TABLE
from hijaiyyah.hisa.machine import HISAMachine
from hijaiyyah.hisa.opcodes import RTL_IMPLEMENTED, OpCode

ROOT = Path(__file__).resolve().parents[2]
TB_PARITY = ROOT / "rtl" / "tb" / "tb_parity.v"

GPR_COUNT = 18
HREG_COUNT = 16
MAX_CYCLES = 400

pytestmark = pytest.mark.skipif(
    shutil.which("iverilog") is None and os.environ.get("HOM_REQUIRE_IVERILOG") != "1",
    reason="Icarus Verilog is required to execute the RTL",
)


# ── Assembly helper ──────────────────────────────────────────────

def enc(op: OpCode, dst: int = 0, s1: int = 0, s2: int = 0, imm: int = 0) -> int:
    """Same field layout as `enc` in the Verilog testbenches."""
    assert op in RTL_IMPLEMENTED, f"{op.name} is not implemented by the HCPU"
    return (
        (int(op) << 24)
        | ((dst & 0xF) << 20)
        | ((s1 & 0xF) << 16)
        | ((s2 & 0xF) << 12)
        | (imm & 0xFFF)
    )


class State(NamedTuple):
    gpr: Tuple[int, ...]
    hreg: Tuple[Tuple[int, ...], ...]
    guard: bool
    halted: bool


# ── The two machines ─────────────────────────────────────────────

def run_hvm(program: List[int]) -> State:
    machine = HISAMachine(MASTER_TABLE)
    machine.load_program(list(program))
    for _ in range(MAX_CYCLES):
        if machine.step() is None:
            break
    regs = machine.regs
    return State(
        gpr=tuple(regs.gpr[:GPR_COUNT]),
        hreg=tuple(tuple(h) for h in regs.hreg[:HREG_COUNT]),
        guard=bool(regs.sr.guard_pass),
        halted=True,
    )


@pytest.fixture(scope="session")
def rtl_sim(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Compile hcpu_top with the parity harness once for the whole session."""
    out = tmp_path_factory.mktemp("rtl") / "tb_parity.vvp"
    sources = [str(TB_PARITY), *sorted(str(p) for p in (ROOT / "rtl").glob("*.v"))]
    proc = subprocess.run(
        ["iverilog", "-g2012", "-I", str(ROOT / "rtl"), "-o", str(out), *sources],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, f"iverilog failed:\n{proc.stderr}"
    return out


def run_rtl(sim: Path, program: List[int], tmp_path: Path) -> State:
    hexfile = tmp_path / "program.hex"
    hexfile.write_text("".join(f"{w:08X}\n" for w in program), encoding="utf-8")

    proc = subprocess.run(
        ["vvp", str(sim), f"+PROGRAM={hexfile}", f"+CYCLES={MAX_CYCLES}"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, f"vvp failed:\n{proc.stdout}\n{proc.stderr}"

    gpr: Dict[int, int] = {}
    hreg: Dict[int, Tuple[int, ...]] = {}
    halted = False
    flags = 0

    for line in proc.stdout.splitlines():
        # Icarus prints %X in lower case, so match either.
        if m := re.fullmatch(r"GPR\[(\d+)\]=([0-9A-Fa-f]{8})", line.strip()):
            gpr[int(m.group(1))] = int(m.group(2), 16)
        elif m := re.fullmatch(r"HREG\[(\d+)\]=([0-9A-Fa-f]{36})", line.strip()):
            packed = int(m.group(2), 16)
            # comp[i] occupies bits [8i +: 8], so the hex string runs
            # comp17 .. comp0 from the left.
            hreg[int(m.group(1))] = tuple(
                (packed >> (8 * i)) & 0xFF for i in range(18)
            )
        elif m := re.fullmatch(r"HALTED=(\d+)", line.strip()):
            halted = m.group(1) == "1"
        elif m := re.fullmatch(r"FLAGS=([0-9A-Fa-f]{2})", line.strip()):
            flags = int(m.group(1), 16)

    assert len(gpr) == GPR_COUNT, f"parsed {len(gpr)} GPRs, expected {GPR_COUNT}"
    assert len(hreg) == HREG_COUNT, f"parsed {len(hreg)} H-regs, expected {HREG_COUNT}"

    return State(
        gpr=tuple(gpr[i] for i in range(GPR_COUNT)),
        hreg=tuple(hreg[i] for i in range(HREG_COUNT)),
        guard=bool(flags & 0x01),  # FLAG_G
        halted=halted,
    )


# ── Programs ─────────────────────────────────────────────────────
# Letter indices are 1-based, matching the ROM and CodexEntry.index.

BA, SIN, MIM = 2, 12, 24

PROGRAMS: Dict[str, List[int]] = {
    "load_one_letter": [
        enc(OpCode.HLOAD, dst=0, imm=BA),
        enc(OpCode.HALT),
    ],
    "load_three_letters": [
        enc(OpCode.HLOAD, dst=0, imm=BA),
        enc(OpCode.HLOAD, dst=1, imm=SIN),
        enc(OpCode.HLOAD, dst=3, imm=MIM),
        enc(OpCode.HALT),
    ],
    "guard_a_letter": [
        enc(OpCode.HLOAD, dst=0, imm=BA),
        enc(OpCode.HGRD, s1=0),
        enc(OpCode.HALT),
    ],
    "codex_add": [
        enc(OpCode.HLOAD, dst=0, imm=BA),
        enc(OpCode.HLOAD, dst=1, imm=SIN),
        enc(OpCode.HCADD, dst=2, s1=0, s2=1),
        enc(OpCode.HALT),
    ],
    "string_integral_bsm": [
        enc(OpCode.HLOAD, dst=0, imm=BA),
        enc(OpCode.HLOAD, dst=1, imm=SIN),
        enc(OpCode.HLOAD, dst=3, imm=MIM),
        enc(OpCode.HCADD, dst=2, s1=0, s2=1),
        enc(OpCode.HCADD, dst=2, s1=2, s2=3),
        enc(OpCode.HGRD, s1=2),
        enc(OpCode.HALT),
    ],
    "norm_of_a_letter": [
        enc(OpCode.HLOAD, dst=0, imm=MIM),
        enc(OpCode.HNRM2, dst=5, s1=0),
        enc(OpCode.HALT),
    ],
    "distance_between_letters": [
        enc(OpCode.HLOAD, dst=0, imm=BA),
        enc(OpCode.HLOAD, dst=1, imm=SIN),
        enc(OpCode.HDIST, dst=4, s1=0, s2=1),
        enc(OpCode.HALT),
    ],
    "every_letter_loads": [
        *(enc(OpCode.HLOAD, dst=i % HREG_COUNT, imm=i + 1) for i in range(28)),
        enc(OpCode.HALT),
    ],
}


# ── The comparison ───────────────────────────────────────────────

@pytest.mark.parametrize("name", sorted(PROGRAMS), ids=sorted(PROGRAMS))
def test_hreg_state_agrees(name: str, rtl_sim: Path, tmp_path: Path) -> None:
    program = PROGRAMS[name]
    hvm, rtl = run_hvm(program), run_rtl(rtl_sim, program, tmp_path)

    assert rtl.halted, f"{name}: the HCPU never reached HALT"

    for i, (a, b) in enumerate(zip(hvm.hreg, rtl.hreg, strict=True)):
        assert a == b, (
            f"{name}: H{i} differs\n"
            f"  HVM = {list(a)}\n"
            f"  RTL = {list(b)}"
        )


@pytest.mark.parametrize("name", sorted(PROGRAMS), ids=sorted(PROGRAMS))
def test_gpr_state_agrees(name: str, rtl_sim: Path, tmp_path: Path) -> None:
    program = PROGRAMS[name]
    hvm, rtl = run_hvm(program), run_rtl(rtl_sim, program, tmp_path)

    assert hvm.gpr == rtl.gpr, (
        f"{name}: GPRs differ\n"
        f"  HVM = {list(hvm.gpr)}\n"
        f"  RTL = {list(rtl.gpr)}"
    )


@pytest.mark.parametrize("name", sorted(PROGRAMS), ids=sorted(PROGRAMS))
def test_guard_flag_agrees(name: str, rtl_sim: Path, tmp_path: Path) -> None:
    program = PROGRAMS[name]
    hvm, rtl = run_hvm(program), run_rtl(rtl_sim, program, tmp_path)

    assert hvm.guard == rtl.guard, (
        f"{name}: GUARD flag differs — HVM={hvm.guard}, RTL={rtl.guard}"
    )


# ── Guards on the harness itself ─────────────────────────────────

def test_programs_only_use_hardware_opcodes() -> None:
    for name, program in PROGRAMS.items():
        for word in program:
            op = OpCode((word >> 24) & 0xFF)
            assert op in RTL_IMPLEMENTED, f"{name} uses software-only {op.name}"


def test_the_harness_can_tell_states_apart(rtl_sim: Path, tmp_path: Path) -> None:
    """
    A comparison that always passes would be worse than no comparison. Two
    programs that load different letters must produce different RTL states.
    """
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(exist_ok=True)
    b.mkdir(exist_ok=True)

    ba = run_rtl(rtl_sim, PROGRAMS["load_one_letter"], a)
    mim = run_rtl(rtl_sim, [enc(OpCode.HLOAD, dst=0, imm=MIM), enc(OpCode.HALT)], b)

    assert ba.hreg[0] != mim.hreg[0], "the harness cannot distinguish two letters"
