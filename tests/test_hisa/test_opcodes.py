from hijaiyyah.hisa.opcodes import InstructionWord, OpCode


def test_decode():
    raw = (OpCode.CLOAD << 24) | (1 << 20) | 5
    iw = InstructionWord(raw)
    assert iw.opcode == OpCode.CLOAD and iw.dst == 1 and iw.imm == 5
def test_disassemble():
    raw = (OpCode.HALT << 24)
    assert "HALT" in InstructionWord(raw).disassemble()
