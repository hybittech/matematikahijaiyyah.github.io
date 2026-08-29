// ============================================================================
// HCPU Integration Testbench — tb_hcpu_top.v (Tier 1.5)
// Tests forwarding, Data RAM, and zero-NOP programs
// (c) 2026 HMCL — HM-28-v1.2-HC18D
// ============================================================================

`include "hcpu_pkg.vh"

module tb_hcpu_top;

    reg clk, rst_n;
    wire uart_tx, halted, guard_led;

    // ── Instruction memory (testbench-provided) ─────────────────
    // BRAM-style: registered read with 1-cycle latency + clock enable.
    // The fetch stage (hcpu_fetch.v) expects address on cycle N,
    // data valid on cycle N+1 — matching FPGA BRAM behavior.
    // imem_ce gates the output register: during pipeline stalls,
    // the BRAM holds its output to prevent in-flight data loss.
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
        .CLK_HZ(50_000_000),
        .BAUD(5_000_000)  // Fast baud for simulation
    ) u_dut (
        .clk       (clk),
        .rst_n     (rst_n),
        .imem_addr (imem_addr),
        .imem_ce   (imem_ce),
        .imem_data (imem_data),
        .uart_tx   (uart_tx),
        .halted    (halted),
        .guard_led (guard_led),
        // Debug port — unused in TB (hierarchical access is OK in sim)
        .dbg_gpr_raddr (5'd0),
        .dbg_gpr_rdata (),
        .dbg_flags     ()
    );

    // ── Clock generation (100 MHz) ──────────────────────────────
    initial clk = 0;
    always #5 clk = ~clk;

    // ── Helper function ─────────────────────────────────────────
    function [`ILEN-1:0] enc;
        input [7:0]  op;
        input [3:0]  dst, s1, s2;
        input [11:0] imm;
        enc = {op, dst, s1, s2, imm};
    endfunction

    // ── Waveform dump ───────────────────────────────────────────
    initial begin
        $dumpfile("tb_hcpu_top.vcd");
        $dumpvars(0, tb_hcpu_top);
    end

    // ── Test execution ──────────────────────────────────────────
    integer i;
    integer cycle_count;
    integer pass_count, fail_count;

    initial begin
        pass_count = 0;
        fail_count = 0;

        $display("=== HCPU Integration Test (Tier 1.5 — with Forwarding) ===");

        // ═══════════════════════════════════════════════════════
        //  Program 1: Load + Guard (NO NOPs — forwarding test)
        // ═══════════════════════════════════════════════════════

        for (i = 0; i < `CODE_DEPTH; i = i + 1)
            imem[i] = {`OP_NOP, 24'h000000};

        imem[0] = enc(`OP_HLOAD, 4'd0, 4'd0, 4'd0, 12'd2);   // H0 <- Ba
        imem[1] = enc(`OP_HGRD,  4'd0, 4'd0, 4'd0, 12'd0);   // Guard H0 (uses forwarding!)
        imem[2] = enc(`OP_MOVI,  4'd0, 4'd0, 4'd0, 12'd42);  // R0 <- 42
        imem[3] = enc(`OP_HALT,  4'd0, 4'd0, 4'd0, 12'd0);

        rst_n = 0;
        repeat (5) @(posedge clk);
        rst_n = 1;

        cycle_count = 0;
        while (!halted && cycle_count < 50) begin
            @(posedge clk);
            cycle_count = cycle_count + 1;
        end

        $display("Program 1 halted after %0d cycles", cycle_count);

        if (guard_led) begin
            $display("PASS: Guard LED is ON (Ba passes)");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: Guard LED should be ON");
            fail_count = fail_count + 1;
        end

        if (u_dut.u_regfile.gpr[0] == 32'd42) begin
            $display("PASS: R0 = 42");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: R0 = %0d (expected 42)", u_dut.u_regfile.gpr[0]);
            fail_count = fail_count + 1;
        end

        // ═══════════════════════════════════════════════════════
        //  Program 2: BSM without NOPs (forwarding stress test)
        // ═══════════════════════════════════════════════════════

        for (i = 0; i < `CODE_DEPTH; i = i + 1)
            imem[i] = {`OP_NOP, 24'h000000};

        imem[0] = enc(`OP_HLOAD, 4'd0, 4'd0, 4'd0, 12'd2);   // H0 <- Ba
        imem[1] = enc(`OP_HLOAD, 4'd1, 4'd0, 4'd0, 12'd12);  // H1 <- Sin
        imem[2] = enc(`OP_HCADD, 4'd2, 4'd0, 4'd1, 12'd0);   // H2 <- H0+H1
        imem[3] = enc(`OP_HLOAD, 4'd3, 4'd0, 4'd0, 12'd24);  // H3 <- Mim
        imem[4] = enc(`OP_HCADD, 4'd2, 4'd2, 4'd3, 12'd0);   // H2 <- H2+H3
        imem[5] = enc(`OP_HGRD,  4'd0, 4'd2, 4'd0, 12'd0);   // Guard H2
        imem[6] = enc(`OP_HNRM2, 4'd0, 4'd2, 4'd0, 12'd0);   // R0 <- ||H2||^2
        imem[7] = enc(`OP_HALT,  4'd0, 4'd0, 4'd0, 12'd0);

        rst_n = 0;
        repeat (5) @(posedge clk);
        rst_n = 1;

        cycle_count = 0;
        while (!halted && cycle_count < 50) begin
            @(posedge clk);
            cycle_count = cycle_count + 1;
        end

        $display("\nProgram 2 (BSM no NOPs) halted after %0d cycles", cycle_count);
        $display("H2[Theta] = %0d (expected 10)", u_dut.u_regfile.hreg[2][7:0]);
        $display("Guard LED = %0d (expected 1)", guard_led);
        $display("R0 (||BSM||^2) = %0d (expected 112)", u_dut.u_regfile.gpr[0]);

        if (u_dut.u_regfile.hreg[2][7:0] == 8'd10) begin
            $display("PASS: BSM Theta = 10");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: BSM Theta != 10");
            fail_count = fail_count + 1;
        end

        if (u_dut.u_regfile.gpr[0] == 32'd112) begin
            $display("PASS: ||BSM||^2 = 112");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: ||BSM||^2 = %0d (expected 112)", u_dut.u_regfile.gpr[0]);
            fail_count = fail_count + 1;
        end

        // ═══════════════════════════════════════════════════════
        //  Program 3: Loop (NO NOPs — forwarding test)
        // ═══════════════════════════════════════════════════════

        for (i = 0; i < `CODE_DEPTH; i = i + 1)
            imem[i] = {`OP_NOP, 24'h000000};

        imem[0] = enc(`OP_MOVI,  4'd0, 4'd0, 4'd0, 12'd0);   // R0 <- 0
        imem[1] = enc(`OP_MOVI,  4'd1, 4'd0, 4'd0, 12'd3);   // R1 <- 3
        // loop: (addr 2)
        imem[2] = enc(`OP_ADDI,  4'd0, 4'd0, 4'd0, 12'd1);   // R0++
        imem[3] = enc(`OP_CMP,   4'd0, 4'd0, 4'd1, 12'd0);   // CMP R0, R1
        imem[4] = enc(`OP_JNE,   4'd0, 4'd0, 4'd0, 12'hFFE); // JNE -2 (-> addr 2)
        imem[5] = enc(`OP_HALT,  4'd0, 4'd0, 4'd0, 12'd0);

        rst_n = 0;
        repeat (5) @(posedge clk);
        rst_n = 1;

        cycle_count = 0;
        while (!halted && cycle_count < 100) begin
            @(posedge clk);
            cycle_count = cycle_count + 1;
        end

        $display("\nProgram 3 (loop no NOPs) halted after %0d cycles", cycle_count);

        if (u_dut.u_regfile.gpr[0] == 32'd3) begin
            $display("PASS: R0 = 3 (loop counted correctly)");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: R0 = %0d (expected 3)", u_dut.u_regfile.gpr[0]);
            fail_count = fail_count + 1;
        end

        // ═══════════════════════════════════════════════════════
        //  Program 4: Data RAM STORE + LOAD test
        // ═══════════════════════════════════════════════════════

        for (i = 0; i < `CODE_DEPTH; i = i + 1)
            imem[i] = {`OP_NOP, 24'h000000};

        imem[0] = enc(`OP_MOVI,  4'd1, 4'd0, 4'd0, 12'd99);    // R1 <- 99
        imem[1] = enc(`OP_MOVI,  4'd2, 4'd0, 4'd0, 12'd0);     // R2 <- 0 (base addr)
        imem[2] = enc(`OP_NOP,   4'd0, 4'd0, 4'd0, 12'd0);     // pipeline settle
        imem[3] = enc(`OP_STORE, 4'd0, 4'd1, 4'd2, 12'd0);     // MEM[R2+0] <- R1
        imem[4] = enc(`OP_MOVI,  4'd1, 4'd0, 4'd0, 12'd0);     // R1 <- 0 (clear)
        imem[5] = enc(`OP_NOP,   4'd0, 4'd0, 4'd0, 12'd0);     // pipeline settle
        imem[6] = enc(`OP_LOAD,  4'd3, 4'd2, 4'd0, 12'd0);     // R3 <- MEM[R2+0]
        imem[7] = enc(`OP_NOP,   4'd0, 4'd0, 4'd0, 12'd0);     // Let LOAD finish
        imem[8] = enc(`OP_HALT,  4'd0, 4'd0, 4'd0, 12'd0);

        rst_n = 0;
        repeat (5) @(posedge clk);
        rst_n = 1;

        cycle_count = 0;
        while (!halted && cycle_count < 50) begin
            @(posedge clk);
            cycle_count = cycle_count + 1;
        end

        $display("\nProgram 4 (Data RAM) halted after %0d cycles", cycle_count);

        if (u_dut.u_regfile.gpr[3] == 32'd99) begin
            $display("PASS: R3 = 99 (STORE/LOAD round-trip)");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: R3 = %0d (expected 99)", u_dut.u_regfile.gpr[3]);
            fail_count = fail_count + 1;
        end

        // ═══════════════════════════════════════════════════════
        //  Program 5: Negative Guard Audit (test_negative)
        // ═══════════════════════════════════════════════════════
        for (i = 0; i < `CODE_DEPTH; i = i + 1)
            imem[i] = {`OP_NOP, 24'h000000};

        imem[0] = enc(`OP_HLOAD, 4'd0, 4'd0, 4'd0, 12'd31);  // H0 <- Corrupt index 31
        imem[1] = enc(`OP_HGRD,  4'd0, 4'd0, 4'd0, 12'd0);   // Guard Check
        imem[2] = enc(`OP_JNGD,  4'd0, 4'd0, 4'd0, 12'd2);   // If Failed (Guard=0), jump +2 -> addr 4
        imem[3] = enc(`OP_HALT,  4'd0, 4'd0, 4'd0, 12'd0);   // (Fail case) Halt immediately
        imem[4] = enc(`OP_MOVI,  4'd1, 4'd0, 4'd0, 12'd200); // (Pass case) R1 <- 200
        imem[5] = enc(`OP_HALT,  4'd0, 4'd0, 4'd0, 12'd0);

        rst_n = 0;
        repeat (5) @(posedge clk);
        rst_n = 1;

        cycle_count = 0;
        while (!halted && cycle_count < 50) begin
            @(posedge clk);
            cycle_count = cycle_count + 1;
        end

        $display("\nProgram 5 (Negative Guard) halted after %0d cycles", cycle_count);

        if (u_dut.u_regfile.gpr[1] == 32'd200) begin
            $display("PASS: Guard correctly FAIL-BRANCHED on corrupt vector.");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: Guard did NOT fail-branch! R1 = %0d", u_dut.u_regfile.gpr[1]);
            fail_count = fail_count + 1;
        end

        // ═══════════════════════════════════════════════════════
        //  Program 6: Load-Use Hazard Stall Protection
        // ═══════════════════════════════════════════════════════
        for (i = 0; i < `CODE_DEPTH; i = i + 1)
            imem[i] = {`OP_NOP, 24'h000000};

        imem[0] = enc(`OP_MOVI,  4'd2, 4'd0, 4'd0, 12'd5);     // R2 <- 5 
        imem[1] = enc(`OP_MOVI,  4'd3, 4'd0, 4'd0, 12'd10);    // R3 <- 10 (Mem Base)
        imem[2] = enc(`OP_STORE, 4'd0, 4'd2, 4'd3, 12'd0);     // MEM[10] <- R2 (5)
        imem[3] = enc(`OP_MOVI,  4'd1, 4'd0, 4'd0, 12'd0);     // R1 <- 0 (clear before load)
        imem[4] = enc(`OP_NOP,   4'd0, 4'd0, 4'd0, 12'd0);     // Bubble
        imem[5] = enc(`OP_LOAD,  4'd1, 4'd3, 4'd0, 12'd0);     // R1 <- MEM[10] (5)
        imem[6] = enc(`OP_ADD,   4'd4, 4'd1, 4'd2, 12'd0);     // R4 <- R1 + R2 = 5 + 5 = 10 (DEPENDENCY!)
        imem[7] = enc(`OP_HALT,  4'd0, 4'd0, 4'd0, 12'd0);

        rst_n = 0;
        repeat (5) @(posedge clk);
        rst_n = 1;

        cycle_count = 0;
        while (!halted && cycle_count < 50) begin
            @(posedge clk);
            cycle_count = cycle_count + 1;
        end

        $display("\nProgram 6 (Load-Use Stall) halted after %0d cycles", cycle_count);

        if (u_dut.u_regfile.gpr[4] == 32'd10) begin
            $display("PASS: Load-Use stall resolved correctly! R4 = 10.");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: Load-Use pipeline failed! R4 = %0d (expected 10)", u_dut.u_regfile.gpr[4]);
            fail_count = fail_count + 1;
        end

        // ═══════════════════════════════════════════════════════
        //  Program 7: HISAB HPACK + HCRC (Protocol serialization)
        // ═══════════════════════════════════════════════════════
        for (i = 0; i < `CODE_DEPTH; i = i + 1)
            imem[i] = {`OP_NOP, 24'h000000};

        // Ba = ROM index 2
        // Expected: pack_word0 = 0x00010120, CRC32 = 0x9A3115CC
        imem[0] = enc(`OP_HLOAD, 4'd0, 4'd0, 4'd0, 12'd2);   // H0 <- Ba
        imem[1] = enc(`OP_HPACK, 4'd0, 4'd0, 4'd0, 12'd0);   // R0 <- pack_word0(H0)
        imem[2] = enc(`OP_HCRC,  4'd1, 4'd0, 4'd0, 12'd0);   // R1 <- CRC32(H0)
        imem[3] = enc(`OP_HALT,  4'd0, 4'd0, 4'd0, 12'd0);

        rst_n = 0;
        repeat (5) @(posedge clk);
        rst_n = 1;

        cycle_count = 0;
        while (!halted && cycle_count < 50) begin
            @(posedge clk);
            cycle_count = cycle_count + 1;
        end

        $display("\nProgram 7 (HISAB HPACK+HCRC) halted after %0d cycles", cycle_count);
        $display("R0 (pack_word0) = 0x%08X (expected 0x00010120)", u_dut.u_regfile.gpr[0]);
        $display("R1 (CRC32)      = 0x%08X (expected 0x9A3115CC)", u_dut.u_regfile.gpr[1]);

        if (u_dut.u_regfile.gpr[0] == 32'h00010120) begin
            $display("PASS: HPACK pack_word0 = Ba golden value");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: HPACK pack_word0 mismatch!");
            fail_count = fail_count + 1;
        end

        if (u_dut.u_regfile.gpr[1] == 32'h9A3115CC) begin
            $display("PASS: HCRC CRC32 = Ba golden value");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: HCRC CRC32 mismatch!");
            fail_count = fail_count + 1;
        end

        // ═══════════════════════════════════════════════════════
        $display("\n=============================");
        $display("Total: %0d PASS, %0d FAIL", pass_count, fail_count);
        $display("=============================");
        // $fatal exits non-zero so a failing run reaches the shell and CI.
        if (fail_count > 0) $fatal(1, "*** %0d INTEGRATION TESTS FAILED ***", fail_count);
        $display("=== All integration tests complete ===");
        $finish(0);
    end

endmodule
