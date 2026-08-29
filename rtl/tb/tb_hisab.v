// ============================================================================
// HCPU HISAB Testbench — tb_hisab.v
// Standalone verification of nibble-packing + CRC32 for all 28 letters
// (c) 2026 HMCL — HM-28-v1.2-HC18D
// ============================================================================
//
// Test strategy:
//   1. Load each of the 28 letters from ROM
//   2. Feed the 144-bit H-Reg vector into hcpu_hisab
//   3. Verify nibble-packing: byte 0 = {v[0][3:0], v[1][3:0]}
//   4. Verify guard_status matches hcpu_guard output
//   5. Verify CRC32 against Python-generated golden values (Ba, Alif, Ya)
//

`include "hcpu_pkg.vh"

module tb_hisab;

    // ── DUT signals ─────────────────────────────────────────────
    reg  [1:0]            op;
    reg  [`HREG_W-1:0]    vec_in;
    reg  [`XLEN-1:0]      gpr_s1, gpr_s2;
    reg  [7:0]            extra_byte;

    wire [`XLEN-1:0]      pack_word0, pack_word1, pack_word2;
    wire [7:0]            guard_status;
    wire [`XLEN-1:0]      crc_out;
    wire                  done;

    hcpu_hisab u_hisab (
        .op          (op),
        .vec_in      (vec_in),
        .gpr_s1      (gpr_s1),
        .gpr_s2      (gpr_s2),
        .extra_byte  (extra_byte),
        .pack_word0  (pack_word0),
        .pack_word1  (pack_word1),
        .pack_word2  (pack_word2),
        .guard_status(guard_status),
        .crc_out     (crc_out),
        .done        (done)
    );

    // ── ROM for letter vectors ──────────────────────────────────
    reg  [`ROM_ADDR_W-1:0] rom_addr;
    wire [`HREG_W-1:0]     rom_data;
    wire                   rom_valid;

    hcpu_rom u_rom (
        .addr     (rom_addr),
        .data_out (rom_data),
        .valid    (rom_valid)
    );

    // ── Guard checker (for cross-validation) ────────────────────
    wire guard_pass_ref;
    wire g1_ref, g2_ref, g3_ref, g4_ref, t1_ref, t2_ref;

    hcpu_guard #(.PIPELINE_GUARD(0)) u_guard_ref (
        .clk        (1'b0),
        .rst_n      (1'b1),
        .vec        (vec_in),
        .guard_pass (guard_pass_ref),
        .g1_pass    (g1_ref),
        .g2_pass    (g2_ref),
        .g3_pass    (g3_ref),
        .g4_pass    (g4_ref),
        .t1_pass    (t1_ref),
        .t2_pass    (t2_ref)
    );

    // ── Python-generated golden CRC32 values ────────────────────
    // From gen_golden.py — cross-validated with Python zlib.crc32
    localparam ALIF_PACK0 = 32'h00100000;
    localparam ALIF_PACK1 = 32'h01000000;
    localparam ALIF_PACK2 = 32'h00003F00;
    localparam ALIF_CRC32 = 32'hEFBE516E;

    localparam BA_PACK0   = 32'h00010120;
    localparam BA_PACK1   = 32'h11000001;
    localparam BA_PACK2   = 32'h00003F10;
    localparam BA_CRC32   = 32'h9A3115CC;

    localparam YA_PACK0   = 32'h00000230;
    localparam YA_PACK1   = 32'h20001001;
    localparam YA_PACK2   = 32'h00003F20;
    localparam YA_CRC32   = 32'hD2B786A9;

    // ── Waveform dump ───────────────────────────────────────────
    initial begin
        $dumpfile("tb_hisab.vcd");
        $dumpvars(0, tb_hisab);
    end

    // ── Test execution ──────────────────────────────────────────
    integer i;
    integer pass_count, fail_count;
    reg [7:0] expected_guard_ref;

    initial begin
        pass_count = 0;
        fail_count = 0;
        op         = 2'd0;  // HPACK mode
        gpr_s1     = 32'd0;
        gpr_s2     = 32'd0;
        extra_byte = 8'd0;

        $display("=== HISAB Standalone Testbench ===");
        $display("Testing all 28 letters: nibble-pack + guard + CRC32\n");

        // ── Test all 28 letters ─────────────────────────────────
        for (i = 1; i <= 28; i = i + 1) begin
            rom_addr = i[`ROM_ADDR_W-1:0];
            #1;  // Combinational settle

            vec_in = rom_data;
            #1;  // HISAB combinational settle

            // Build expected guard from reference checker
            expected_guard_ref = {2'b00, t2_ref, t1_ref, g4_ref, g3_ref, g2_ref, g1_ref};

            // Test 1: Nibble packing structural check
            // Byte 0 should be {vec[0][3:0], vec[1][3:0]}
            if (pack_word0[7:0] == {vec_in[3:0], vec_in[11:8]}) begin
                pass_count = pass_count + 1;
            end else begin
                $display("FAIL [ROM %0d]: pack byte0 = 0x%02X, expected 0x%02X",
                         i, pack_word0[7:0], {vec_in[3:0], vec_in[11:8]});
                fail_count = fail_count + 1;
            end

            // Test 2: Guard status matches reference guard checker
            if (guard_status == expected_guard_ref) begin
                pass_count = pass_count + 1;
            end else begin
                $display("FAIL [ROM %0d]: guard_status = 0x%02X, expected 0x%02X",
                         i, guard_status, expected_guard_ref);
                fail_count = fail_count + 1;
            end

            // Test 3: CRC32 is non-zero (structural sanity)
            if (crc_out != 32'd0) begin
                pass_count = pass_count + 1;
            end else begin
                $display("FAIL [ROM %0d]: CRC32 = 0 (should never be zero for valid frame)",
                         i);
                fail_count = fail_count + 1;
            end

            // Test 4: done signal is always 1 (single-cycle)
            if (done) begin
                pass_count = pass_count + 1;
            end else begin
                $display("FAIL [ROM %0d]: done signal not asserted", i);
                fail_count = fail_count + 1;
            end
        end

        $display("--- 28-letter sweep: %0d PASS, %0d FAIL ---\n",
                 pass_count, fail_count);

        // ── Golden value tests: Alif (ROM index 1) ──────────────
        $display("=== Golden CRC32 Cross-Validation ===\n");

        rom_addr = 5'd1;
        #1;
        vec_in = rom_data;
        #1;

        $display("Alif: pack0=0x%08X (exp 0x%08X)", pack_word0, ALIF_PACK0);
        $display("      pack1=0x%08X (exp 0x%08X)", pack_word1, ALIF_PACK1);
        $display("      pack2=0x%08X (exp 0x%08X)", pack_word2, ALIF_PACK2);
        $display("      CRC32=0x%08X (exp 0x%08X)", crc_out, ALIF_CRC32);

        if (pack_word0 == ALIF_PACK0) begin
            $display("  PASS: Alif pack_word0"); pass_count = pass_count + 1;
        end else begin
            $display("  FAIL: Alif pack_word0"); fail_count = fail_count + 1;
        end
        if (pack_word1 == ALIF_PACK1) begin
            $display("  PASS: Alif pack_word1"); pass_count = pass_count + 1;
        end else begin
            $display("  FAIL: Alif pack_word1"); fail_count = fail_count + 1;
        end
        if (pack_word2 == ALIF_PACK2) begin
            $display("  PASS: Alif pack_word2"); pass_count = pass_count + 1;
        end else begin
            $display("  FAIL: Alif pack_word2"); fail_count = fail_count + 1;
        end
        if (crc_out == ALIF_CRC32) begin
            $display("  PASS: Alif CRC32"); pass_count = pass_count + 1;
        end else begin
            $display("  FAIL: Alif CRC32"); fail_count = fail_count + 1;
        end

        // ── Golden value tests: Ba (ROM index 2) ────────────────
        rom_addr = 5'd2;
        #1;
        vec_in = rom_data;
        #1;

        $display("\nBa:   pack0=0x%08X (exp 0x%08X)", pack_word0, BA_PACK0);
        $display("      pack1=0x%08X (exp 0x%08X)", pack_word1, BA_PACK1);
        $display("      pack2=0x%08X (exp 0x%08X)", pack_word2, BA_PACK2);
        $display("      CRC32=0x%08X (exp 0x%08X)", crc_out, BA_CRC32);

        if (pack_word0 == BA_PACK0) begin
            $display("  PASS: Ba pack_word0"); pass_count = pass_count + 1;
        end else begin
            $display("  FAIL: Ba pack_word0"); fail_count = fail_count + 1;
        end
        if (pack_word1 == BA_PACK1) begin
            $display("  PASS: Ba pack_word1"); pass_count = pass_count + 1;
        end else begin
            $display("  FAIL: Ba pack_word1"); fail_count = fail_count + 1;
        end
        if (pack_word2 == BA_PACK2) begin
            $display("  PASS: Ba pack_word2"); pass_count = pass_count + 1;
        end else begin
            $display("  FAIL: Ba pack_word2"); fail_count = fail_count + 1;
        end
        if (crc_out == BA_CRC32) begin
            $display("  PASS: Ba CRC32"); pass_count = pass_count + 1;
        end else begin
            $display("  FAIL: Ba CRC32"); fail_count = fail_count + 1;
        end

        // ── Golden value tests: Ya (ROM index 28) ───────────────
        rom_addr = 5'd28;
        #1;
        vec_in = rom_data;
        #1;

        $display("\nYa:   pack0=0x%08X (exp 0x%08X)", pack_word0, YA_PACK0);
        $display("      pack1=0x%08X (exp 0x%08X)", pack_word1, YA_PACK1);
        $display("      pack2=0x%08X (exp 0x%08X)", pack_word2, YA_PACK2);
        $display("      CRC32=0x%08X (exp 0x%08X)", crc_out, YA_CRC32);

        if (pack_word0 == YA_PACK0) begin
            $display("  PASS: Ya pack_word0"); pass_count = pass_count + 1;
        end else begin
            $display("  FAIL: Ya pack_word0"); fail_count = fail_count + 1;
        end
        if (pack_word1 == YA_PACK1) begin
            $display("  PASS: Ya pack_word1"); pass_count = pass_count + 1;
        end else begin
            $display("  FAIL: Ya pack_word1"); fail_count = fail_count + 1;
        end
        if (pack_word2 == YA_PACK2) begin
            $display("  PASS: Ya pack_word2"); pass_count = pass_count + 1;
        end else begin
            $display("  FAIL: Ya pack_word2"); fail_count = fail_count + 1;
        end
        if (crc_out == YA_CRC32) begin
            $display("  PASS: Ya CRC32"); pass_count = pass_count + 1;
        end else begin
            $display("  FAIL: Ya CRC32"); fail_count = fail_count + 1;
        end

        // ── Summary ─────────────────────────────────────────────
        $display("\n=============================");
        $display("HISAB Total: %0d PASS, %0d FAIL", pass_count, fail_count);
        $display("=============================");

        if (fail_count == 0) begin
            $display("=== ALL HISAB TESTS PASSED ===");
            $finish(0);
        end else begin
            // $fatal exits non-zero so a failing run reaches the shell and CI.
            $fatal(1, "*** %0d HISAB TESTS FAILED ***", fail_count);
        end
    end

endmodule
