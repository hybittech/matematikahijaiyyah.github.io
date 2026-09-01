"""Tests for the HC lexer."""
from hijaiyyah.language.lexer import Lexer, TokenType


def test_integer():
    tokens = Lexer("42").tokenize()
    assert tokens[0].type == TokenType.INTEGER and tokens[0].value == "42"

def test_float():
    tokens = Lexer("3.14").tokenize()
    assert tokens[0].type == TokenType.FLOAT and tokens[0].value == "3.14"

def test_hijaiyyah_quoted():
    tokens = Lexer("'ب'").tokenize()
    assert tokens[0].type == TokenType.HIJAIYYAH and tokens[0].value == "ب"

def test_string():
    tokens = Lexer('"hello"').tokenize()
    assert tokens[0].type == TokenType.STRING_LIT and tokens[0].value == "hello"

def test_keywords():
    tokens = Lexer("let mut fn if else for in while return break continue").tokenize()
    kw_types = [t.type for t in tokens if t.type != TokenType.NEWLINE and t.type != TokenType.EOF]
    assert TokenType.KW_LET in kw_types
    assert TokenType.KW_BREAK in kw_types
    assert TokenType.KW_CONTINUE in kw_types

def test_operators():
    tokens = Lexer("&& || == != <= >=").tokenize()
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    assert TokenType.AMP_AMP in types
    assert TokenType.PIPE_PIPE in types

def test_comment_skipped():
    tokens = Lexer("42 // this is a comment\n43").tokenize()
    ints = [t for t in tokens if t.type == TokenType.INTEGER]
    assert len(ints) == 2

def test_escape_in_string():
    tokens = Lexer(r'"hello\nworld"').tokenize()
    assert tokens[0].value == "hello\nworld"

def test_haa():
    tokens = Lexer("'هـ'").tokenize()
    assert tokens[0].type == TokenType.HIJAIYYAH and tokens[0].value == "هـ"
