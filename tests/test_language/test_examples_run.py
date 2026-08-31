"""
Every .hc file in the repository must lex, parse, and evaluate.

examples/five_fields_demo.py — the one example that exercises all five
analytical fields — had been broken for as long as `audit` was a keyword,
and nothing noticed, because no test ever executed an example. The five
files under docs/examples/ were worse: 0 bytes each.

This module is the guard against both. It discovers .hc files rather than
listing them, so a new example is covered the moment it is added.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import pytest

from hijaiyyah.language.evaluator import HCEvaluator
from hijaiyyah.language.lexer import Lexer
from hijaiyyah.language.parser import Parser

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_DIRS = ("examples", "docs/examples")


def _discover() -> List[Path]:
    found: List[Path] = []
    for d in EXAMPLE_DIRS:
        found.extend(sorted((ROOT / d).glob("*.hc")))
    return found


HC_FILES = _discover()
HC_IDS = [str(p.relative_to(ROOT)) for p in HC_FILES]


def test_examples_were_actually_found() -> None:
    """A glob that silently matches nothing would make every test below vacuous."""
    assert len(HC_FILES) >= 10, f"expected at least 10 .hc files, found {len(HC_FILES)}"


@pytest.mark.parametrize("path", HC_FILES, ids=HC_IDS)
def test_example_is_not_empty(path: Path) -> None:
    """The docs/examples/ files shipped as 0-byte placeholders for a long time."""
    assert path.stat().st_size > 0, f"{path.name} is empty"


@pytest.mark.parametrize("path", HC_FILES, ids=HC_IDS)
def test_example_runs(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    output: List[str] = []

    ast = Parser(Lexer(source).tokenize()).parse()
    HCEvaluator(
        print_func=lambda *a: output.append(" ".join(str(x) for x in a))
    ).evaluate(ast)

    assert output, f"{path.name} ran but printed nothing — is it doing anything?"
