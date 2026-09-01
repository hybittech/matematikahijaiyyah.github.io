from hijaiyyah.core.exomatrix import build_exomatrix
from hijaiyyah.core.master_table import MASTER_TABLE


def test_5x5():
    for e in MASTER_TABLE.all_entries():
        E = build_exomatrix(e)
        assert len(E) == 5
        assert all(len(r) == 5 for r in E)
