"""Tests for the HC parser."""
from hijaiyyah.language.ast_nodes import LetStmt, Literal
from hijaiyyah.language.lexer import Lexer
from hijaiyyah.language.parser import Parser


def _parse(src):
    return Parser(Lexer(src).tokenize()).parse()

def test_let_stmt():
    p = _parse("let x = 42;")
    assert len(p.body) == 1
    assert isinstance(p.body[0], LetStmt)
    assert p.body[0].name == "x"

def test_arithmetic():
    p = _parse("1 + 2 * 3;")
    assert len(p.body) == 1

def test_function_call():
    p = _parse("println(42);")
    assert len(p.body) == 1

def test_module_call():
    p = _parse('hm::geometry::diameter();')
    assert len(p.body) == 1

def test_method_call():
    p = _parse("h.guard();")
    assert len(p.body) == 1

def test_if_else():
    p = _parse("if true { 1; } else { 2; }")
    assert len(p.body) == 1

def test_for_loop():
    p = _parse("for i in 0..10 { println(i); }")
    assert len(p.body) == 1

def test_match():
    p = _parse("match x { 0 => 1, _ => 2, }")
    assert len(p.body) == 1

def test_hijaiyyah_literal():
    p = _parse("let h = 'ب';")
    stmt = p.body[0]
    assert isinstance(stmt, LetStmt)
    assert isinstance(stmt.value, Literal)
    assert stmt.value.lit_type == "hybit_ref"
