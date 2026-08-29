from hijaiyyah.integrity.seal import compute_seal, verify_seal


def test_seal_stable():
    s1 = compute_seal()
    s2 = compute_seal()
    assert s1 == s2


def test_verify_correct():
    assert verify_seal(compute_seal())


def test_verify_wrong():
    assert not verify_seal("wrong")
