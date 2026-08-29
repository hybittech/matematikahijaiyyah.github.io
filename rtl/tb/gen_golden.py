"""Generate HISAB golden values for RTL testbench cross-validation."""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Imports follow the sys.path bootstrap above, so E402 is expected here.
from src.hijaiyyah.core.master_table import MasterTable  # noqa: E402
from src.hijaiyyah.hisab.serialize import (  # noqa: E402
    _compute_guard_status,
    _nibble_pack,
    serialize_letter,
)

mt = MasterTable()
entries = mt.all_entries()  # 28 entries in ROM order

print("=== HISAB Golden Values for RTL Cross-Validation ===\n")
print(f"Total letters: {len(entries)}\n")

for idx, entry in enumerate(entries):
    v = list(entry.vector)
    nb = _nibble_pack(v)
    gs = _compute_guard_status(v)
    frame = serialize_letter(v)
    
    pw0 = int.from_bytes(nb[0:4], 'little')
    pw1 = int.from_bytes(nb[4:8], 'little')
    pw2 = (gs << 8) | nb[8]
    crc = frame.digest
    
    print(f"ROM[{idx+1:2d}] {entry.name:6s}: v18={v}")
    print(f"  pack_word0=0x{pw0:08X}  pack_word1=0x{pw1:08X}  pack_word2=0x{pw2:08X}")
    print(f"  guard_status=0x{gs:02X}  CRC32=0x{crc:08X}")
    
    if entry.name == 'Ba':
        print("\n  // === Verilog golden constants for Ba ===")
        print(f"  localparam BA_PACK0 = 32'h{pw0:08X};")
        print(f"  localparam BA_PACK1 = 32'h{pw1:08X};")
        print(f"  localparam BA_PACK2 = 32'h{pw2:08X};")
        print(f"  localparam BA_CRC32 = 32'h{crc:08X};")
    
    if entry.name == 'Alif':
        print("\n  // === Verilog golden constants for Alif ===")
        print(f"  localparam ALIF_PACK0 = 32'h{pw0:08X};")
        print(f"  localparam ALIF_PACK1 = 32'h{pw1:08X};")
        print(f"  localparam ALIF_PACK2 = 32'h{pw2:08X};")
        print(f"  localparam ALIF_CRC32 = 32'h{crc:08X};")
    
    if entry.name == 'Ya':
        print("\n  // === Verilog golden constants for Ya ===")
        print(f"  localparam YA_PACK0 = 32'h{pw0:08X};")
        print(f"  localparam YA_PACK1 = 32'h{pw1:08X};")
        print(f"  localparam YA_PACK2 = 32'h{pw2:08X};")
        print(f"  localparam YA_CRC32 = 32'h{crc:08X};")
    print()
