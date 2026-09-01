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

# A guarded block, up to the matching `except ImportError`. Captured whole so
# that every `from ... import ...` inside it is examined — the first version of
# this scan matched a single line and so walked straight past
#
#     try:
#         from a.b import (
#             C as _C,
#         )
#         from a.b import (
#             D as _D,
#         )
#     except ImportError:
#
# which is exactly the shape two live failures were hiding in.
_GUARDED_BLOCK = re.compile(r"try:\n(.*?)\n\s*except ImportError", re.S)
_FROM_IMPORT = re.compile(r"from ([\w.]+) import\s*\(?\s*([\w,\s]+?)\)?\s*$", re.M)


def _absolute(module: str, path: Path) -> str:
    """Resolve a relative import against the package the file sits in."""
    if not module.startswith("."):
        return module
    depth = len(module) - len(module.lstrip("."))
    package = path.relative_to(SRC).with_suffix("").parts
    if path.name == "__init__.py":
        package = package[:-1]
    anchor = package[: len(package) - depth]
    return ".".join([*anchor, module.lstrip(".")]).rstrip(".")


def _guarded_imports() -> List[Tuple[str, str, str]]:
    """
    First-party guarded imports only.

    A try/except around an optional third-party dependency — PIL, scipy — is
    the construct working as intended: the feature degrades when the package
    is absent. A guard around one of this project's own modules is different,
    because that module either exists or was never written.
    """
    found: List[Tuple[str, str, str]] = []
    for path in sorted(SRC.rglob("*.py")):
        rel = str(path.relative_to(ROOT))
        for block in _GUARDED_BLOCK.finditer(path.read_text(encoding="utf-8")):
            for imp in _FROM_IMPORT.finditer(block.group(1)):
                module = _absolute(imp.group(1), path)
                if not module.startswith("hijaiyyah"):
                    continue
                for piece in imp.group(2).split(","):
                    name = piece.strip().split(" as ")[0].strip()
                    if name:
                        found.append((rel, module, name))
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
