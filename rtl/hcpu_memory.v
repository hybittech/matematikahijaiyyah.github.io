// ============================================================================
// HCPU Memory Stage — hcpu_memory.v
// Stack operations (PUSH/POP) + Data RAM (LOAD/STORE)
// (c) 2026 HMCL — HM-28-v1.2-HC18D / Tier 1.5
// ============================================================================

`include "hcpu_pkg.vh"

module hcpu_memory (
    input  wire                    clk,
    input  wire                    rst_n,

    // ── Pipeline control ────────────────────────────────────────
    input  wire                    stall,

    // ── Input from Execute ──────────────────────────────────────
    input  wire [7:0]              ex_opcode,
    input  wire [3:0]              ex_dst,
    input  wire [`XLEN-1:0]        ex_gpr_result,
    input  wire [`HREG_W-1:0]      ex_hreg_result,
    input  wire                    ex_gpr_we,
    input  wire                    ex_hreg_we,
    input  wire [7:0]              ex_flags_new,
    input  wire                    ex_flags_we,
    input  wire                    ex_is_halt,
    input  wire                    ex_is_push,
    input  wire                    ex_is_pop,
    input  wire [`XLEN-1:0]        ex_push_data,

    // ── Data RAM interface (from execute) ────────────────────────
    input  wire                    ex_mem_read,
    input  wire                    ex_mem_write,
    input  wire [`DATA_ADDR_W-1:0] ex_mem_addr,
    input  wire [`XLEN-1:0]        ex_mem_wdata,

    // ── Data RAM port (directly connected to hcpu_dataram) ──────
    output wire                    dram_re,
    output wire                    dram_we,
    output wire [`DATA_ADDR_W-1:0] dram_addr,
    output wire [`XLEN-1:0]        dram_wdata,
    input  wire [`XLEN-1:0]        dram_rdata,

    // ── Output to Writeback ─────────────────────────────────────
    output reg  [3:0]              mem_dst,
    output wire [`XLEN-1:0]        mem_gpr_result,
    output reg  [`HREG_W-1:0]      mem_hreg_result,
    output reg                     mem_gpr_we,
    output reg                     mem_hreg_we,
    output reg  [7:0]              mem_flags_new,
    output reg                     mem_flags_we,
    output reg                     mem_is_halt
);

    // ── Stack storage ───────────────────────────────────────────
    reg [`XLEN-1:0] stack [0:`STACK_DEPTH-1];
    reg [7:0]       sp;  // Stack pointer (0 = empty)
    reg [`XLEN-1:0] stack_rd;
    reg             stack_rd_valid;

    // ── Data RAM interface ──────────────────────────────────────
    assign dram_re    = ex_mem_read  && !stall;
    assign dram_we    = ex_mem_write && !stall;
    assign dram_addr  = ex_mem_addr;
    assign dram_wdata = ex_mem_wdata;

    // ── HCHECK: Stack fault detection ────────────────────────
    // [HC-02] Stack overflow:  PUSH when sp >= STACK_DEPTH
    // [HC-03] Stack underflow: POP  when sp == 0
    wire stack_overflow  = ex_is_push && (sp >= `STACK_DEPTH);
    wire stack_underflow = ex_is_pop  && (sp == 8'd0);
    wire hcheck_fault    = stack_overflow || stack_underflow;

    // ── Stack pointer ───────────────────────────────────────────
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sp <= 8'd0;
        end else if (!stall && !hcheck_fault) begin
            if (ex_is_push && sp < `STACK_DEPTH)
                sp <= sp + 1;
            if (ex_is_pop && sp > 0)
                sp <= sp - 1;
        end
    end

    // ── Stack array access ──────────────────────────────────────
    // Deliberately in a clock-only block, with no reset. An array touched
    // inside an async-reset block has to be resettable bit by bit, which no
    // memory primitive can do — Yosys reports "Replacing memory \stack with
    // list of registers" and builds 8,392 flip-flops instead. hcpu_dataram
    // maps to block RAM precisely because its array is written the same way.
    //
    // The read register IS this stage's pipeline register for pop data, so
    // the latency is unchanged. The address stays a bare `sp - 1` so it can
    // map to a primitive; the empty-stack case is handled on the output side
    // rather than folded into the address.
    //
    // sp updates on the same edge, and the non-blocking RHS sees its pre-edge
    // value — the same `sp` the combinational read used.
    always @(posedge clk) begin
        if (!stall && !hcheck_fault && ex_is_push && sp < `STACK_DEPTH)
            stack[sp] <= ex_push_data;
        if (!stall)
            stack_rd <= stack[sp - 1];
    end

    // The valid flag is ordinary state, not array contents, so it keeps the
    // async reset and masks the wrapped address when the stack is empty.
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            stack_rd_valid <= 1'b0;
        else if (!stall)
            stack_rd_valid <= (sp > 0);
    end

    wire [`XLEN-1:0] stack_top = stack_rd_valid ? stack_rd : {`XLEN{1'b0}};

    // ── Load result path ────────────────────────────────────────
    // The data RAM registers its own read output, and that register IS this
    // stage's pipeline register for load data — re-registering dram_rdata here
    // would cost an extra cycle for nothing. mem_is_load is captured on the
    // same edge as rdata_r, so the two always describe the same instruction.
    reg [`XLEN-1:0] mem_gpr_result_r;
    reg             mem_is_load;
    reg             mem_is_pop;

    assign mem_gpr_result = mem_is_load ? dram_rdata
                          : mem_is_pop  ? stack_top
                                        : mem_gpr_result_r;

    // ── Pipeline register to Writeback ──────────────────────────
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            mem_dst          <= 4'd0;
            mem_gpr_result_r <= {`XLEN{1'b0}};
            mem_is_load      <= 1'b0;
            mem_is_pop       <= 1'b0;
            mem_hreg_result <= {`HREG_W{1'b0}};
            mem_gpr_we      <= 1'b0;
            mem_hreg_we     <= 1'b0;
            mem_flags_new   <= 8'h00;
            mem_flags_we    <= 1'b0;
            mem_is_halt     <= 1'b0;
        end else if (!stall) begin
            mem_dst         <= ex_dst;
            mem_hreg_result <= ex_hreg_result;
            mem_gpr_we      <= ex_gpr_we;
            mem_hreg_we     <= ex_hreg_we;
            mem_flags_new   <= ex_flags_new;
            mem_flags_we    <= ex_flags_we;
            // HCHECK: fault from stack overflow/underflow → HALT_ERR
            mem_is_halt     <= ex_is_halt || hcheck_fault;

            // Neither LOAD nor POP data is captured here — both arrive from
            // their own memory's output register, selected by mem_is_load and
            // mem_is_pop. Only the ALU result still needs a register.
            mem_is_load      <= ex_mem_read;
            mem_is_pop       <= ex_is_pop;
            mem_gpr_result_r <= ex_gpr_result;
        end
    end

endmodule
