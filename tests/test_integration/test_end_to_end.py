from hijaiyyah.algebra.aggregametric import string_integral
from hijaiyyah.core.guards import guard_check
from hijaiyyah.core.master_table import MASTER_TABLE
from hijaiyyah.core.rom import pack_rom, unpack_rom
from hijaiyyah.integrity.injectivity import InjectivityVerifier


def test_full_stack():
    assert len(MASTER_TABLE.all_entries()) == 28
    assert all(guard_check(e) for e in MASTER_TABLE.all_entries())
    assert InjectivityVerifier().verify()
    vecs = [list(e.vector) for e in MASTER_TABLE.all_entries()]
    rom = pack_rom(vecs)
    assert len(rom) == 252
    restored = unpack_rom(rom)
    assert restored == vecs
    cod = string_integral("بسم الله")
    assert cod["cod18"][0] == 12
