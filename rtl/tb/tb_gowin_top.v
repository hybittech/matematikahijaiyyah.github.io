// ============================================================================
// Tang Nano 9K wrapper testbench — tb_gowin_top.v
// (c) 2026 HMCL
// ============================================================================
//
// Runs the board wrapper exactly as the FPGA would: 27 MHz oscillator, program
// loaded from program.hex, output read off the serial pin. The UART receiver
// below samples uart_txd at the baud the *board* is meant to use, not at
// whatever the design happens to produce — which is the whole point.
//
// The wrapper used to hand hcpu_top CLK_HZ = 50_000_000 while a placeholder
// PLL passed the 27 MHz oscillator straight through. CLKS_PER_BIT was sized
// for a clock that did not exist, putting the line at 62,212 baud against an
// expected 115,200. A receiver tolerates 2-3%; this was 46% out, so nothing
// legible would ever have come out of the port. Simulating the core alone
// could not catch it, because the core was behaving exactly as parameterised.
//
// Expected output for rtl/programs/test_bsm.hasm: "112" — the squared norm of
// Ba + Sin + Mim, matching the Python reference.
//
//   iverilog -g2012 -I rtl -o tb_gowin_top.vvp \
//       rtl/tb/tb_gowin_top.v rtl/fpga/gowin/hcpu_gowin_top.v rtl/*.v
//   vvp tb_gowin_top.vvp
//

`timescale 1ns / 1ps
`include "hcpu_pkg.vh"

module tb_gowin_top;

    // The board's oscillator. 27 MHz is 37.037 ns; the half period is rounded
    // to 18.5 ns, which is close enough that the UART sampling below still
    // lands mid-bit.
    localparam real HALF_PERIOD = 18.5;
    localparam integer OSC_HZ    = 27_000_000;
    localparam integer BAUD      = 115200;
    // One bit time in nanoseconds, at the baud the board expects.
    localparam real BIT_NS       = 1_000_000_000.0 / BAUD;

    reg  clk_27m = 1'b0;
    reg  btn_rst_n = 1'b0;
    wire uart_txd;
    wire [5:0] led;

    always #HALF_PERIOD clk_27m = ~clk_27m;

    hcpu_gowin_top #(
        .USE_PLL (0),
        .BAUD    (BAUD)
    ) u_board (
        .clk_27m   (clk_27m),
        .btn_rst_n (btn_rst_n),
        .uart_txd  (uart_txd),
        .led       (led)
    );

    // ── UART receiver ───────────────────────────────────────────
    // Deliberately independent of the design: it times bits from BIT_NS, so
    // it only decodes correctly if the transmitter really is at 115200.
    reg [7:0] received [0:63];
    integer   count = 0;
    integer   bit_i;
    reg [7:0] shifted;

    initial begin
        forever begin
            @(negedge uart_txd);            // start bit
            #(BIT_NS * 1.5);                // into the middle of bit 0
            for (bit_i = 0; bit_i < 8; bit_i = bit_i + 1) begin
                shifted[bit_i] = uart_txd;
                #BIT_NS;
            end
            if (count < 64) begin
                received[count] = shifted;
                count = count + 1;
            end
        end
    end

    // ── Stimulus and checking ───────────────────────────────────
    integer i;
    integer pass_count = 0;
    integer fail_count = 0;
    reg [8*16-1:0] text;

    task expect_text;
        input [8*16-1:0] want;
        input integer    want_len;
        integer k;
        reg ok;
        begin
            ok = (count >= want_len);
            for (k = 0; ok && k < want_len; k = k + 1)
                if (received[k] !== want[8*(want_len-1-k) +: 8])
                    ok = 1'b0;
            if (ok) begin
                $display("PASS: UART emitted the expected characters");
                pass_count = pass_count + 1;
            end else begin
                $display("FAIL: UART output did not match");
                fail_count = fail_count + 1;
            end
        end
    endtask

    initial begin
        btn_rst_n = 1'b0;
        repeat (10) @(posedge clk_27m);
        btn_rst_n = 1'b1;

        // Long enough for the program to run and shift out four characters at
        // 115200 baud from a 27 MHz clock.
        #(BIT_NS * 10 * 6 + 200_000);

        $display("=======================================");
        $display("Tang Nano 9K wrapper — UART at %0d baud from %0d Hz", BAUD, OSC_HZ);
        $display("=======================================");
        $display("Characters received: %0d", count);
        text = 0;
        for (i = 0; i < count && i < 16; i = i + 1) begin
            $display("  [%0d] 0x%02h '%c'", i, received[i], received[i]);
        end

        // test_bsm.hasm prints the squared norm of Ba + Sin + Mim.
        expect_text({"1", "1", "2"}, 3);

        if (count == 0) begin
            $display("FAIL: nothing came out of the serial pin");
            fail_count = fail_count + 1;
        end

        $display("=======================================");
        $display("Gowin wrapper: %0d PASS, %0d FAIL", pass_count, fail_count);
        $display("=======================================");

        if (fail_count > 0) $fatal(1, "%0d test(s) FAILED", fail_count);
        else $finish(0);
    end

endmodule
