from hijaiyyah.algebra.intrametric import diameter_sq, polarization_check
from hijaiyyah.core.master_table import MASTER_TABLE


def test_diameter(): assert diameter_sq()==70
def test_polarization():
    es = MASTER_TABLE.all_entries()
    assert polarization_check(es[0],es[1])["pass"]
