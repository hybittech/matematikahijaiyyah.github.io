// ============================================================================
// HCPU Execution Parity Harness — tb_parity.v
// (c) 2026 HMCL — HM-28-v1.2-HC18D
// ============================================================================
//
// Runs an arbitrary program on the HCPU and prints the final architectural
// state in a machine-readable form, so tests/test_hisa/test_execution_parity.py
// can diff it against the same program run on the Python HVM.
//
// The encoding is pinned by test_isa_parity.py, but matching opcode numbers say
// nothing about matching behaviour. HLOAD is the cautionary case: both sides
// agreed it was 0x40 and still disagreed about what it did, because the HVM
// indexed the letter table from 0 while the ROM numbers letters from 1. Nothing
// crashed — the program simply computed with the wrong letter.
//
// Usage (driven by the Python test, not by hand):
//   iverilog -g2012 -I rtl -o tb_parity.vvp rtl/tb/tb_parity.v rtl/*.v
//   vvp tb_parity.vvp +PROGRAM=prog.hex +CYCLES=200
//
// Output format, one item per line:
//   HALTED=<0|1>
//   CYCLES=<n>
//   GPR[<i>]=<8 hex digits>
//   HREG[<i>]=<36 hex digits>
//   FLAGS=<2 hex digits>
//

`timescale 1ns / 1ps
`include "hcpu_pkg.vh"

module tb_parity;

    reg clk, rst_n;
    wire uart_tx, halted, guard_led;

    integer i;
    integer cycle_count;
    integer max_cycles;
    // 4096 bits = 512 characters. A 1024-bit register holds only 128, and a
    // pytest tmp_path can exceed that — the path then arrives truncated from
    // the left and $readmemh silently fails, leaving every register unknown.
    reg [4095:0] program_path;

    // ── Instruction memory ──────────────────────────────────────
    // Same BRAM-style registered read the integration testbench uses: address
    // on cycle N, data on N+1, output held while imem_ce is low.
    reg [`ILEN-1:0] imem [0:`CODE_DEPTH-1];
    wire [`CODE_ADDR_W-1:0] imem_addr;
    wire imem_ce;
    reg  [`ILEN-1:0] imem_data_r;
    wire [`ILEN-1:0] imem_data;

    always @(posedge clk)
        if (imem_ce)
            imem_data_r <= imem[imem_addr];
    assign imem_data = imem_data_r;

    // ── DUT ─────────────────────────────────────────────────────
    hcpu_top #(
        .CLK_HZ (50_000_000),
        .BAUD   (5_000_000)
    ) u_dut (
        .clk       (clk),
        .rst_n     (rst_n),
        .imem_addr (imem_addr),
        .imem_ce   (imem_ce),
        .imem_data (imem_data),
        .uart_tx   (uart_tx),
        .halted    (halted),
        .guard_led (guard_led),
        .dbg_gpr_raddr (5'd0),
        .dbg_gpr_rdata (),
        .dbg_flags     ()
    );

    initial clk = 0;
    always #5 clk = ~clk;

    initial begin
        if (!$value$plusargs("PROGRAM=%s", program_path)) begin
            $display("ERROR: +PROGRAM=<hexfile> is required");
            $fatal(1, "no program given");
        end
        if (!$value$plusargs("CYCLES=%d", max_cycles))
            max_cycles = 500;

        // Unwritten words stay NOP so a short program cannot run into garbage.
        for (i = 0; i < `CODE_DEPTH; i = i + 1)
            imem[i] = {`OP_NOP, 24'h000000};

        $readmemh(program_path, imem);

        rst_n = 0;
        repeat (5) @(posedge clk);
        rst_n = 1;

        cycle_count = 0;
        while (!halted && cycle_count < max_cycles) begin
            @(posedge clk);
            cycle_count = cycle_count + 1;
        end

        // Let the final writeback land before sampling.
        repeat (3) @(posedge clk);

        $display("HALTED=%0d", halted ? 1 : 0);
        $display("CYCLES=%0d", cycle_count);

        for (i = 0; i < `GPR_COUNT; i = i + 1)
            $display("GPR[%0d]=%08X", i, u_dut.u_regfile.gpr[i]);

        for (i = 0; i < `HREG_COUNT; i = i + 1)
            $display("HREG[%0d]=%036X", i, u_dut.u_regfile.hreg[i]);

        $display("FLAGS=%02X", u_dut.u_regfile.flags);

        $finish(0);
    end

endmodule
