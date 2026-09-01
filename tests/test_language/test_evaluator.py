"""Tests for the HC evaluator."""
from hijaiyyah.language.evaluator import HCEvaluator
from hijaiyyah.language.lexer import Lexer
from hijaiyyah.language.parser import Parser


def _eval(src):
    tokens = Lexer(src).tokenize()
    ast = Parser(tokens).parse()
    output = []
    ev = HCEvaluator(print_func=lambda *a: output.append(" ".join(str(x) for x in a)))
    ev.evaluate(ast)
    return output

def test_println():
    out = _eval('println("hello");')
    assert out == ["hello"]

def test_let_and_print():
    out = _eval('let x = 42; println(x);')
    assert "42" in out[0]

def test_load_letter():
    out = _eval("let h = 'ب'; println(h.theta());")
    assert "2" in out[0]

def test_guard():
    out = _eval("let h = 'ب'; println(h.guard());")
    assert "True" in out[0]

def test_norm2():
    out = _eval("let h = 'ا'; println(h.norm2());")
    assert "1" in out[0]

def test_module_call():
    out = _eval('let d = hm::geometry::diameter_sq(); println(d);')
    assert "70" in out[0]

def test_string_integral():
    out = _eval('let c = hm::integral::string_integral("بسم"); println(c);')
    assert len(out) == 1

def test_arithmetic():
    out = _eval("println(2 + 3 * 4);")
    assert "14" in out[0]

def test_comparison():
    out = _eval("println(1 < 2);")
    assert "True" in out[0]
