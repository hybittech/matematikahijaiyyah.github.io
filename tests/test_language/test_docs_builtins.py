"""
docs/hc_language.md §13, against the built-ins that actually exist.

The section had drifted in both directions. It listed `load14`, `zero14` and
`hybit`, none of which were ever implemented — calling one raised "Undefined
variable". And it omitted `len`, `abs` and `sqrt`, which do exist. A reference
that names functions you cannot call, and hides ones you can, is worse than no
reference.

Only §13 is checked. The standard library has its own tables in §12, and
test_stdlib_complete.py already holds those to the implementation.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Set

import pytest

from hijaiyyah.language.grammar import BUILTIN_FUNCTIONS

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "hc_language.md"

BUILTINS: Set[str] = set(BUILTIN_FUNCTIONS)


def _section_13() -> str:
    text = DOC.read_text(encoding="utf-8")
    start = text.index("## 13. Built-in Functions")
    end = text.index("## 14.", start)
    return text[start:end]


def _documented() -> Set[str]:
    """Names appearing as `name(` in a table row of §13."""
    return {m.group(1) for m in re.finditer(r"^\|\s*`([a-z_0-9]+)\(", _section_13(), re.M)}


def test_section_13_was_located() -> None:
    section = _section_13()
    assert "Built-in Functions" in section
    assert len(_documented()) >= 10, "the table format probably changed"


@pytest.mark.parametrize("name", sorted(BUILTINS), ids=sorted(BUILTINS))
def test_every_builtin_is_documented(name: str) -> None:
    assert name in _documented(), (
        f"`{name}` is callable but §13 does not list it"
    )


def test_no_documented_builtin_is_imaginary() -> None:
    """
    The failure that prompted this test: three names in the table had no
    implementation behind them at all.
    """
    imaginary = sorted(_documented() - BUILTINS)
    assert not imaginary, (
        f"§13 lists {imaginary}, which cannot be called — "
        "remove them or implement them"
    )
