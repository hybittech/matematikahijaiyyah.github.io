"""
Every function the HC grammar advertises must actually be callable.

grammar.STDLIB_MODULES is the language's documented surface — it is what the
editor completes, what the docs list, and what a reader assumes exists. It had
drifted badly: 27 of the 55 entries had no implementation, so more than half of
hm::geometry raised "Module member not found" when called. Ten of the thirteen
geometry functions were unreachable.

The evaluator now forwards to hijaiyyah.algebra instead of carrying its own copy
of the maths, which is also what removed the third parallel implementation of
the codex algebra — the Python packages, the JavaScript engine, and the HC
evaluator had each held their own.
"""

from __future__ import annotations

from importlib import import_module
from typing import List

import pytest

from hijaiyyah.language.evaluator import HCEvaluator
from hijaiyyah.language.grammar import STDLIB_MODULES
from hijaiyyah.language.lexer import Lexer
from hijaiyyah.language.parser import Parser


def _names(module: str) -> List[str]:
    declared = STDLIB_MODULES[module]
    return list(declared)  # a dict yields its keys, a list its items


ENTRIES = [(mod, fn) for mod in STDLIB_MODULES for fn in _names(mod)]
IDS = [f"{mod}::{fn}" for mod, fn in ENTRIES]


def test_the_declared_surface_is_not_empty() -> None:
    """A stdlib table that parsed as empty would make every test below vacuous."""
    assert len(ENTRIES) >= 50, f"only {len(ENTRIES)} stdlib entries found"
    assert len(STDLIB_MODULES) == 5


@pytest.mark.parametrize(("module", "func"), ENTRIES, ids=IDS)
def test_declared_function_resolves(module: str, func: str) -> None:
    """Reaching the name from HC source must not raise 'not found'."""
    source = f"let _x = {module}::{func};"
    ast = Parser(Lexer(source).tokenize()).parse()
    HCEvaluator(print_func=lambda *a: None).evaluate(ast)


@pytest.mark.parametrize(("module", "func"), ENTRIES, ids=IDS)
def test_declared_function_is_callable(module: str, func: str) -> None:
    evaluator = HCEvaluator(print_func=lambda *a: None)
    table = evaluator.globals.get("hm")
    assert isinstance(table, dict), "hm namespace missing"

    short = module.split("::", 1)[1]
    assert short in table, f"{module} is not registered"
    assert callable(table[short][func]), f"{module}::{func} is not callable"


def test_evaluator_forwards_to_the_algebra_packages() -> None:
    """
    Delegation, not a copy. If a function here stopped being the one in
    hijaiyyah.algebra, the two could drift apart again silently.
    """
    evaluator = HCEvaluator(print_func=lambda *a: None)
    table = evaluator.globals.get("hm")

    for short, dotted in HCEvaluator._STDLIB_SOURCES.items():
        package = import_module(dotted)
        for name, fn in table[short].items():
            assert fn is getattr(package, name), (
                f"hm::{short}::{name} is not {dotted}.{name} — "
                "the evaluator has its own copy again"
            )


def test_a_missing_implementation_fails_at_construction() -> None:
    """
    The gap used to surface only when a program called the function. Building
    the evaluator must reject an advertised name with nothing behind it.
    """
    from hijaiyyah.core.exceptions import EBNFSemanticError

    original = dict(STDLIB_MODULES)
    geometry = _names("hm::geometry")
    try:
        STDLIB_MODULES["hm::geometry"] = [*geometry, "fungsi_yang_tidak_ada"]
        with pytest.raises(EBNFSemanticError, match="fungsi_yang_tidak_ada"):
            HCEvaluator(print_func=lambda *a: None)
    finally:
        STDLIB_MODULES.clear()
        STDLIB_MODULES.update(original)

    # And the real table still builds cleanly afterwards.
    HCEvaluator(print_func=lambda *a: None)
