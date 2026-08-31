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


# ── Keywords as member names ─────────────────────────────────────
# A stdlib function whose name collides with a keyword used to be
# unreachable: 'audit' lexes as KW_AUDIT, so hm::exomatrix::audit could not
# be parsed at all and examples/five_fields_demo.hc did not run. After '::'
# or '.', a keyword cannot begin a new construct, so it is read as a name.

def test_keyword_is_accepted_after_double_colon():
    ast = Parser(Lexer("hm::exomatrix::audit(E);").tokenize()).parse()
    assert ast is not None


def test_keyword_is_accepted_after_dot():
    ast = Parser(Lexer("let x = h.audit();").tokenize()).parse()
    assert ast is not None


def test_every_keyword_survives_as_a_member_name():
    from hijaiyyah.language.tokens import KEYWORDS

    for kw in KEYWORDS:
        Parser(Lexer(f"hm::mod::{kw}(x);").tokenize()).parse()
        Parser(Lexer(f"obj.{kw}();").tokenize()).parse()


def test_keyword_still_keyword_in_statement_position():
    """The fix must not let a keyword be used as a bare variable name."""
    import pytest

    from hijaiyyah.language.parser import ParseError

    with pytest.raises(ParseError):
        Parser(Lexer("let audit = 1;").tokenize()).parse()
