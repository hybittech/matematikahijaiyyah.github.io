from hijaiyyah.hisa.compiler import HL18ECompiler


def test_placeholder():
    c = HL18ECompiler()
    assert c.compile("") == []
