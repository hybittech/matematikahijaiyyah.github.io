from hijaiyyah.core.master_table import MASTER_TABLE
from hijaiyyah.hisa.machine import HISAMachine
from hijaiyyah.hisa.opcodes import OpCode


def test_cload():
    """IMM is the 1-based letter index, so #1 is Alif — as on the HCPU ROM."""
    m = HISAMachine(MASTER_TABLE)
    raw = (OpCode.CLOAD << 24) | (0 << 20) | 1  # HLOAD H0, #1 → Alif
    m.load_program([raw])
    m.step()
    alif = MASTER_TABLE.get_by_index(1)
    assert alif is not None and alif.char == "ا"
    assert m.regs.hreg[0] == list(alif.vector)


def test_cload_index_is_one_based_like_the_rom():
    """
    HLOAD H0, #2 loads Ba on the HCPU (rtl/hcpu_rom.v index 2). Indexing the
    entry list directly with IMM used to give Ta here instead.
    """
    m = HISAMachine(MASTER_TABLE)
    m.load_program([(OpCode.HLOAD << 24) | (0 << 20) | 2])
    m.step()
    ba = MASTER_TABLE.get_by_index(2)
    assert ba is not None and ba.char == "ب"
    assert m.regs.hreg[0] == list(ba.vector)


def test_cload_rejects_index_zero():
    """The ROM reports valid = 0 for address 0; nothing should be loaded."""
    m = HISAMachine(MASTER_TABLE)
    m.load_program([(OpCode.HLOAD << 24) | (0 << 20) | 0])
    m.step()
    assert m.regs.hreg[0] == [0] * 18
