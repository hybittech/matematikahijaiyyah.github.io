from hijaiyyah.core.master_table import MASTER_TABLE


def test_28_letters():
    assert len(MASTER_TABLE.all_entries()) == 28


def test_sha256_stable():
    s1 = MASTER_TABLE.compute_sha256()
    s2 = MASTER_TABLE.compute_sha256()
    assert s1 == s2


def test_lookup_ba():
    e = MASTER_TABLE.get_by_char("ب")
    assert e is not None
    assert e.name == "Ba"
