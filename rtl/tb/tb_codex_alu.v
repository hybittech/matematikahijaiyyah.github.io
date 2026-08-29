// ============================================================================
// Testbench: Codex ALU — tb_codex_alu.v
// Verifies HCADD, HNRM2, HDIST operations
// (c) 2026 HMCL
// ============================================================================

`timescale 1ns/1ps
`include "hcpu_pkg.vh"

module tb_codex_alu;

    reg  [2:0]          op;
    reg  [`HREG_W-1:0]  src1, src2;
    wire [`HREG_W-1:0]  result_vec;
    wire [`XLEN-1:0]    result_scl;
    wire                done;

    hcpu_codex_alu uut (
        .op         (op),
        .src1       (src1),
        .src2       (src2),
        .result_vec (result_vec),
        .result_scl (result_scl),
        .done       (done)
    );

    // ROM for test vectors
    reg  [`ROM_ADDR_W-1:0] rom_addr;
    wire [`HREG_W-1:0]     rom_data;
    wire                   rom_valid;

    hcpu_rom u_rom (
        .addr     (rom_addr),
        .data_out (rom_data),
        .valid    (rom_valid)
    );

    `define COMP(vec, idx) vec[8*(idx) +: 8]

    integer pass_count, fail_count;
    reg [`HREG_W-1:0] vec_ba, vec_sin, vec_mim;
    reg [`HREG_W-1:0] vec_ha, vec_kha, vec_dal, vec_ra;
    reg [`HREG_W-1:0] vec_alif, vec_haa;

    initial begin
        $dumpfile("tb_codex_alu.vcd");
        $dumpvars(0, tb_codex_alu);

        pass_count = 0;
        fail_count = 0;

        // Load test vectors from ROM
        rom_addr = 5'd1;  #1; vec_alif = rom_data;
        rom_addr = 5'd2;  #1; vec_ba   = rom_data;
        rom_addr = 5'd6;  #1; vec_ha   = rom_data;
        rom_addr = 5'd7;  #1; vec_kha  = rom_data;
        rom_addr = 5'd8;  #1; vec_dal  = rom_data;
        rom_addr = 5'd10; #1; vec_ra   = rom_data;
        rom_addr = 5'd12; #1; vec_sin  = rom_data;
        rom_addr = 5'd24; #1; vec_mim  = rom_data;
        rom_addr = 5'd27; #1; vec_haa  = rom_data;

        $display("=== HCPU Codex ALU Verification ===");

        // ── Test 1: HCADD Ba + Sin ─────────────────────────────
        // Ba: [2,0,0,1,0,1,0,0,0,1,0,0,0,0,1,1,1,0]
        // Sin: [4,0,0,0,0,0,0,0,0,1,2,0,0,0,0,0,3,0]
        // Sum: [6,0,0,1,0,1,0,0,0,2,2,0,0,0,1,1,4,0]
        op = 3'd0;  // HCADD
        src1 = vec_ba;
        src2 = vec_sin;
        #1;
        if (`COMP(result_vec, 0) == 8'd6 &&  // Θ̂
            `COMP(result_vec, 3) == 8'd1 &&  // Nd
            `COMP(result_vec, 9) == 8'd2 &&  // Qp
            `COMP(result_vec,10) == 8'd2 &&  // Qx
            `COMP(result_vec,16) == 8'd4) begin // A_Q
            $display("PASS: HCADD Ba+Sin correct");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: HCADD Ba+Sin");
            $display("  Theta=%0d Nd=%0d Qp=%0d Qx=%0d AQ=%0d",
                `COMP(result_vec,0), `COMP(result_vec,3),
                `COMP(result_vec,9), `COMP(result_vec,10),
                `COMP(result_vec,16));
            fail_count = fail_count + 1;
        end

        // ── Test 2: HCADD Ba + Sin + Mim (string بسم) ──────────
        src1 = result_vec;  // Ba+Sin
        src2 = vec_mim;
        // Mim: [4,0,0,0,0,0,0,0,1,0,0,0,0,1,0,1,1,0]
        // Expected: [10,0,0,1,0,1,0,0,1,2,2,0,0,1,1,2,5,0]
        #1;
        if (`COMP(result_vec, 0) == 8'd10 &&  // Θ̂
            `COMP(result_vec, 8) == 8'd1  &&  // Kc
            `COMP(result_vec,13) == 8'd1  &&  // Qc
            `COMP(result_vec,16) == 8'd5) begin // A_Q
            $display("PASS: HCADD BSM (بسم) correct");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: HCADD BSM");
            fail_count = fail_count + 1;
        end

        // ── Test 3: HNRM2 (Dal) ────────────────────────────────
        // Dal: [1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0]
        // ‖v₁₄‖² = 1² + 1² = 2
        op = 3'd1;  // HNRM2
        src1 = vec_dal;
        #1;
        if (result_scl == 32'd2) begin
            $display("PASS: HNRM2 Dal = 2");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: HNRM2 Dal = %0d (expected 2)", result_scl);
            fail_count = fail_count + 1;
        end

        // ── Test 4: HNRM2 (Haa) ────────────────────────────────
        // Haa: [8,0,0,0,0,0,0,0,1,0,0,0,0,2,0,1,2,0]
        // ‖v₁₄‖² = 64+1+4 = 69
        op = 3'd1;
        src1 = vec_haa;
        #1;
        if (result_scl == 32'd69) begin
            $display("PASS: HNRM2 Haa = 69");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: HNRM2 Haa = %0d (expected 69)", result_scl);
            fail_count = fail_count + 1;
        end

        // ── Test 5: HDIST (Ha, Kha) = 1 ────────────────────────
        // Ha: [3,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,1,0]
        // Kha: [3,1,0,0,0,1,0,0,0,1,0,0,0,0,1,1,1,0]
        // Diff in Na only: (0-1)²=1, AN: (0-1)²=1 but only 14D!
        // 14D components (0..13): only diff at index 1 (Na): (0-1)²=1
        op = 3'd2;  // HDIST
        src1 = vec_ha;
        src2 = vec_kha;
        #1;
        if (result_scl == 32'd1) begin
            $display("PASS: HDIST Ha-Kha = 1 (nearest neighbor)");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: HDIST Ha-Kha = %0d (expected 1)", result_scl);
            fail_count = fail_count + 1;
        end

        // ── Test 6: HDIST (Dal, Ra) = 1 ─────────────────────────
        // Dal: [1,0,0,0,0,0,0,0,0,0,0,0,1,0,...]
        // Ra:  [1,0,0,0,0,0,0,0,0,0,0,1,0,0,...]
        // Diff at Qs(11): (0-1)²=1, Qa(12): (1-0)²=1 → total=2
        op = 3'd2;
        src1 = vec_dal;
        src2 = vec_ra;
        #1;
        if (result_scl == 32'd2) begin
            $display("PASS: HDIST Dal-Ra = 2");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: HDIST Dal-Ra = %0d (expected 2)", result_scl);
            fail_count = fail_count + 1;
        end

        $display("=======================================");
        $display("Codex ALU Tests: %0d PASS, %0d FAIL", pass_count, fail_count);
        $display("=======================================");

        // $finish(1) sets the diagnostic message level, not the exit status —
        // vvp still returns 0, so a failing run would look green to CI.
        // $fatal is what actually exits non-zero.
        if (fail_count > 0) $fatal(1, "%0d test(s) FAILED", fail_count);
        else $finish(0);
    end

endmodule
