// ============================================================================
// HCPU Decode Stage — hcpu_decode.v
// Instruction field extraction, register read, control signal generation
// (c) 2026 HMCL — HM-28-v1.2-HC18D
// ============================================================================

`include "hcpu_pkg.vh"

module hcpu_decode (
    input  wire                    clk,
    input  wire                    rst_n,

    // ── Pipeline control ────────────────────────────────────────
    input  wire                    stall,
    input  wire                    flush,

    // ── Input from Fetch ────────────────────────────────────────
    input  wire [`ILEN-1:0]        if_instruction,
    input  wire [`XLEN-1:0]        if_pc,

    // ── Register file read (combinational) ──────────────────────
    output wire [4:0]              gpr_raddr1,     // → regfile
    output wire [4:0]              gpr_raddr2,
    input  wire [`XLEN-1:0]        gpr_rdata1,     // ← regfile
    input  wire [`XLEN-1:0]        gpr_rdata2,
    output wire [3:0]              hreg_raddr1,    // → regfile
    output wire [3:0]              hreg_raddr2,
    input  wire [`HREG_W-1:0]      hreg_rdata1,    // ← regfile
    input  wire [`HREG_W-1:0]      hreg_rdata2,

    // ── Output to Execute (pipeline register) ───────────────────
    output reg  [7:0]              id_opcode,
    output reg  [3:0]              id_dst,
    output reg  [3:0]              id_s1,
    output reg  [3:0]              id_s2,
    output reg  [11:0]             id_imm,
    output reg  [`XLEN-1:0]        id_gpr_s1,     // GPR[S1] value
    output reg  [`XLEN-1:0]        id_gpr_s2,     // GPR[S2] value
    output reg  [`HREG_W-1:0]      id_hreg_s1,    // H-Reg[S1] value
    output reg  [`HREG_W-1:0]      id_hreg_s2,    // H-Reg[S2] value
    output reg  [`XLEN-1:0]        id_pc,         // PC of this instruction

    // ── Decoded control signals ─────────────────────────────────
    output reg                     id_gpr_we,     // Write to GPR
    output reg                     id_hreg_we,    // Write to H-Reg
    output reg                     id_mem_read,   // Load from data RAM
    output reg                     id_mem_write,  // Store to data RAM
    output reg                     id_is_branch,  // Branch instruction
    output reg                     id_is_jump,    // Unconditional jump
    output reg                     id_is_codex,   // Codex H-Reg operation
    output reg                     id_is_halt,    // HALT instruction
    output reg                     id_is_print,   // PRINT instruction
    output reg                     id_is_push,    // Stack push
    output reg                     id_is_pop,     // Stack pop

    // ── Input from Execute for Hazard Detection ──────────────────
    input  wire                    ex_mem_read,   // EX is doing a LOAD
    input  wire                    ex_mem_write,  // EX is doing a STORE
    input  wire [3:0]              ex_dst,        // EX destination
    input  wire [`DATA_ADDR_W-1:0] ex_mem_addr,   // EX computed memory address

    // ── Output to Controller ────────────────────────────────────
    output wire                    load_use_hazard,  // Load-use penalty
    output wire                    store_load_hazard // Store-load address conflict
);

    wire [7:0]  opcode = if_instruction[`OP_MSB:`OP_LSB];
    wire [3:0]  dst    = if_instruction[`DST_MSB:`DST_LSB];
    wire [3:0]  s1     = if_instruction[`S1_MSB:`S1_LSB];
    wire [3:0]  s2     = if_instruction[`S2_MSB:`S2_LSB];
    wire [11:0] imm    = if_instruction[`IMM_MSB:`IMM_LSB];

    // ── Operand Dependency Decode (combinational) ───────────────
    // Two independent case blocks: a single case statement cannot set both
    // id_uses_s1 and id_uses_s2 for the same opcode because Verilog case
    // only executes the first matching branch.
    reg id_uses_s1, id_uses_s2;
    always @(*) begin
        id_uses_s1 = 1'b0;
        id_uses_s2 = 1'b0;

        // S1 usage: instructions that read GPR[S1] or H-Reg[S1]
        case (opcode)
            `OP_MOV, `OP_ADD, `OP_SUB, `OP_MUL, `OP_CMP, `OP_ADDI, `OP_CMPI,
            `OP_LOAD, `OP_STORE, `OP_HCADD, `OP_HGRD, `OP_HNRM2, `OP_HDIST,
            `OP_HPACK, `OP_HCRC,
            `OP_PRINT, `OP_PUSH: id_uses_s1 = 1'b1;
            default: ;
        endcase

        // S2 usage: instructions that read GPR[S2] or H-Reg[S2]
        case (opcode)
            `OP_ADD, `OP_SUB, `OP_MUL, `OP_CMP,
            `OP_STORE, `OP_HCADD, `OP_HDIST: id_uses_s2 = 1'b1;
            default: ;
        endcase
    end

    // ── Load-Use Hazard Detection ───────────────────────────────
    // With BRAM-latency fetch, by the time LOAD reaches EX, the dependent
    // instruction has already entered decode. So we detect the hazard one
    // stage earlier: when LOAD is in the decode pipeline register (id_*)
    // and the current IF instruction (s1/s2) depends on the LOAD's dst.
    //
    // The flush-based stall mechanism then:
    //   1. Freezes fetch (hold IF instruction)
    //   2. Flushes decode (NOP into ID pipeline register)
    //   3. LOAD flows from decode → EX (because decode runs, not stalled)
    //   4. Next cycle: ADD enters decode, LOAD at EX → MEM, no stall
    //   5. ADD enters EX, LOAD at MEM → MEM forwarding supplies result
    assign load_use_hazard = id_mem_read && (id_dst != 0) &&
                             ((id_uses_s1 && (s1 == id_dst)) ||
                              (id_uses_s2 && (s2 == id_dst)));

    // ── Store-to-Load Hazard Detection ───────────────────────────
    // If the EX stage is doing a STORE, and the decoded instruction
    // is a LOAD with the same computed address, stall 1 cycle to
    // ensure the STORE commits before the LOAD reads.
    wire id_is_load_op  = (opcode == `OP_LOAD);
    // Compute the current instruction's load address (S1 + IMM)
    wire [`XLEN-1:0] id_load_addr_raw = gpr_rdata1 + {{20{imm[11]}}, imm};
    wire [`DATA_ADDR_W-1:0] id_load_addr = id_load_addr_raw[`DATA_ADDR_W-1:0];

    assign store_load_hazard = ex_mem_write && id_is_load_op &&
                               (ex_mem_addr == id_load_addr);

    // Drive register file addresses (combinational, before clock)
    assign gpr_raddr1  = {1'b0, s1};
    assign gpr_raddr2  = {1'b0, s2};
    assign hreg_raddr1 = s1;
    assign hreg_raddr2 = s2;

    // ── Pipeline register + control decode ──────────────────────
    always @(posedge clk or negedge rst_n) begin
        // Async reset and synchronous flush clear the same registers, but
        // they must stay in separate branches: `flush` is not in the
        // sensitivity list, so folding it into the async-reset condition
        // makes the block un-inferrable (yosys: "Multiple edge sensitive
        // events found for this signal").
        if (!rst_n) begin
            id_opcode    <= `OP_NOP;
            id_dst       <= 4'd0;
            id_s1        <= 4'd0;
            id_s2        <= 4'd0;
            id_imm       <= 12'd0;
            id_gpr_s1    <= {`XLEN{1'b0}};
            id_gpr_s2    <= {`XLEN{1'b0}};
            id_hreg_s1   <= {`HREG_W{1'b0}};
            id_hreg_s2   <= {`HREG_W{1'b0}};
            id_pc        <= {`XLEN{1'b0}};
            id_gpr_we    <= 1'b0;
            id_hreg_we   <= 1'b0;
            id_mem_read  <= 1'b0;
            id_mem_write <= 1'b0;
            id_is_branch <= 1'b0;
            id_is_jump   <= 1'b0;
            id_is_codex  <= 1'b0;
            id_is_halt   <= 1'b0;
            id_is_print  <= 1'b0;
            id_is_push   <= 1'b0;
            id_is_pop    <= 1'b0;
        end else if (flush) begin
            id_opcode    <= `OP_NOP;
            id_dst       <= 4'd0;
            id_s1        <= 4'd0;
            id_s2        <= 4'd0;
            id_imm       <= 12'd0;
            id_gpr_s1    <= {`XLEN{1'b0}};
            id_gpr_s2    <= {`XLEN{1'b0}};
            id_hreg_s1   <= {`HREG_W{1'b0}};
            id_hreg_s2   <= {`HREG_W{1'b0}};
            id_pc        <= {`XLEN{1'b0}};
            id_gpr_we    <= 1'b0;
            id_hreg_we   <= 1'b0;
            id_mem_read  <= 1'b0;
            id_mem_write <= 1'b0;
            id_is_branch <= 1'b0;
            id_is_jump   <= 1'b0;
            id_is_codex  <= 1'b0;
            id_is_halt   <= 1'b0;
            id_is_print  <= 1'b0;
            id_is_push   <= 1'b0;
            id_is_pop    <= 1'b0;
        end else if (!stall) begin
            // Latch fields
            id_opcode  <= opcode;
            id_dst     <= dst;
            id_s1      <= s1;
            id_s2      <= s2;
            id_imm     <= imm;
            id_gpr_s1  <= gpr_rdata1;
            id_gpr_s2  <= gpr_rdata2;
            id_hreg_s1 <= hreg_rdata1;
            id_hreg_s2 <= hreg_rdata2;
            id_pc      <= if_pc;

            // ── Control signal decode ───────────────────────────
            // Defaults
            id_gpr_we    <= 1'b0;
            id_hreg_we   <= 1'b0;
            id_mem_read  <= 1'b0;
            id_mem_write <= 1'b0;
            id_is_branch <= 1'b0;
            id_is_jump   <= 1'b0;
            id_is_codex  <= 1'b0;
            id_is_halt   <= 1'b0;
            id_is_print  <= 1'b0;
            id_is_push   <= 1'b0;
            id_is_pop    <= 1'b0;

            case (opcode)
                `OP_NOP:    ;  // no-op

                `OP_HALT:   id_is_halt <= 1'b1;

                `OP_MOV:    id_gpr_we <= 1'b1;
                `OP_MOVI:   id_gpr_we <= 1'b1;

                `OP_ADD:    id_gpr_we <= 1'b1;
                `OP_ADDI:   id_gpr_we <= 1'b1;
                `OP_SUB:    id_gpr_we <= 1'b1;
                `OP_MUL:    id_gpr_we <= 1'b1;

                `OP_CMP:    ;  // Only sets flags, no reg write
                `OP_CMPI:   ;

                `OP_JMP:    id_is_jump <= 1'b1;
                `OP_JEQ:    id_is_branch <= 1'b1;
                `OP_JNE:    id_is_branch <= 1'b1;
                `OP_JGD:    id_is_branch <= 1'b1;
                `OP_JNGD:   id_is_branch <= 1'b1;

                `OP_PUSH:   id_is_push <= 1'b1;
                `OP_POP:    begin id_is_pop <= 1'b1; id_gpr_we <= 1'b1; end
                `OP_LOAD:   begin id_mem_read <= 1'b1; id_gpr_we <= 1'b1; end
                `OP_STORE:  begin id_mem_write <= 1'b1; end

                `OP_HLOAD:  begin id_is_codex <= 1'b1; id_hreg_we <= 1'b1; end
                `OP_HCADD:  begin id_is_codex <= 1'b1; id_hreg_we <= 1'b1; end
                `OP_HGRD:   begin id_is_codex <= 1'b1; end  // Sets GUARD flag only
                `OP_HNRM2:  begin id_is_codex <= 1'b1; id_gpr_we <= 1'b1; end
                `OP_HDIST:  begin id_is_codex <= 1'b1; id_gpr_we <= 1'b1; end

                `OP_HPACK:  begin id_is_codex <= 1'b1; id_gpr_we <= 1'b1; end  // HISAB nibble-pack
                `OP_HCRC:   begin id_is_codex <= 1'b1; id_gpr_we <= 1'b1; end  // HISAB CRC32

                `OP_PRINT:  id_is_print <= 1'b1;

                default: begin
                    id_is_halt <= 1'b1;  // Unimplemented → HALT_ERR
                    id_dst     <= 4'hE;  // Arbitrary error code mark
                    id_gpr_we  <= 1'b0;
                    id_hreg_we <= 1'b0;
                    id_mem_write <= 1'b0;
                end
            endcase
        end
        // If stall: hold all outputs unchanged
    end

endmodule
