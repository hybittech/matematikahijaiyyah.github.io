// ============================================================================
// Testbench: Master Table ROM — tb_rom.v
// Verifies all 28 letter vectors match hm28.json golden values
// (c) 2026 HMCL
// ============================================================================

`timescale 1ns/1ps
`include "hcpu_pkg.vh"

module tb_rom;

    reg  [`ROM_ADDR_W-1:0] addr;
    wire [`HREG_W-1:0]     data_out;
    wire                   valid;

    hcpu_rom uut (
        .addr     (addr),
        .data_out (data_out),
        .valid    (valid)
    );

    // Extract component from 144-bit vector
    `define COMP(vec, idx) vec[8*(idx) +: 8]

    integer pass_count;
    integer fail_count;
    integer i;

    // Task to check one letter
    task check_letter;
        input [4:0]  index;
        input [7:0]  exp_theta, exp_na, exp_nb, exp_nd;
        input [7:0]  exp_kp, exp_kx, exp_ks, exp_ka, exp_kc;
        input [7:0]  exp_qp, exp_qx, exp_qs, exp_qa, exp_qc;
        input [7:0]  exp_an, exp_ak, exp_aq, exp_psi;
        begin
            addr = index;
            #1;
            if (!valid) begin
                $display("FAIL: Index %0d — invalid address", index);
                fail_count = fail_count + 1;
            end else if (
                `COMP(data_out, 0)  == exp_theta &&
                `COMP(data_out, 1)  == exp_na    &&
                `COMP(data_out, 2)  == exp_nb    &&
                `COMP(data_out, 3)  == exp_nd    &&
                `COMP(data_out, 4)  == exp_kp    &&
                `COMP(data_out, 5)  == exp_kx    &&
                `COMP(data_out, 6)  == exp_ks    &&
                `COMP(data_out, 7)  == exp_ka    &&
                `COMP(data_out, 8)  == exp_kc    &&
                `COMP(data_out, 9)  == exp_qp    &&
                `COMP(data_out, 10) == exp_qx    &&
                `COMP(data_out, 11) == exp_qs    &&
                `COMP(data_out, 12) == exp_qa    &&
                `COMP(data_out, 13) == exp_qc    &&
                `COMP(data_out, 14) == exp_an    &&
                `COMP(data_out, 15) == exp_ak    &&
                `COMP(data_out, 16) == exp_aq    &&
                `COMP(data_out, 17) == exp_psi
            ) begin
                $display("PASS: Index %0d", index);
                pass_count = pass_count + 1;
            end else begin
                $display("FAIL: Index %0d", index);
                $display("  Got:    [%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d]",
                    `COMP(data_out,0), `COMP(data_out,1), `COMP(data_out,2),
                    `COMP(data_out,3), `COMP(data_out,4), `COMP(data_out,5),
                    `COMP(data_out,6), `COMP(data_out,7), `COMP(data_out,8),
                    `COMP(data_out,9), `COMP(data_out,10),`COMP(data_out,11),
                    `COMP(data_out,12),`COMP(data_out,13),`COMP(data_out,14),
                    `COMP(data_out,15),`COMP(data_out,16),`COMP(data_out,17));
                $display("  Expect: [%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d]",
                    exp_theta, exp_na, exp_nb, exp_nd,
                    exp_kp, exp_kx, exp_ks, exp_ka, exp_kc,
                    exp_qp, exp_qx, exp_qs, exp_qa, exp_qc,
                    exp_an, exp_ak, exp_aq, exp_psi);
                fail_count = fail_count + 1;
            end
        end
    endtask

    initial begin
        $dumpfile("tb_rom.vcd");
        $dumpvars(0, tb_rom);

        pass_count = 0;
        fail_count = 0;

        $display("=== HCPU ROM Verification (28 letters) ===");

        //                    idx  Θ  Na Nb Nd Kp Kx Ks Ka Kc Qp Qx Qs Qa Qc AN AK AQ  Ψ
        check_letter( 5'd1,   0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0); // Alif
        check_letter( 5'd2,   2, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0); // Ba
        check_letter( 5'd3,   2, 2, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 2, 1, 1, 0); // Ta
        check_letter( 5'd4,   2, 3, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 3, 1, 1, 0); // Tsa
        check_letter( 5'd5,   3, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0); // Jim
        check_letter( 5'd6,   3, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0); // Ha
        check_letter( 5'd7,   3, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0); // Kha
        check_letter( 5'd8,   1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0); // Dal
        check_letter( 5'd9,   1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0); // Dzal
        check_letter(5'd10,   1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0); // Ra
        check_letter(5'd11,   1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0); // Zay
        check_letter(5'd12,   4, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 3, 0); // Sin
        check_letter(5'd13,   4, 3, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 3, 0, 3, 0); // Syin
        check_letter(5'd14,   6, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 2, 0); // Shad
        check_letter(5'd15,   6, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 2, 0); // Dhad
        check_letter(5'd16,   4, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0); // Tha
        check_letter(5'd17,   4, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0); // Zha
        check_letter(5'd18,   3, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 2, 0); // Ain
        check_letter(5'd19,   3, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 2, 0); // Ghain
        check_letter(5'd20,   5, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 2, 0); // Fa
        check_letter(5'd21,   6, 2, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 2, 0, 2, 0); // Qaf
        check_letter(5'd22,   2, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1); // Kaf
        check_letter(5'd23,   1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0); // Lam
        check_letter(5'd24,   4, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0); // Mim
        check_letter(5'd25,   2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0); // Nun
        check_letter(5'd26,   5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 2, 0); // Waw
        check_letter(5'd27,   8, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 0, 1, 2, 0); // Haa
        check_letter(5'd28,   3, 0, 0, 2, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 2, 0, 2, 0); // Ya

        // Invalid address test
        addr = 5'd0;  #1;
        if (!valid) begin
            $display("PASS: Index 0 — correctly invalid");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: Index 0 should be invalid");
            fail_count = fail_count + 1;
        end

        addr = 5'd29; #1;
        if (!valid) begin
            $display("PASS: Index 29 — correctly invalid");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL: Index 29 should be invalid");
            fail_count = fail_count + 1;
        end

        $display("=====================================");
        $display("ROM Tests: %0d PASS, %0d FAIL", pass_count, fail_count);
        $display("=====================================");

        if (fail_count > 0) $finish(1);
        else $finish(0);
    end

endmodule
