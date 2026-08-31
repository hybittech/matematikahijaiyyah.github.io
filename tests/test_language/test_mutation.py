"""
Assignment, mutability, and constructs that span lines.

Three gaps found by writing the documentation examples in docs/examples/, all
of which made ordinary programs impossible to express:

  - There was no assignment statement, so `x = 2` was a parse error and a loop
    could not carry a running total. The grammar had carried the production
    (assignment = identifier , '=' , expression) all along; only the parser
    was missing it, and `mut` was lexed and then discarded.
  - A newline inside brackets ended the expression, so an argument list could
    not span lines however long it ran.
  - Array literals parsed but had no evaluator, so `[1, 2, 3]` raised
    "No evaluator for AST node" the moment it was reached.

Mutability follows docs/hc_language.md §5.1: `let` binds immutably, `let mut`
is the mutable form, `const` is neither.
"""

from __future__ import annotations

import pytest

from hijaiyyah.core.exceptions import EBNFSemanticError
from hijaiyyah.language.evaluator import HCEvaluator
from hijaiyyah.language.lexer import Lexer
from hijaiyyah.language.parser import Parser


def run(source: str) -> list[str]:
    output: list[str] = []
    HCEvaluator(
        print_func=lambda *a: output.append(" ".join(str(x) for x in a))
    ).evaluate(Parser(Lexer(source).tokenize()).parse())
    return output


# ── Assignment ───────────────────────────────────────────────────

def test_mutable_binding_can_be_reassigned() -> None:
    assert run("let mut x = 1; x = 2; println(x);") == ["2"]


def test_immutable_binding_cannot_be_reassigned() -> None:
    with pytest.raises(EBNFSemanticError, match="immutable binding 'x'"):
        run("let x = 1; x = 2;")


def test_the_error_names_the_fix() -> None:
    """A diagnostic that only says 'no' costs the reader a search."""
    with pytest.raises(EBNFSemanticError, match=r"let mut x"):
        run("let x = 1; x = 2;")


def test_constant_cannot_be_reassigned() -> None:
    with pytest.raises(EBNFSemanticError, match="constant 'C'"):
        run("const C = 1; C = 2;")


def test_constant_error_does_not_suggest_let_mut_on_the_name() -> None:
    """`let mut C` is not the fix for a const; the message must not imply it."""
    with pytest.raises(EBNFSemanticError) as excinfo:
        run("const C = 1; C = 2;")
    assert "let mut C" not in str(excinfo.value)


def test_assignment_to_an_undeclared_name_is_rejected() -> None:
    with pytest.raises(EBNFSemanticError, match="undefined variable"):
        run("y = 1;")


def test_assignment_reaches_an_outer_scope() -> None:
    """
    A block introduces a scope, so the assignment has to walk outward to find
    the binding. HC has no bare block statement — blocks appear only after
    `if`, `for`, `while` and `fn` — so this goes through an `if`.
    """
    assert run("let mut n = 0; if true { n = 5; } println(n);") == ["5"]


# ── Accumulation, the reason assignment matters ──────────────────

def test_for_loop_can_carry_a_running_total() -> None:
    assert run("let mut t = 0; for i in 0..5 { t = t + i; } println(t);") == ["10"]


def test_while_loop_can_advance_its_own_counter() -> None:
    assert run("let mut n = 0; while n < 3 { n = n + 1; } println(n);") == ["3"]


def test_counting_letters_that_pass_a_guard() -> None:
    """The shape docs/examples/iot_guard.hc had to avoid writing."""
    source = """
    let mut passed = 0;
    for i in 1..=28 {
        let h = load_id(i);
        if h.guard() { passed = passed + 1; }
    }
    println(passed);
    """
    assert run(source) == ["28"]


# ── Line breaks inside brackets ──────────────────────────────────

def test_argument_list_spans_lines() -> None:
    assert run('println("a",\n        "b",\n        "c");') == ["a b c"]


def test_method_arguments_span_lines() -> None:
    assert run("let h = 'ج';\nprintln(h.theta(),\n        h.norm2());") == ["3 12"]


def test_parenthesised_expression_spans_lines() -> None:
    assert run("let x = (\n  1 + 2\n);\nprintln(x);") == ["3"]


def test_array_literal_spans_lines_with_a_trailing_comma() -> None:
    assert run("let a = [\n  10,\n  20,\n  30,\n];\nprintln(len(a), a[1]);") == ["3 20"]


def test_single_line_calls_still_parse() -> None:
    """The newline skipping must not change anything that already worked."""
    assert run("println(1, 2);") == ["1 2"]


# ── Array literals ───────────────────────────────────────────────

def test_array_literal_evaluates() -> None:
    assert run("let a = [1, 2, 3]; println(len(a), a[0], a[2]);") == ["3 1 3"]


def test_empty_array_literal() -> None:
    assert run("let a = []; println(len(a));") == ["0"]


def test_array_elements_are_evaluated_not_stored_raw() -> None:
    assert run("let a = [1 + 1, 2 * 3]; println(a[0], a[1]);") == ["2 6"]
