// ============================================================================
// Testbench: Guard Checker — tb_guard.v
// Verifies G1–G4, T1–T2 for all 28 letters + corruption injection
// (c) 2026 HMCL
// ============================================================================

`timescale 1ns/1ps
`include "hcpu_pkg.vh"

module tb_guard;

    reg  [`HREG_W-1:0] vec;
    wire guard_pass, g1, g2, g3, g4, t1, t2;

    hcpu_guard uut (
        .vec        (vec),
        .guard_pass (guard_pass),
        .g1_pass    (g1),
        .g2_pass    (g2),
        .g3_pass    (g3),
        .g4_pass    (g4),
        .t1_pass    (t1),
        .t2_pass    (t2)
    );

    // ROM for loading valid vectors
    reg  [`ROM_ADDR_W-1:0] rom_addr;
    wire [`HREG_W-1:0]     rom_data;
    wire                   rom_valid;

    hcpu_rom u_rom (
        .addr     (rom_addr),
        .data_out (rom_data),
        .valid    (rom_valid)
    );

    integer pass_count, fail_count;
    integer idx;

    initial begin
        $dumpfile("tb_guard.vcd");
        $dumpvars(0, tb_guard);

        pass_count = 0;
        fail_count = 0;

        $display("=== HCPU Guard Checker Verification ===");

        // ── Test 1: All 28 letters should PASS ──────────────────
        for (idx = 1; idx <= 28; idx = idx + 1) begin
            rom_addr = idx[4:0];
            #1;
            vec = rom_data;
            #1;
            if (guard_pass) begin
                $display("PASS: Letter %0d — all guards pass", idx);
                pass_count = pass_count + 1;
            end else begin
                $display("FAIL: Letter %0d — G1=%b G2=%b G3=%b G4=%b T1=%b T2=%b",
                         idx, g1, g2, g3, g4, t1, t2);
                fail_count = fail_count + 1;
            end
        end

        // ── Test 2: G1 corruption (break A_N) ───────────────────
        // Load Ba (index 2), corrupt A_N component
        rom_addr = 5'd2; #1;
        vec = rom_data;
        vec[8*`C_AN +: 8] = 8'd99;  // A_N should be 1, set to 99
        #1;
        if (!g1) begin
            $display("PASS: G1 correctly detects A_N corruption");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: G1 missed A_N corruption");
            fail_count = fail_count + 1;
        end

        // ── Test 3: G2 corruption (break A_K) ───────────────────
        rom_addr = 5'd2; #1;
        vec = rom_data;
        vec[8*`C_AK +: 8] = 8'd0;  // A_K should be 1, set to 0
        #1;
        if (!g2) begin
            $display("PASS: G2 correctly detects A_K corruption");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: G2 missed A_K corruption");
            fail_count = fail_count + 1;
        end

        // ── Test 4: G3 corruption (break A_Q) ───────────────────
        rom_addr = 5'd2; #1;
        vec = rom_data;
        vec[8*`C_AQ +: 8] = 8'd99;  // A_Q should be 1, set to 99
        #1;
        if (!g3) begin
            $display("PASS: G3 correctly detects A_Q corruption");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: G3 missed A_Q corruption");
            fail_count = fail_count + 1;
        end

        // ── Test 5: G4 corruption (ρ < 0) ──────────────────────
        // Load Haa (Θ̂=8), corrupt Qc to make U > Θ̂
        rom_addr = 5'd27; #1;
        vec = rom_data;
        vec[8*`C_QC +: 8] = 8'd10;  // 4*10=40 >> 8=Θ̂
        #1;
        if (!g4) begin
            $display("PASS: G4 correctly detects rho<0");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: G4 missed rho<0 corruption");
            fail_count = fail_count + 1;
        end

        // ── Test 6: T1 violation (Ks>0 but Qc=0) ───────────────
        vec = {`HREG_W{1'b0}};
        vec[8*`C_KS +: 8] = 8'd1;  // Ks=1
        vec[8*`C_QC +: 8] = 8'd0;  // Qc=0 — violates T1
        #1;
        if (!t1) begin
            $display("PASS: T1 correctly detects Ks>0, Qc=0");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: T1 missed violation");
            fail_count = fail_count + 1;
        end

        // ── Test 7: T2 violation (Kc>0 but Qc=0) ───────────────
        vec = {`HREG_W{1'b0}};
        vec[8*`C_KC +: 8] = 8'd2;  // Kc=2
        vec[8*`C_QC +: 8] = 8'd0;  // Qc=0 — violates T2
        #1;
        if (!t2) begin
            $display("PASS: T2 correctly detects Kc>0, Qc=0");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: T2 missed violation");
            fail_count = fail_count + 1;
        end

        $display("========================================");
        $display("Guard Tests: %0d PASS, %0d FAIL", pass_count, fail_count);
        $display("========================================");

        // $finish(1) sets the diagnostic message level, not the exit status —
        // vvp still returns 0, so a failing run would look green to CI.
        // $fatal is what actually exits non-zero.
        if (fail_count > 0) $fatal(1, "%0d test(s) FAILED", fail_count);
        else $finish(0);
    end

endmodule
