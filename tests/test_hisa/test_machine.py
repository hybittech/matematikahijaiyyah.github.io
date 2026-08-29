from hijaiyyah.core.master_table import MASTER_TABLE
from hijaiyyah.hisa.machine import HISAMachine
from hijaiyyah.hisa.opcodes import OpCode


def test_cload():
    m = HISAMachine(MASTER_TABLE)
    raw = (OpCode.CLOAD << 24) | (0 << 20) | 1  # load letter[1] into H0
    m.load_program([raw])
    m.step()
    assert m.regs.hreg[0] == list(MASTER_TABLE.all_entries()[1].vector)
