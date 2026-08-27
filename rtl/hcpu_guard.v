// ============================================================================
// HCPU Guard Checker — hcpu_guard.v  (v2.0)
// Hardware implementation of G1–G4 structural guards + T1–T2 topology
// Single-cycle combinational with optional pipeline register
// (c) 2026 HMCL — Hybit Technology
// ============================================================================
//
// Guard checks (from Bab I, Matematika Hijaiyyah):
//   G1: A_N = Na + Nb + Nd
//   G2: A_K = Kp + Kx + Ks + Ka + Kc
//   G3: A_Q = Qp + Qx + Qs + Qa + Qc
//   G4: ρ = Θ̂ − U ≥ 0  where U = Qx + Qs + Qa + 4×Qc
//   T1: Ks > 0  ⇒  Qc ≥ 1
//   T2: Kc > 0  ⇒  Qc ≥ 1
//
// PIPELINE_GUARD parameter:
//   0 = fully combinational (1 cycle, default)
//   1 = registered output   (2 cycles, breaks critical path)
//

`include "hcpu_pkg.vh"

module hcpu_guard #(
    parameter PIPELINE_GUARD = 0  // 0 = combinational, 1 = registered
)(
    input  wire                clk,
    input  wire                rst_n,
    input  wire [`HREG_W-1:0]  vec,         // 144-bit codex vector
    output wire                guard_pass,  // 1 = all guards pass
    output wire                g1_pass,
    output wire                g2_pass,
    output wire                g3_pass,
    output wire                g4_pass,
    output wire                t1_pass,
    output wire                t2_pass
);

    // ── Extract components ──────────────────────────────────────
    wire [7:0] theta = vec[8*`C_THETA +: 8];  // Θ̂
    wire [7:0] na    = vec[8*`C_NA    +: 8];   // Na
    wire [7:0] nb    = vec[8*`C_NB    +: 8];   // Nb
    wire [7:0] nd    = vec[8*`C_ND    +: 8];   // Nd
    wire [7:0] kp    = vec[8*`C_KP    +: 8];   // Kp
    wire [7:0] kx    = vec[8*`C_KX    +: 8];   // Kx
    wire [7:0] ks    = vec[8*`C_KS    +: 8];   // Ks
    wire [7:0] ka    = vec[8*`C_KA    +: 8];   // Ka
    wire [7:0] kc    = vec[8*`C_KC    +: 8];   // Kc
    wire [7:0] qp    = vec[8*`C_QP    +: 8];   // Qp
    wire [7:0] qx    = vec[8*`C_QX    +: 8];   // Qx
    wire [7:0] qs    = vec[8*`C_QS    +: 8];   // Qs
    wire [7:0] qa    = vec[8*`C_QA    +: 8];   // Qa
    wire [7:0] qc    = vec[8*`C_QC    +: 8];   // Qc
    wire [7:0] a_n   = vec[8*`C_AN    +: 8];   // A_N
    wire [7:0] a_k   = vec[8*`C_AK    +: 8];   // A_K
    wire [7:0] a_q   = vec[8*`C_AQ    +: 8];   // A_Q

    // ── G1: A_N = Na + Nb + Nd ──────────────────────────────────
    wire [9:0] sum_n = na + nb + nd;
    // Compare the full 10-bit sum so a carry out of bit 7 cannot alias to a pass.
    wire g1_comb = ({2'b00, a_n} == sum_n);

    // ── G2: A_K = Kp + Kx + Ks + Ka + Kc ───────────────────────
    wire [10:0] sum_k = kp + kx + ks + ka + kc;
    wire g2_comb = ({3'b000, a_k} == sum_k);

    // ── G3: A_Q = Qp + Qx + Qs + Qa + Qc ───────────────────────
    wire [10:0] sum_q = qp + qx + qs + qa + qc;
    wire g3_comb = ({3'b000, a_q} == sum_q);

    // ── G4: ρ = Θ̂ − U ≥ 0 ──────────────────────────────────────
    // U = Qx + Qs + Qa + 4 × Qc
    wire [10:0] u_val = qx + qs + qa + ({qc, 2'b00});  // qc << 2 = 4*qc
    // ρ = Θ̂ − U ≥ 0 ⇔ Θ̂ ≥ U, compared at full width so a wide U cannot alias.
    wire g4_comb = ({3'b000, theta} >= u_val);

    // ── T1: Ks > 0 ⇒ Qc ≥ 1 ────────────────────────────────────
    wire t1_comb = (ks == 8'd0) || (qc >= 8'd1);

    // ── T2: Kc > 0 ⇒ Qc ≥ 1 ────────────────────────────────────
    // No exceptions: Kaf carries Ka=1, Kc=0 in the canonical Master Table,
    // so T2 is vacuously satisfied. (A prior is_kaf override existed only to
    // mask a corrupted ROM entry and was removed once the data was corrected.)
    wire t2_comb = (kc == 8'd0) || (qc >= 8'd1);

    // ── Combined combinational result ───────────────────────────
    wire guard_pass_comb = g1_comb & g2_comb & g3_comb & g4_comb
                         & t1_comb & t2_comb;

    // ── Output: optional pipeline register ──────────────────────
    generate
        if (PIPELINE_GUARD) begin : gen_pipelined
            // Registered output — breaks critical path at cost of 1 cycle latency
            reg g1_r, g2_r, g3_r, g4_r, t1_r, t2_r, guard_r;
            always @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    g1_r    <= 1'b0;
                    g2_r    <= 1'b0;
                    g3_r    <= 1'b0;
                    g4_r    <= 1'b0;
                    t1_r    <= 1'b0;
                    t2_r    <= 1'b0;
                    guard_r <= 1'b0;
                end else begin
                    g1_r    <= g1_comb;
                    g2_r    <= g2_comb;
                    g3_r    <= g3_comb;
                    g4_r    <= g4_comb;
                    t1_r    <= t1_comb;
                    t2_r    <= t2_comb;
                    guard_r <= guard_pass_comb;
                end
            end
            assign g1_pass    = g1_r;
            assign g2_pass    = g2_r;
            assign g3_pass    = g3_r;
            assign g4_pass    = g4_r;
            assign t1_pass    = t1_r;
            assign t2_pass    = t2_r;
            assign guard_pass = guard_r;
        end else begin : gen_combinational
            // Fully combinational — single cycle
            assign g1_pass    = g1_comb;
            assign g2_pass    = g2_comb;
            assign g3_pass    = g3_comb;
            assign g4_pass    = g4_comb;
            assign t1_pass    = t1_comb;
            assign t2_pass    = t2_comb;
            assign guard_pass = guard_pass_comb;
        end
    endgenerate

endmodule
