from hijaiyyah.algebra.aggregametric import add_codex, string_integral


def test_additivity():
    bs = string_integral("بس")
    m = string_integral("م")
    bsm = string_integral("بسم")
    assert add_codex(bs, m)["cod18"] == bsm["cod18"]


def test_anagram():
    assert string_integral("بسم")["cod18"] == string_integral("سبم")["cod18"]
