from hijaiyyah.core.master_table import MASTER_TABLE


def test_vector_length():
    for e in MASTER_TABLE.all_entries():
        assert len(e.vector) == 18


def test_all_non_negative():
    for e in MASTER_TABLE.all_entries():
        assert all(v >= 0 for v in e.vector)


def test_properties():
    ba = MASTER_TABLE.get_by_char("ب")
    assert ba.theta_hat == 2
    assert ba.nd == 1
