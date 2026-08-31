"""
Optional imports must resolve, or not be written.

Five modules guarded a delegation behind `try: ... except ImportError`, and
seven of the thirteen guards were catching a target that does not exist:

    hijaiyyah.core.codex.Codex              module never existed
    hijaiyyah.hisa.assembler.Assembler      the module exports functions
    hijaiyyah.hisa.compiler.HISACompiler    the class is HL18ECompiler
    hijaiyyah.skeleton.csgi.CSGIProcessor   the module has CSGIGraph
    hijaiyyah.hisa.hcheck.HCheck            the class is HCHECK

Each failure was silent by construction. The guard set the name to None, a
`if x and hasattr(x, 'method')` test downstream never fired, and a local
fallback ran instead — so every module carried two implementations, one of
them permanently dead, and nothing said so. hijaiyyah.assembler's fallback
emitted `bytes(count)`, a run of NUL bytes, so the .hbc it produced carried no
instructions at all.

This is the same shape as the divergences the parity suites exist to catch,
with one difference: the try/except was actively hiding it.
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path
from typing import List, Tuple

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

# try:
#     from a.b import C [as D]
# except ImportError:
_GUARDED = re.compile(
    r"try:\s*\n\s*from ([\w.]+) import (\w+)(?:\s+as\s+\w+)?\s*\n\s*except ImportError",
    re.M,
)


def _guarded_imports() -> List[Tuple[str, str, str]]:
    found: List[Tuple[str, str, str]] = []
    for path in sorted(SRC.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for match in _GUARDED.finditer(text):
            found.append(
                (str(path.relative_to(ROOT)), match.group(1), match.group(2))
            )
    return found


GUARDED = _guarded_imports()
IDS = [f"{f}:{m}.{n}" for f, m, n in GUARDED] or ["none"]


def test_the_scan_covers_the_source_tree() -> None:
    """A regex that matched nothing would make the check below vacuous."""
    assert SRC.is_dir()
    assert len(list(SRC.rglob("*.py"))) > 50


@pytest.mark.parametrize(
    ("source_file", "module", "name"),
    GUARDED or [("", "", "")],
    ids=IDS,
)
def test_guarded_import_resolves(source_file: str, module: str, name: str) -> None:
    """
    An optional import is only honest if the thing it reaches for exists. A
    guard around a target that was never written is dead code wearing a
    fallback's clothes.
    """
    if not module:
        pytest.skip("no guarded imports in the tree")

    try:
        imported = importlib.import_module(module)
    except ImportError as exc:
        pytest.fail(
            f"{source_file} guards `from {module} import {name}`, but the "
            f"module cannot be imported at all: {exc}"
        )

    assert hasattr(imported, name), (
        f"{source_file} guards `from {module} import {name}`, but {module} "
        f"defines no {name}. Either implement it or drop the guard — as it "
        "stands the fallback below is the only code that ever runs."
    )


# ── The consequence that made this worth fixing ──────────────────

def test_assembler_emits_real_instruction_words() -> None:
    """
    The dead delegation left `bytes(count)` as the encoder: NUL bytes, one per
    instruction. A .hbc built that way carries nothing executable.
    """
    from hijaiyyah.assembler import HASMAssembler

    result = HASMAssembler().assemble("HLOAD 0 0 0 2\nHGRD 0 0 0 0\nHALT")

    assert result.success, result.errors
    assert result.instruction_count == 3, "one count per instruction, not per byte"
    assert result.bytecode.endswith(
        bytes.fromhex("40000002") + bytes.fromhex("60000000") + bytes.fromhex("01000000")
    ), "the encoded words must match the frozen H-ISA"


def test_compiler_does_not_report_success_over_an_empty_result() -> None:
    """
    Code generation is not implemented. compile_source used to return
    success=True with zero instructions, which tells a caller their source
    compiled when nothing was produced.
    """
    from hijaiyyah.compiler import HCCompiler

    result = HCCompiler().compile_source("let h = 1; println(h);")

    assert result.success is False
    assert result.instruction_count == 0
    assert any("not implemented" in e for e in result.errors), result.errors


def test_available_stages_matches_what_the_compiler_can_do() -> None:
    from hijaiyyah.compiler import HCCompiler

    stages = HCCompiler().available_stages
    assert stages["lexer"] is True
    assert stages["parser"] is True
    assert stages["assembler"] is True
    assert stages["codegen"] is False, "codegen is a stub; do not advertise it"
