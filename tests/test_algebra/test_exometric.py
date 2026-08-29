from hijaiyyah.algebra.exometric import audit, build, phi, reconstruct
from hijaiyyah.algebra.vektronometry import norm2
from hijaiyyah.core.master_table import MASTER_TABLE


def test_audit_all():
    for e in MASTER_TABLE.all_entries():
        assert audit(build(e))["all_pass"]


def test_phi_gt_norm():
    for e in MASTER_TABLE.all_entries():
        assert phi(build(e)) > norm2(e)


def test_reconstruct():
    for e in MASTER_TABLE.all_entries():
        assert reconstruct(build(e)) == list(e.vector)
