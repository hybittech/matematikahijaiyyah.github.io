# HCPU RTL Architecture Specification — Phase 2.0
## Hijaiyyah Core Processing Unit • Hybit Silicon Implementation

> **Identifier**: HCPU-SPEC-2.3.0
> **Date**: 2026-04-10
> **Author**: HMCL Engineering — Hybit Technology
> **Release Tag**: HM-28-v1.2-HC18D
> **Status**: RTL Architecture Spec — RTL Hardened, Synthesis-Ready
> **Validation**: 7 programs, 10 assertions, 0 FAIL
> **FPGA Target (Full)**: Digilent Arty A7-35T (XC7A35T-1CPG236C)
> **FPGA Target (Reduced)**: Lattice iCE40UP5K *(§10.2)*
> **MPW Target**: Efabless Open MPW — SkyWater SKY130 *(§11)*

---

## Table of Contents

1. [System Context & Hybit Mapping](#1-system-context--hybit-mapping)
2. [Architecture Overview](#2-architecture-overview)
3. [Register File](#3-register-file)
4. [Pipeline Stages](#4-pipeline-stages)
5. [Hazard Resolution](#5-hazard-resolution)
6. [Codex Subsystem](#6-codex-subsystem)
7. [Memory Subsystem](#7-memory-subsystem)
8. [I/O: UART Transmitter](#8-io-uart-transmitter)
9. [H-ISA Opcode Reference](#9-h-isa-opcode-reference)
10. [FPGA Implementation](#10-fpga-implementation)
11. [MPW / ASIC Readiness](#11-mpw--asic-readiness)
12. [Assembler Toolchain](#12-assembler-toolchain)
13. [RTL Source Inventory](#13-rtl-source-inventory)
14. [Verification Status](#14-verification-status)
15. [Industry Readiness Checklist](#15-industry-readiness-checklist)
16. [Known Limitations](#16-known-limitations)
17. [Errata](#17-errata)

---

## 1. System Context & Hybit Mapping

HCPU is the **hardware realization** of the Hybit computational stack. Every RTL module maps directly to an existing layer of the Hybit architecture defined in the project's `README.md` and `docs/architecture.md`.

### 1.1 Hybit ↔ Hardware Mapping

| Hybit Layer | Software Component | Hardware Module (RTL) | Status |
|---|---|---|---|
| **Dataset Seal** | `data/hm28.json` (252 bytes) | [hcpu_rom.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_rom.v) — 28×144-bit combinational ROM | ✅ Implemented |
| **Guard System** | `core/guards` — G1–G4, T1–T2 | [hcpu_guard.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_guard.v) — single-cycle combinational checker | ✅ Implemented |
| **H-ISA** | `hisa/` — 44 opcodes | [hcpu_pkg.vh](file:///c:/hijaiyyah-mathematics/rtl/hcpu_pkg.vh) — Phase 2.0 subset (28 opcodes) | ✅ Implemented |
| **HVM Registers** | `vm/HVM` — R0–R15 (18D each) | [hcpu_regfile.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_regfile.v) — 18 GPR (32-bit) + 16 H-Reg (144-bit) | ✅ Implemented |
| **HVM Interpreter** | `vm/HVM.execute()` | 5-stage pipeline: Fetch → Decode → Execute → Memory → Writeback | ✅ Implemented |
| **Hybit Engine** | `vm/HybitEngine` — HCADD, HNRM2, HDIST | [hcpu_codex_alu.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_codex_alu.v) — 18-wide parallel vector ALU | ✅ Implemented |
| **AGM (Aggregametric)** | `algebra/aggregametric.py` | `HCADD` instruction — component-wise 18×8-bit add | ✅ Implemented |
| **ITM (Intrametric)** | `algebra/intrametric.py` | `HDIST` instruction — squared Euclidean distance (14-component) | ✅ Implemented |
| **VTM (Vektronometry)** | `algebra/vektronometry.py` | `HNRM2` instruction — squared norm (14-component) | ✅ Implemented |
| **EXM (Exometric)** | `algebra/exometric.py` | `HGRD` instruction → FLAG_G | ✅ Implemented |
| **HCHECK** | `vm/HCheck` | Hardware runtime invariant checker: HC-00 (invalid opcode), HC-01 (invalid ROM index), HC-02 (stack overflow), HC-03 (stack underflow) → `HALT_ERR` | ✅ Implemented |
| **HISAB** | `hisab/` | [hcpu_hisab.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_hisab.v) — nibble-packer + CRC32 engine (`HPACK`, `HCRC`) | ✅ Operational |

### 1.2 Verification Traceability (1.380-Check Framework)

The RTL test suite maps to the project's formal verification framework:

| Bab | Software Tests | RTL Testbench Coverage |
|---|---|---|
| **Bab I** — 658 checks | G1–G4 ×28, T1–T2 ×28, Injectivity ×378 | `tb_hcpu_top` P1 (Ba guard), P5 (negative guard), `tb_guard` |
| **Bab II** — 683 checks | VTM, NMV, AGM, ITM, EXM | `tb_hcpu_top` P2 (BSM AGM integral), `tb_codex_alu` (HNRM2/HDIST) |
| **Bab III** — 39 checks | Closure, Identity, Pipeline | `tb_hcpu_top` P2 (closure on HCADD), P3 (loop/branch) |

---

## 2. Architecture Overview

HCPU is a **5-stage in-order pipelined processor** implementing the H-ISA (Hijaiyyah Instruction Set Architecture). It uses a **Harvard architecture** with separate instruction and data memory buses.

### 2.1 Key Parameters

| Parameter | Value | Source |
|---|---|---|
| Data word width (`XLEN`) | 32 bits | `hcpu_pkg.vh` |
| Instruction width (`ILEN`) | 32 bits, fixed-length | `hcpu_pkg.vh` |
| H-Reg vector width (`HREG_W`) | 144 bits (18 × 8-bit unsigned components) | `hcpu_pkg.vh` |
| Immediate field width | 12 bits (signed or unsigned per opcode) | `hcpu_pkg.vh` |
| System clock | 50 MHz (from 100 MHz via MMCM on Arty A7) | `hcpu_xilinx_top.v` |
| UART baud rate | 115200 (8N1) | `hcpu_pkg.vh` |
| Code memory | 4096 × 32-bit words | `hcpu_pkg.vh` |
| Data memory | 4096 × 32-bit words (16 KB, word-addressed) | `hcpu_pkg.vh` |
| Stack depth | 256 entries × 32 bits | `hcpu_pkg.vh` |

### 2.2 Block Diagram

```
                    ┌──────────────────────────────────────────────────────┐
                    │                    HCPU Top-Level                     │
  ┌──────────┐     │  ┌───────┐  ┌───────┐  ┌─────────┐  ┌───────┐       │
  │   Code   │◄────┤  │ FETCH │─►│DECODE │─►│ EXECUTE │─►│MEMORY │──►WB  │
  │   ROM    │     │  └───┬───┘  └───┬───┘  └────┬────┘  └───┬───┘       │
  └──────────┘     │      │          │    ┌──────┤            │            │
                    │      │    ┌─────┴──┐│┌─────┴────┐ ┌─────┴─────┐     │
                    │      │    │RegFile ││├ ScalarALU │ │  DataRAM  │     │
                    │      │    │18 GPR  │││  (32-bit) │ │  (16 KB)  │     │
                    │      │    │16 H-Reg│││  MOV/ADD/ │ │  LOAD/    │     │
                    │      │    │ FLAGS  │││  SUB/MUL/ │ │  STORE    │     │
                    │      │    └────────┘││  CMP      │ ├───────────┤     │
                    │      │             ││├──────────┤ │  Stack    │     │
                    │      │             │││ CodexALU │ │  (256×32) │     │
                    │ ┌────┴────┐        │││ HCADD    │ │  PUSH/POP │     │
                    │ │  Ctrl   │        │││ HNRM2    │ └───────────┘     │
                    │ │ pc_stall│        │││ HDIST    │                    │
                    │ │ id_flush│        ││├──────────┤  ┌──────────────┐ │
                    │ │ if_flush│        │││  Guard   │  │  UART TX     │ │
                    │ │ ex_stall│        │││ G1–G4    │  │  8N1 115200  │─┼──► TXD
                    │ └────┬────┘        │││ T1–T2    │  └──────────────┘ │
                    │      │       ┌─────┤│└──────────┘                    │
                    │      │       │ FWD ││ ┌──────────┐                   │
                    │      └───────┤EX→ID││ │Master ROM│                   │
                    │              │MEM→ID│└─┤28×144-bit│                   │
                    │              └──────┘  └──────────┘                   │
                    └──────────────────────────────────────────────────────┘
```

---

## 3. Register File (`hcpu_regfile.v`)

### 3.1 GPR Bank — Scalar Computation

| Property | Value |
|---|---|
| Count | 18 registers (`R0`–`R17`) |
| Width | 32 bits each |
| Read ports | 2 pipeline (combinational, with write-through) + 1 debug (read-only) |
| Write port | 1 (synchronous, rising edge) |
| Debug port | `dbg_gpr_raddr` / `dbg_gpr_rdata` — synthesis-safe Wishbone/MPW read-back |
| R0 | General-purpose (not hardwired to zero) |
| R17 | Link register (by convention) |
| Addressing | 5-bit (4-bit from instruction field, zero-extended) |
| Reset value | All zeros (`32'h0`) |

### 3.2 H-Reg Bank — Hybit / Codex Operations

| Property | Value |
|---|---|
| Count | 16 registers (`H0`–`H15`) |
| Width | 144 bits each (18 components × 8 bits unsigned) |
| Read ports | 2 (combinational, with write-through) |
| Write port | 1 (synchronous, rising edge) |
| Addressing | 4-bit |
| Reset value | All zeros (`144'h0`) |

**Component layout** (LSB-first, `component[i]` = `hreg[8*i +: 8]`):

| Index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Name | Θ̂ | Na | Nb | Nd | Kp | Kx | Ks | Ka | Kc | Qp | Qx | Qs | Qa | Qc | A_N | A_K | A_Q | Ψ |
| Group | Turn | Nuqṭah×3 | — | Khaṭṭ×5 | — | — | — | — | Qaws×5 | — | — | — | — | Aggregates×3 | — | — | Chi |

### 3.3 Special Registers

| Register | Width | Reset | Location | Description |
|---|---|---|---|---|
| `flags` | 8 bits | `8'h00` | `hcpu_regfile.v` | Status flags |
| `pc` | 32 bits | `32'h0` | `hcpu_fetch.v` | Program counter |
| `sp` | 8 bits | `8'h00` | `hcpu_memory.v` | Stack pointer |

### 3.4 Flag Register

| Bit | Name | Set By | Description |
|---|---|---|---|
| `[0]` | `FLAG_G` | `HGRD` | Guard pass (`1`) / fail (`0`) — maps to EXM audit |
| `[1]` | `FLAG_Z` | `CMP`, `CMPI` | Zero (equality) |
| `[2]` | `FLAG_O` | — | Reserved (overflow, unused in Phase 1.5) |
| `[3]` | `FLAG_LT` | `CMP`, `CMPI` | Less-than (sign bit of subtraction result) |

### 3.5 Transparent Write-Through Bypass

Both register banks implement same-cycle bypass to resolve RAW hazards between WB and ID:

```verilog
assign gpr_rdata1 = (gpr_we && gpr_waddr == gpr_raddr1) ? gpr_wdata : gpr[gpr_raddr1];
```

> [!NOTE]
> This bypass resolves RAW hazards only. WAW hazards are structurally impossible in this in-order single-write-port pipeline.

---

## 4. Pipeline Stages

### 4.1 IF — Fetch (`hcpu_fetch.v`)

| Condition | `pc` | `if_instruction` |
|---|---|---|
| Normal | `pc ← pc + 1` | 2-phase fetch: wait for `fetch_valid`, then latch `imem_data` |
| `pc_stall = 1` | Hold | Hold. `imem_ce = 0` — BRAM output register frozen. |
| `if_flush = 1` | `pc ← branch_target` | Insert NOP, clear `fetch_valid` (1 bubble cycle for BRAM read) |
| `rst_n = 0` | `← 0` | Insert NOP, clear `fetch_valid` |

> [!NOTE]
> The fetch stage implements a 2-phase fetch (`fetch_valid` flag) to compensate for the 1-cycle synchronous read latency of FPGA BRAM. After a reset or taken branch, one NOP bubble is inherently injected to allow the BRAM read pipeline to catch up.
>
> **BRAM clock enable (`imem_ce`)**: The fetch module outputs `imem_ce = !stall` to gate the external BRAM output register. During pipeline stalls, this prevents the BRAM from overwriting in-flight instruction data with the next address's content (see BUG-08 errata).

### 4.2 ID — Decode (`hcpu_decode.v`)

**Instruction format**: `[31:24] OP  [23:20] DST  [19:16] S1  [15:12] S2  [11:0] IMM`

Key responsibilities:
- Field extraction and control signal generation
- Register file read address driving (combinational)
- **Load-use hazard detection** via operand-used flags
- **Invalid opcode trapping** → `HALT_ERR` (no side effects, no writes)

**Operand-used decode** (two independent `case` blocks):
```verilog
// S1 readers: MOV, ADD, SUB, MUL, CMP, ADDI, CMPI, LOAD, STORE,
//             HCADD, HGRD, HNRM2, HDIST, PRINT, PUSH
// S2 readers: ADD, SUB, MUL, CMP, STORE, HCADD, HDIST
```

### 4.3 EX — Execute (`hcpu_execute.v`)

Contains three parallel computation units and branch resolution:

| Unit | Inputs | Output | Operations |
|---|---|---|---|
| Scalar ALU | GPR operands | 32-bit result | ADD, ADDI, SUB, MUL, MOV, MOVI, CMP, CMPI |
| Codex ALU | H-Reg operands via `hcpu_codex_alu.v` | 144-bit vector or 32-bit scalar | HCADD, HNRM2, HDIST |
| Guard checker | H-Reg operand via `hcpu_guard.v` | 1-bit pass/fail → FLAG_G | HGRD (`PIPELINE_GUARD` configurable) |
| Branch resolver | Flags + opcode | `branch_taken`, `branch_target` | JMP, JEQ, JNE, JGD, JNGD |

> [!NOTE]
> The `MUL` instruction uses the `hcpu_mul` module with a `USE_DSP` parameter. For FPGA targets, `USE_DSP=1` infers a DSP48 block. For ASIC/MPW targets, `USE_DSP=0` instantiates an area-efficient 5-level combinational shift-add tree.

**Branch resolution** is combinational within the EX stage. When taken, the controller flushes IF/ID and ID/EX, incurring a **fixed 1-cycle branch penalty**.

**Flags forwarding**: CMP result computed in the current EX cycle is forwarded immediately for same-cycle branch decisions.

### 4.4 MEM — Memory (`hcpu_memory.v`)

- **Data RAM**: LOAD address = `GPR[S1] + sign_ext(IMM)`, STORE address = `GPR[S2] + sign_ext(IMM)`
- **Stack**: PUSH writes `stack[sp] ← GPR[S1]`, increments `sp`. POP decrements `sp`, reads `stack[sp-1]`.
- **Write gate**: `dram_we` is gated by `!stall` to prevent spurious writes during pipeline freezes.
- **Result mux** (priority): POP data → LOAD data → EX passthrough.

### 4.5 WB — Writeback (`hcpu_writeback.v`)

Purely combinational pass-through from MEM pipeline registers to register file write ports. Asserts `wb_halt` to latch processor halt.

---

## 5. Hazard Resolution

### 5.1 Data Forwarding (`hcpu_forward.v`)

Combinational bypass MUX network:
```
Priority: EX forward (most recent) → MEM forward → register file read
```
Forwarding applies independently to both GPR (32-bit) and H-Reg (144-bit) operands.

### 5.2 Load-Use Hazard (1-Cycle Stall)

**Rationale**: A `LOAD` result is not available until the MEM/WB pipeline register is latched. An instruction in ID that depends on the loaded register cannot proceed.

**Detection** (combinational, in `hcpu_decode.v`):
```verilog
load_use_hazard = id_mem_read && (id_dst != 0) &&
                 ((id_uses_s1 && (s1 == id_dst)) ||
                  (id_uses_s2 && (s2 == id_dst)));
```

> [!NOTE]
> The hazard is detected when the LOAD is in the **ID pipeline register** (not EX), because the BRAM-pipelined fetch timing means the dependent instruction arrives at IF in the same cycle the LOAD enters ID. See BUG-06 and BUG-07 errata.

**Resolution** (in `hcpu_controller.v`):

| Stage | Action |
|---|---|
| PC / IF | **Frozen** (`pc_stall = 1`). PC and IF/ID register hold current values. |
| ID | IF/ID register continues to hold. Instruction in ID is **preserved**, not flushed. |
| ID/EX | **Flushed** (`id_flush = 1`). NOP bubble injected into EX. |
| EX / MEM / WB | Continue normally. LOAD proceeds through MEM and WB. |

After 1 stall cycle, the dependent instruction enters EX with the load result available via MEM→ID forwarding or register file write-through.

### 5.3 Store-to-Load Hazard (1-Cycle Stall)

**Rationale**: Since there is no store-to-load forwarding through memory, a `LOAD` instruction that reads from the same address as an immediately preceding `STORE` would read stale data from the cycle before the `STORE` completes.

**Detection** (combinational, in `hcpu_decode.v`):
```verilog
store_load_hazard = ex_mem_write && id_is_load_op &&
                   (ex_mem_addr == id_load_addr);
```

**Resolution**: Identical to load-use hazards. The front-end (PC/IF) is frozen and a 1-cycle bubble is injected into EX, ensuring the `STORE` commits to memory before the `LOAD` reads from it.

### 5.4 Branch Flush

When `branch_taken = 1` and `global_stall = 0`:

| Stage | Action |
|---|---|
| IF/ID | Flushed (`if_flush = 1`). NOP inserted, PC redirected. |
| ID/EX | Flushed (`id_flush = 1`). Speculative instruction invalidated. |
| EX / MEM / WB | Continue. No speculative instruction commits. |

### 5.5 UART Blocking Stall

When `PRINT` is active and `uart_busy = 1`, **all stages** freeze (`global_stall = 1`) until transmission completes.

### 5.6 Controller Signal Equations

```verilog
global_stall = (print_pending && uart_busy) || halted;
data_hazard  = load_use_hazard || store_load_hazard;
pc_stall     = global_stall || data_hazard;
id_stall     = global_stall;
ex_stall     = global_stall;
if_flush     = branch_taken && !global_stall;
id_flush     = (branch_taken || data_hazard) && !global_stall;
```

---

## 6. Codex Subsystem

This subsystem is the hardware realization of the Hybit paradigm's core operations.

### 6.1 Master Table ROM (`hcpu_rom.v`) — Dataset Seal Implementation

| Property | Value |
|---|---|
| Valid entries | 28 (indices 1–28, Alif through Ya) |
| Invalid test entry | Index 31 (corrupt vector for guard validation) |
| Entry width | 144 bits (18 × 8-bit components) |
| Read latency | Combinational (asynchronous `case` statement) |
| Address width | 5 bits |
| Invalid index | Returns `data_out = 0`, `valid = 0` |
| Data source | `data/hm28.json` (SHA-256: `81af756b...`) |

Index 31 contains `{Θ̂=1, Qc=2}`: intentionally fails G4 ($\theta=1$, $U=4 \times Q_c = 8$, $1 \ge 8$ → FALSE). Used exclusively for hardware guard validation.

### 6.2 Guard Checker (`hcpu_guard.v`) — EXM Hardware Implementation

Single-cycle combinational comparator network implementing all six structural constraints from Bab I:

| Check | Formula | Hybit Invariant |
|---|---|---|
| G1 | $A_N = N_a + N_b + N_d$ | Nuqṭah aggregate |
| G2 | $A_K = K_p + K_x + K_s + K_a + K_c$ | Khaṭṭ aggregate |
| G3 | $A_Q = Q_p + Q_x + Q_s + Q_a + Q_c$ | Qaws aggregate |
| G4 | $\hat\Theta \ge U$, where $U = Q_x + Q_s + Q_a + 4Q_c$ | Turning sufficiency |
| T1 | $K_s > 0 \Rightarrow Q_c \ge 1$ | Secondary khatt topology |
| T2 | $K_c > 0 \Rightarrow Q_c \ge 1$ (Kaf exception) | Closing khatt topology |

`guard_pass = G1 & G2 & G3 & G4 & T1 & T2`

This is the **O(1) intrinsic validation** — the defining property of hybit that distinguishes it from bit and qubit.

### 6.3 Codex ALU (`hcpu_codex_alu.v`) — Hybit Engine Hardware

All operations are **single-cycle combinational** (`done` hardwired to `1`).

| Opcode | Operation | Hybit MV Op | Formula | Output |
|---|---|---|---|---|
| `HCADD` | Component-wise add | **AGM** | $H_{dst}[i] = H_{s1}[i] + H_{s2}[i]$, $i \in [0,17]$ | 144-bit vector |
| `HNRM2` | Squared norm (14D) | **VTM** | $R_{dst} = \sum_{i=0}^{13} H_{s1}[i]^2$ | 32-bit scalar |
| `HDIST` | Squared distance (14D) | **ITM** | $R_{dst} = \sum_{i=0}^{13} (H_{s1}[i] - H_{s2}[i])^2$ | 32-bit scalar |

> [!IMPORTANT]
> `HNRM2` and `HDIST` operate on indices 0–13 only (Θ̂ through Qc). Indices 14–17 (A_N, A_K, A_Q, Ψ) are aggregates and are excluded from distance metrics by design. This matches the software `algebra/intrametric.py` implementation.

**Arithmetic bounds**: Component values max at 8 (Θ̂ for Haa). Square max = 64 (7 bits). Sum of 14 squares max = 896 (10 bits). `HCADD` accumulation safe for ~30 characters before 8-bit overflow.

### 6.4 HISAB Serializer (`hcpu_hisab.v`) — Auditable Bridging Hardware

The HISAB (Hijaiyyah Inter-System Standard for Auditable Bridging) module implements the protocol's two core operations in hardware:

| Opcode | Operation | Description | Output |
|---|---|---|---|
| `HPACK` (`0x50`) | Nibble-pack | Packs 18 H-Reg components into three 32-bit GPR words (4-bit nibbles) | `GPR[DST] ← pack_word[S2]` |
| `HCRC` (`0x51`) | CRC32 digest | Computes IEEE 802.3 CRC32 over the 12-byte HISAB LETTER frame | `GPR[DST] ← CRC32(pack_word0 ∥ pack_word1 ∥ pack_word2)` |

**HPACK nibble layout** (pack_word0 as example):
```
pack_word0[31:28] = comp[7]   // Ka
pack_word0[27:24] = comp[6]   // Ks
...                            // 4 bits per component
pack_word0[3:0]   = comp[0]   // Θ̂
```

**HCRC implementation**: Bit-serial CRC32 with polynomial `0x04C11DB7`, processing 96 bits (12 bytes) in a single combinational pass. Cross-validated against Python `zlib.crc32()` reference for all 28 letters.

> [!NOTE]
> Both HISAB operations are **single-cycle combinational**. The guard checker validates the H-Reg input before packing — invalid vectors are caught by `HGRD` before reaching `HPACK`/`HCRC`.

---

## 7. Memory Subsystem

### 7.1 Instruction Memory

| | Simulation | FPGA |
|---|---|---|
| Type | Testbench `reg` array | Synchronous Block RAM |
| Depth | 4096 words | 1024 words (Arty A7) |
| Width | 32 bits | 32 bits |
| Read latency | 1 cycle (BRAM-style, `imem_ce`-gated) | 1 cycle (BRAM) |
| Clock enable | `imem_ce` from fetch (holds during stall) | BRAM CE pin |
| Initialization | Inline in testbench | `$readmemh("program.hex")` |

> [!NOTE]
> Both simulation and physical FPGA/MPW instruction memories now use synchronous BRAM read (`always @(posedge clk) if (imem_ce) imem_data <= imem[addr]`). The `imem_ce` signal from the fetch module gates the BRAM output register during pipeline stalls, preventing in-flight instruction data loss. The fetch stage (§4.1) compensates for the 1-cycle latency via 2-phase `fetch_valid` tracking.

### 7.2 Data RAM (`hcpu_dataram.v`)

| Property | Value |
|---|---|
| Type | On-chip RAM (infers BRAM on FPGA) |
| Depth | 4096 words |
| Width | 32 bits, **word-addressed** (not byte-addressed) |
| Total size | 16 KB |
| Write | Synchronous (rising edge, when `we=1`) |
| Read | Combinational (`assign rdata = mem[addr]`) |
| Initialization | Zero-filled (simulation only) |

> [!NOTE]
> Store-to-load hazard is now handled in hardware (§5.3). The controller automatically inserts a 1-cycle stall when a `LOAD` targets the same address as an immediately preceding `STORE`. No software NOP insertion is required.

### 7.3 Hardware Stack

| Property | Value |
|---|---|
| Depth | 256 entries × 32 bits |
| Location | Register array in `hcpu_memory.v` |
| Overflow | **HALT_ERR** via HCHECK HC-02 (`PUSH` when `sp ≥ 256`) |
| Underflow | **HALT_ERR** via HCHECK HC-03 (`POP` when `sp == 0`) |

### 7.4 HCHECK — Hardware Runtime Invariant Checker

HCHECK is the hardware realization of the `vm/HCheck` validation layer. It enforces runtime invariants that cannot be detected at compile time, halting the processor with `HALT_ERR` on violation.

| ID | Check | Detection Location | Trigger Condition | Action |
|---|---|---|---|---|
| HC-00 | Invalid opcode | `hcpu_decode.v` (default case) | Unknown opcode in instruction stream | `id_is_halt ← 1`, suppress all writes |
| HC-01 | Invalid ROM index | `hcpu_execute.v` | `HLOAD` with `rom_valid == 0` | `ex_is_halt ← 1`, suppress H-Reg write |
| HC-02 | Stack overflow | `hcpu_memory.v` | `PUSH` when `sp ≥ STACK_DEPTH` | `mem_is_halt ← 1`, suppress PUSH |
| HC-03 | Stack underflow | `hcpu_memory.v` | `POP` when `sp == 0` | `mem_is_halt ← 1`, suppress POP |

> [!IMPORTANT]
> All HCHECK traps are **zero-side-effect**: on fault, the offending operation is suppressed (no register/memory writes) and the processor halts cleanly. This is the hardware equivalent of the software `HCheck.validate()` throwing an exception.

---

## 8. I/O: UART Transmitter (`hcpu_uart_tx.v`)

| Property | Value |
|---|---|
| Protocol | 8N1 (8 data, no parity, 1 stop) |
| Baud | 115200 (configurable via parameter) |
| Divider | `CLK_HZ / BAUD` = 434 clocks/bit @ 50 MHz |
| Idle line | High |
| Busy signal | `tx_busy = (state != S_IDLE)` |

**Print FSM** (in `hcpu_top.v`): `PRINT Rn` converts `GPR[Rn]` to decimal ASCII, sends MSB-first, appends `\n` (0x0A). Entire pipeline frozen during transmission.

---

## 9. H-ISA Opcode Reference (Phase 2.0)

### 9.1 Instruction Format

```
[31:24] OPCODE   [23:20] DST   [19:16] S1   [15:12] S2   [11:0] IMM
   8 bits          4 bits       4 bits       4 bits       12 bits
```

### 9.2 Complete Opcode Table

| Mnemonic | Hex | MV Op | Format | Semantics | Cycles |
|---|---|---|---|---|---|
| `NOP` | `0x00` | — | — | No operation | 1 |
| `HALT` | `0x01` | — | — | Halt processor, latch `halted` | 1 |
| `MOV` | `0x03` | — | `DST, S1` | `GPR[DST] ← GPR[S1]` | 1 |
| `MOVI` | `0x04` | — | `DST, IMM` | `GPR[DST] ← zero_ext(IMM)` | 1 |
| `ADD` | `0x10` | — | `DST, S1, S2` | `GPR[DST] ← GPR[S1] + GPR[S2]` | 1 |
| `ADDI` | `0x11` | — | `DST, S1, IMM` | `GPR[DST] ← GPR[S1] + sign_ext(IMM)` | 1 |
| `SUB` | `0x12` | — | `DST, S1, S2` | `GPR[DST] ← GPR[S1] − GPR[S2]` | 1 |
| `MUL` | `0x14` | — | `DST, S1, S2` | `GPR[DST] ← (GPR[S1] × GPR[S2])[31:0]` | 1 |
| `CMP` | `0x20` | — | `S1, S2` | Flags ← `GPR[S1] − GPR[S2]` (no write) | 1 |
| `CMPI` | `0x21` | — | `S1, IMM` | Flags ← `GPR[S1] − sign_ext(IMM)` | 1 |
| `JMP` | `0x22` | — | `IMM` | `PC ← zero_ext(IMM)` | 1+1 flush |
| `JEQ` | `0x23` | — | `IMM` | If `Z=1`: `PC ← PC + sign_ext(IMM)` | 1+0/1 |
| `JNE` | `0x24` | — | `IMM` | If `Z=0`: `PC ← PC + sign_ext(IMM)` | 1+0/1 |
| `JGD` | `0x29` | EXM | `IMM` | If `G=1`: `PC ← PC + sign_ext(IMM)` | 1+0/1 |
| `JNGD` | `0x2A` | EXM | `IMM` | If `G=0`: `PC ← PC + sign_ext(IMM)` | 1+0/1 |
| `LOAD` | `0x30` | — | `DST, S1, IMM` | `GPR[DST] ← DataRAM[GPR[S1] + sign_ext(IMM)]` | 1 (+1 stall if dependent) |
| `STORE` | `0x31` | — | `S1, S2, IMM` | `DataRAM[GPR[S2] + sign_ext(IMM)] ← GPR[S1]` | 1 |
| `PUSH` | `0x32` | — | `S1` | `stack[sp] ← GPR[S1]; sp++` | 1 |
| `POP` | `0x33` | — | `DST` | `sp--; GPR[DST] ← stack[sp]` | 1 |
| `HLOAD` | `0x40` | — | `DST, IMM` | `H[DST] ← ROM[IMM]` (1–28 valid) | 1 |
| `HCADD` | `0x42` | **AGM** | `DST, S1, S2` | `H[DST][i] ← H[S1][i] + H[S2][i]` ∀i | 1 |
| `HNRM2` | `0x06` | **VTM** | `DST, S1` | `GPR[DST] ← Σᵢ₌₀¹³ H[S1][i]²` | 1 |
| `HDIST` | `0x07` | **ITM** | `DST, S1, S2` | `GPR[DST] ← Σᵢ₌₀¹³ (H[S1][i]−H[S2][i])²` | 1 |
| `HPACK` | `0x50` | **HISAB** | `DST, S1, S2` | `GPR[DST] ← nibble_pack(H[S1])[S2]` (word 0–2) | 1 |
| `HCRC` | `0x51` | **HISAB** | `DST, S1` | `GPR[DST] ← CRC32(pack(H[S1]))` | 1 |
| `HGRD` | `0x60` | **EXM** | `S1` | Guard(H[S1]) → FLAG_G | 1 |
| `PRINT` | `0xA0` | — | `S1` | UART decimal print `GPR[S1]` | N (blocking) |
| *default* | — | — | — | → `HALT_ERR`: halt, no side effects | — |

---

## 10. FPGA Implementation

### 10.1 Arty A7-35T — Full Build (`hcpu_xilinx_top.v`)

| Resource | Available | Target |
|---|---|---|
| LUT | 20,800 | < 80% |
| FF | 41,600 | < 70% |
| BRAM (36Kb) | 50 | < 60% |
| DSP48E1 | 90 | < 50% |

**Instruction Memory**: Implemented using true synchronous block RAM (BRAM). The read port is strictly gated by the pipeline's `imem_ce` signal, guaranteeing exactly matching simulated hardware cycle behavior during data hazard stalls.

**Clock**: 100 MHz (pin E3) → MMCM → 50 MHz
**Reset**: BTN0 (pin D9), active high. 3-stage synchronizer gated by MMCM lock.

| LED | Function |
|---|---|
| `led[0]` | Guard flag (FLAG_G) |
| `led[1]` | Halted indicator |
| `led[2]` | MMCM locked |
| `led[3]` | Reset deasserted |

**Reset state**: PC=0, GPR=0, H-Reg=0, Flags=`8'h00`, SP=0, UART=idle (`tx_out=1`), `halted=0`.

### 10.2 iCE40UP5K — Reduced Build

> [!WARNING]
> The iCE40UP5K (5,280 LUTs, 30 EBR, 8 DSP) cannot fit the full design. A reduced configuration is required:
> - GPR: 8 instead of 18
> - H-Reg: 4 instead of 16
> - Data RAM: 256 instead of 4096 words
> - Potentially simplified guard (G1–G3 only)

### 10.3 Clock Domain Analysis (CDC Report)

**Conclusion: HCPU is a single-clock-domain design. No CDC paths exist.**

#### 10.3.1 Clock Domain Inventory

| Domain | Clock Signal | Source | Consumers |
|---|---|---|---|
| `sys_clk` | `clk` (core) / `clk_50m` (FPGA) / `wb_clk_i` (MPW) | MMCM (Xilinx), rPLL (Gowin), or Caravel bus clock | All 15 core modules, UART, Data RAM, Stack |

#### 10.3.2 Clocked Process Audit (19 processes, 15 modules)

| Module | Process Edge | Reset | Domain | Notes |
|---|---|---|---|---|
| `hcpu_fetch.v` | `posedge clk` | `negedge rst_n` | sys_clk | PC + pipeline register |
| `hcpu_decode.v` | `posedge clk` | `negedge rst_n` | sys_clk | ID/EX pipeline register |
| `hcpu_execute.v` | `posedge clk` | `negedge rst_n` | sys_clk | EX/MEM pipeline register |
| `hcpu_memory.v` | `posedge clk` | `negedge rst_n` | sys_clk | Stack pointer (×2 processes) |
| `hcpu_regfile.v` | `posedge clk` | `negedge rst_n` | sys_clk | GPR + H-Reg + Flags write |
| `hcpu_controller.v` | `posedge clk` | `negedge rst_n` | sys_clk | print_pending + halted (×2) |
| `hcpu_uart_tx.v` | `posedge clk` | `negedge rst_n` | sys_clk | Shift register + baud counter |
| `hcpu_dataram.v` | `posedge clk` | — (no reset) | sys_clk | Synchronous write (infers BRAM) |
| `hcpu_guard.v` | `posedge clk` | `negedge rst_n` | sys_clk | Optional pipeline register (`PIPELINE_GUARD=1`) |
| `hcpu_top.v` | `posedge clk` | `negedge rst_n` | sys_clk | PRINT FSM |
| `hcpu_xilinx_top.v` | `posedge clk_50m` | — (sync reset) | sys_clk | Reset sync + IMEM BRAM |
| `hcpu_gowin_top.v` | `posedge clk_50m` | `negedge btn_rst_n` | sys_clk | Reset sync + IMEM BRAM |
| `hcpu_mpw_top.v` | `posedge sys_clk` | — | sys_clk | IMEM write port |
| `hcpu_wb_adapter.v` | `posedge wb_clk_i` | — | sys_clk | Wishbone register interface (×2) |

#### 10.3.3 Asynchronous Boundary Inventory

| Boundary | Type | Synchronizer | Depth | Location |
|---|---|---|---|---|
| Xilinx: `btn_rst` → `sys_rst_n` | Async button input | 3-stage shift register, gated by MMCM lock | 3 FF | `hcpu_xilinx_top.v:43-48` |
| Gowin: `btn_rst_n` → `sys_rst_n` | Async button input | 3-stage shift register with async assert | 3 FF | `hcpu_gowin_top.v:36-44` |
| MPW: `wb_rst_i` → `core_rst_n` | Caravel bus reset | Direct (synchronous to `wb_clk_i`) | 0 (sync) | `hcpu_mpw_top.v` |

> [!NOTE]
> **No multi-clock FIFOs, no gray-code counters, no pulse synchronizers are required.** The HCPU core receives exactly one clock from its wrapper. The UART TX output is a registered signal in the `sys_clk` domain — the external FTDI/USB bridge handles its own sampling.

#### 10.3.4 Combinational-Only Modules (No Clock)

| Module | Type |
|---|---|
| `hcpu_rom.v` | Asynchronous `case` lookup (no clock) |
| `hcpu_forward.v` | Combinational bypass MUX |
| `hcpu_writeback.v` | Combinational pass-through |
| `hcpu_mul.v` (`USE_DSP=0`) | Combinational adder tree |
| `hcpu_codex_alu.v` | Combinational vector ALU |

---

## 11. MPW / ASIC Readiness

HCPU has a defined path to silicon via `rtl/mpw/hcpu_mpw_top.v` (Caravel-compatible wrapper for Efabless Open MPW, SkyWater SKY130).

### 11.1 Synthesis Results (measured)

| Module | Cells (measured) | Flip-flops |
|---|---|---|
| `hcpu_dataram` (4096×32) | 416,165 | 131,072 |
| `hcpu_memory` (256×32 stack) | 25,480 | 8,392 |
| `hcpu_regfile` (18 GPR + 16 H-Reg) | 16,486 | 2,920 |
| `hcpu_codex_alu` | 12,135 | 0 |
| `hcpu_mul` | 2,964 | 0 |
| `hcpu_execute` | 2,687 | 249 |
| `hcpu_hisab` | 1,263 | 0 |
| `hcpu_decode` | 1,061 | 427 |
| `hcpu_forward` | 740 | 0 |
| `hcpu_top` | 700 | 95 |
| `hcpu_guard` | 609 | 0 |
| `hcpu_fetch` | 294 | 129 |
| `hcpu_rom` (28×144) | 109 | 0 |
| `hcpu_uart_tx` | 89 | 23 |
| `hcpu_controller` | 13 | 2 |
| **Total** | **480,795** | **143,309** |

Generic-gate counts from Yosys 0.68 (`rtl/mpw/synth_hcpu.ys`); full report in
`rtl/mpw/hcpu_synth_report.txt`. **No PDK was installed for this run**, so these
are not mapped standard cells and no um2 area or timing can be derived from them.

**`hcpu_dataram` is 87% of the design.** 4096 words x 32 bits infers 131,072
flip-flops because the RTL describes a register array, not a memory macro.
Excluding it, the design is 64,630 cells.

Before any tape-out attempt the data RAM must become an SRAM macro (e.g. OpenRAM
on SKY130) or shrink — 131,072 flip-flops will not fit the 700x700 um user area
in `config.json`. The same applies to the 256x32 stack in `hcpu_memory`.

Critical path: 84 logic levels through the divide/modulo-by-10 at
`hcpu_top.v:193-194` (decimal conversion in the PRINT FSM).

### 11.2 MPW File Inventory

| File | Status | Description |
|---|---|---|
| `hcpu_mpw_top.v` | ✅ Created (v2.1) | Full Caravel `user_project_wrapper` with WB, LA, GPIO, IRQ, and BRAM-style IMEM |
| `hcpu_wb_adapter.v` | ✅ Created | Wishbone B4 slave — 8-register memory map |
| `hcpu_firmware.h` | ✅ Created | C header for management SoC firmware |
| `config.json` | ✅ Created | OpenLane synthesis config (SKY130, 40 MHz, 700×700 μm) |
| `pin_order.cfg` | ✅ Created | Pin placement by edge (S/N/E/W) |
| `Makefile` | ✅ Created | `make harden`, `make lint`, `make clean` |
| `synth_hcpu.ys` | ✅ Created | Yosys synthesis script for area/timing estimation |

### 11.3 MPW Remaining Prerequisites

| Item | Status |
|---|---|
| DFT hooks (scan chain) | ❌ Not applicable for Phase 2.0 |
| Power intent (single domain, no UPF needed) | ✅ Confirmed |
| MUL implementation for ASIC (shift-add vs `*`) | ✅ Done — `hcpu_mul` with `USE_DSP` parameter |
| BRAM synchronous alignment | ✅ Done — Physical wrapper IMEM uses `imem_ce` for 1-cycle sync read |
| GPR read-back port (dedicated, not hierarchical) | ✅ Done — 3rd read port on `hcpu_regfile`, exposed via `hcpu_top` |
| Hierarchical path elimination | ✅ Done — `hcpu_mpw_top.v` no longer uses `u_hcpu.u_regfile.gpr[...]` |

---

## 12. Assembler Toolchain (`asm2hex.py`)

### 12.1 Compile-Time Bounds Checking

| Check | Valid Range | Error |
|---|---|---|
| GPR index | `R0`–`R17` | `ValueError` |
| H-Reg index | `H0`–`H15` | `ValueError` |
| Signed immediate | `−2048` to `+2047` | `ValueError` |
| Mnemonic | Known opcodes only | `ValueError` |

### 12.2 Assembly Features

- Two-pass assembly with forward/backward label resolution
- Branch offsets: PC-relative (signed 12-bit)
- `JMP` target: absolute (unsigned 12-bit)
- Output: `$readmemh`-compatible hex file

---

## 13. RTL Source Inventory

| File | Lines | Hybit Layer |
|---|---|---|
| [hcpu_pkg.vh](file:///c:/hijaiyyah-mathematics/rtl/hcpu_pkg.vh) | 128 | H-ISA constants |
| [hcpu_top.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_top.v) | ~531 | Top-level integration |
| [hcpu_fetch.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_fetch.v) | 92 | IF stage (2-phase BRAM-safe + `imem_ce`) |
| [hcpu_decode.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_decode.v) | ~222 | ID stage + load-use + store-load hazard |
| [hcpu_execute.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_execute.v) | ~263 | EX stage (parameterized MUL) |
| [hcpu_mul.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_mul.v) | ~72 | ASIC/FPGA multiplier (`USE_DSP`) |
| [hcpu_memory.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_memory.v) | 111 | MEM stage |
| [hcpu_writeback.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_writeback.v) | 47 | WB stage |
| [hcpu_forward.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_forward.v) | 92 | Data forwarding |
| [hcpu_controller.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_controller.v) | ~90 | Stall/flush/halt (v2.0) |
| [hcpu_regfile.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_regfile.v) | ~98 | HVM register file (3-port GPR + debug) |
| [hcpu_rom.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_rom.v) | 213 | Dataset Seal (Master Table) |
| [hcpu_guard.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_guard.v) | ~130 | EXM — Guard System (`PIPELINE_GUARD`) |
| [hcpu_codex_alu.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_codex_alu.v) | 115 | Hybit Engine (AGM/VTM/ITM) |
| [hcpu_hisab.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_hisab.v) | ~180 | HISAB serializer (nibble-pack + CRC32) |
| [hcpu_dataram.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_dataram.v) | 48 | Data memory |
| [hcpu_uart_tx.v](file:///c:/hijaiyyah-mathematics/rtl/hcpu_uart_tx.v) | 98 | UART TX |
| [hcpu_xilinx_top.v](file:///c:/hijaiyyah-mathematics/rtl/fpga/xilinx/hcpu_xilinx_top.v) | 92 | FPGA wrapper (imem_ce sync read) |
| [hcpu_mpw_top.v](file:///c:/hijaiyyah-mathematics/rtl/mpw/hcpu_mpw_top.v) | ~180 | MPW Caravel wrapper (imem_ce sync read) |
| [hcpu_wb_adapter.v](file:///c:/hijaiyyah-mathematics/rtl/mpw/hcpu_wb_adapter.v) | ~140 | Wishbone B4 slave adapter |
| [synth_hcpu.ys](file:///c:/hijaiyyah-mathematics/rtl/mpw/synth_hcpu.ys) | ~56 | Yosys synthesis script |
| [lint_hcpu.py](file:///c:/hijaiyyah-mathematics/rtl/scripts/lint_hcpu.py) | ~160 | Verilator lint runner (3-target) |

---

## 14. Verification Status

### 14.1 Integration Test Suite (`tb_hcpu_top`)

| # | Test | DVP ID | Asserts | Expected | Status |
|---|---|---|---|---|---|
| 1 | Guard check on valid vector (Ba) | — | 2 | `guard_led=1`, `R0=42` | ✅ PASS |
| 2 | BSM string integral (Ba+Sin+Mim) | — | 2 | `Θ̂=10`, `‖BSM‖²=112` | ✅ PASS |
| 3 | Loop with branch (count to 3) | HAZ-03 | 1 | `R0=3` | ✅ PASS |
| 4 | Data RAM store/load round-trip | HAZ-02 | 1 | `R3=99` | ✅ PASS |
| 5 | Negative guard (corrupt idx 31) | CDX-02 | 1 | `JNGD` taken, `R1=200` | ✅ PASS |
| 6 | Load-use hazard stall | HAZ-01 | 1 | `R4=10` (5+5) | ✅ PASS |
| 7 | HISAB HPACK+HCRC (Ba golden) | HISAB-01 | 2 | `pack_word0=0x00010120`, `CRC32=0x9A3115CC` | ✅ PASS |

### 14.2 Standalone Testbenches

| Testbench | Scope | Tests | Status |
|---|---|---|---|
| `tb_hisab.v` | All 28 letters: nibble-pack + guard + CRC32 + 3 golden cross-validations | 124 | ✅ ALL PASS |
| `tb_guard.v` | 28 valid letters + 6 corruption injection | 34 | ✅ ALL PASS |
| `tb_codex_alu.v` | HCADD, HNRM2, HDIST | 6 | ✅ ALL PASS |
| `tb_rom.v` | 28 ROM entries | — | ✅ ALL PASS |
| **Total** | | **174** | **✅ 0 FAIL** |

### 14.2 Post-Synthesis

| ID | Test | Requires | Tooling |
|---|---|---|---|
| HW-01 | Timing closure (WNS ≥ 0, TNS ≥ 0) | Vivado or Yosys+STA | `mpw/synth_hcpu.ys` |
| HW-02 | Resource utilization within ceiling | Vivado or Yosys | `mpw/synth_hcpu.ys` → `stat` |
| HW-03 | Physical reset recovery | Board | Manual |
| HW-04 | UART output matches simulation | Board + terminal | Manual |
| HW-05 | Lint clean (0 errors, 0 warnings) | Verilator | `scripts/lint_hcpu.py` |

---

## 15. Industry Readiness Checklist

| Item | Status | Notes |
|---|---|---|
| RTL simulation (cycle-accurate) | ✅ Done | 7 programs, 10 assertions, 174 total tests, 0 FAIL |
| Physical wrapper integrity | ✅ Done | FPGA and MPW verified with BRAM clock-enable (`imem_ce`) |
| Assembler bounds checking | ✅ Done | Register, immediate, mnemonic |
| IMEM BRAM latency alignment | ✅ Done | 2-phase fetch with `fetch_valid` sync + `imem_ce` BRAM gating |
| Load-use hazard protection | ✅ Done | 1-cycle stall with ID-stage detection + operand-used filter |
| HISAB protocol (HPACK/HCRC) | ✅ Done | Nibble-pack + CRC32, cross-validated vs Python `zlib.crc32()` |
| Store-load hazard protection | ✅ Done | 1-cycle stall on address match in ID/EX |
| Branch flush (IF/ID + ID/EX) | ✅ Done | 1-cycle penalty, no speculative commit |
| ASIC-safe multiplier (shift-add) | ✅ Done | `hcpu_mul` with `USE_DSP` switch |
| Invalid opcode trap | ✅ Done | Decode default → HALT_ERR |
| FPGA synthesis script | ✅ Done | Vivado TCL for Arty A7-35T |
| Pin constraints (XDC) | ✅ Done | Clock, reset, UART TX, LEDs |
| MPW wrapper (Caravel) | ✅ Done | `hcpu_mpw_top.v` with program loader |
| Clock domain analysis | ✅ Done | Single domain, 0 CDC paths. Formal audit in §10.3 |
| GPR read-back (synthesis-safe) | ✅ Done | 3rd GPR read port, no hierarchical paths |
| Lint tooling | ✅ Done | `scripts/lint_hcpu.py` — Verilator multi-target |
| Synthesis tooling | ✅ Done | `mpw/synth_hcpu.ys` — Yosys area/timing script |
| Board-level UART test | ❌ Pending | Requires physical board |
| Power intent (UPF/CPF) | N/A | Single always-on domain |
| DFT (scan/JTAG/BIST) | N/A (FPGA) | Required for MPW tapeout |
| Formal verification | ❌ Planned | SymbiYosys, Phase 3 |

---

## 16. Known Limitations (Phase 2.0 - RTL Hardened)

1. **No branch predictor.** Fixed 1-cycle penalty. Resolution in EX stage.
2. **No byte/half-word access.** Data RAM is word-addressed (32-bit granularity).
3. **Codex ALU single-cycle only.** `done` hardwired to 1. Multi-cycle ops need controller integration.
4. **No interrupt support.** Processor runs to HALT or loops.
5. **iCE40UP5K untested.** Full design likely exceeds resources.
6. **No HPROJ, HDCMP, HEXMT.** Phase 2 H-ISA instructions not yet implemented.
7. **HPACK word index via S2 field.** The `S2` field selects which of the 3 packed words to return (0, 1, or 2). Requires 3 instructions to retrieve the full packed representation.

---

## 17. Errata

| ID | Severity | Description | Resolution |
|---|---|---|---|
| BUG-01 | **CRITICAL** | `id_uses_s2` never asserted due to Verilog `case` fall-through. S2 load-use stall broken. | Fixed: split into two independent `case` blocks in `hcpu_decode.v`. |
| BUG-02 | **HIGH** | IMEM latency mismatch: simulation (combinational) vs FPGA (synchronous BRAM 1-cycle). First instruction after reset/branch could be wrong on hardware. | Fixed: rewritten `hcpu_fetch.v` v2.0 with 2-phase `fetch_valid` tracking. |
| BUG-03 | **HIGH** | `STORE` → `LOAD` same-address within 1 instruction reads stale data. No hardware interlock. | Fixed: `store_load_hazard` detection in `hcpu_decode.v`, 1-cycle stall in controller. |
| BUG-04 | **HIGH** | `MUL` uses `*` operator which cannot synthesize on ASIC (no DSP blocks on SKY130). | Fixed: `hcpu_mul.v` shift-add tree with `USE_DSP` parameter. |
| BUG-05 | **HIGH** | GPR read-back in `hcpu_mpw_top.v` uses hierarchical path (`u_hcpu.u_regfile.gpr[...]`) — illegal in synthesis. | Fixed: added 3rd read port to `hcpu_regfile.v`, exposed via `hcpu_top.v`. All 4 instantiation sites updated. |
| BUG-06 | **HIGH** | Testbench IMEM used combinational read (`assign imem_data = imem[addr]`), mismatching the fetch module's 1-cycle BRAM latency expectation. Caused instruction skip on every program. | Fixed: testbench IMEM changed to registered BRAM-style read with `imem_ce` clock-enable gating. |
| BUG-07 | **HIGH** | Load-use hazard detection compared IF sources against **EX stage** (`ex_mem_read`), missing the hazard window due to BRAM-pipelined fetch timing. | Fixed: detection moved to **ID stage** (`id_mem_read`, `id_dst`) in `hcpu_decode.v`. |
| BUG-08 | **HIGH** | During pipeline stalls, the BRAM output register continued updating, overwriting in-flight instruction data (e.g., HALT) with the next address's data (NOP). Caused processor hang after load-use stalls. | Fixed: added `imem_ce` output from `hcpu_fetch.v` (`assign imem_ce = !stall`), wired through `hcpu_top.v` to gate the BRAM clock-enable in both `hcpu_mpw_top.v` and `hcpu_xilinx_top.v`. |
| DOC-01 | MEDIUM | §5.2 incorrectly stated DRAM "1-cycle synchronous read". RTL uses combinational read. | Fixed: reworded to describe MEM/WB pipeline boundary. |
| DOC-02 | LOW | FPGA IMEM latency was only listed as a known limitation, not actively mitigated. | Fixed: promoted to BUG-02, resolved in `hcpu_fetch.v` v2.0. |

---

*© 2026 HMCL — Hybit Technology. Document identifier HCPU-SPEC-2.3.0. All signal names and behaviors verified against committed RTL sources. BUG-01 through BUG-08 patched in source.*
