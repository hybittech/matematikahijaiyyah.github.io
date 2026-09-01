from hijaiyyah.algebra.normivektor import all_dot_variants, diff, u_gradient
from hijaiyyah.core.master_table import MASTER_TABLE


def test_self_diff_zero():
    ba = MASTER_TABLE.get_by_char("ب")
    assert all(x == 0 for x in diff(ba, ba))


def test_u_gradient():
    assert u_gradient() == [0, 1, 1, 1, 4]


def test_dot_variants_theta_equal():
    for c1, c2, _g in all_dot_variants():
        e1, e2 = MASTER_TABLE.get_by_char(c1), MASTER_TABLE.get_by_char(c2)
        assert e1.theta_hat == e2.theta_hat
