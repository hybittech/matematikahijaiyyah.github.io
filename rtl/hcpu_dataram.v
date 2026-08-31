// ============================================================================
// HCPU Data RAM — hcpu_dataram.v
// Synchronous read/write data memory for LOAD/STORE instructions
// (c) 2026 HMCL — HM-28-v1.2-HC18D / Tier 1.5
// ============================================================================
//
// Interface: Single-port synchronous RAM
//   - Write: data written on rising clock edge when we=1
//   - Read:  registered — rdata is valid the cycle AFTER addr is presented
//
// The read used to be combinational, which is why this module could not map
// to a memory primitive: block RAM (FPGA) and SRAM macros (ASIC) both require
// a registered read port. Yosys therefore built the array from flip-flops —
// 4096 x 32 bits became 131,072 FFs, ~87% of the whole design.
//
// The one-cycle read latency costs the pipeline nothing: rdata_r IS the MEM/WB
// pipeline register for load data. hcpu_memory no longer re-registers it, so
// a LOAD still delivers its result to Writeback in exactly the same cycle.
//
// Address space: 4096 × 32-bit words = 16 KB
// FPGA: infers BSRAM on Gowin (8 SP blocks) and BRAM on Xilinx
//

`include "hcpu_pkg.vh"

module hcpu_dataram (
    input  wire                     clk,
    input  wire                     re,            // Read enable (held on stall)
    input  wire                     we,            // Write enable
    input  wire [`DATA_ADDR_W-1:0]  addr,          // Address (12 bits)
    input  wire [`XLEN-1:0]         wdata,         // Write data
    output wire [`XLEN-1:0]         rdata          // Read data (one cycle later)
);

    // ── Memory array ────────────────────────────────────────────
    reg [`XLEN-1:0] mem [0:`DATA_DEPTH-1];
    reg [`XLEN-1:0] rdata_r;

    // ── Synchronous write + registered read ─────────────────────
    // Read-first: the non-blocking RHS sees the pre-edge contents, so a read
    // concurrent with a write to the same address returns the old word —
    // matching what the combinational read returned before.
    always @(posedge clk) begin
        if (we)
            mem[addr] <= wdata;
        if (re)
            rdata_r <= mem[addr];
    end

    assign rdata = rdata_r;

    // ── Initialize to zero (simulation only) ────────────────────
    // synthesis translate_off
    integer i;
    initial begin
        for (i = 0; i < `DATA_DEPTH; i = i + 1)
            mem[i] = {`XLEN{1'b0}};
    end
    // synthesis translate_on

endmodule
