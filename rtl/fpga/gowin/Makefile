# ============================================================================
# HCPU on the Tang Nano 9K — open-source Gowin flow
# (c) 2026 HMCL
# ============================================================================
#
# Mirrors rtl/fpga/xilinx/Makefile. Two targets matter:
#
#   make sim        simulate the board wrapper and decode its UART output
#   make bitstream  synthesise, place, route and pack
#
# `sim` needs only Icarus Verilog and runs anywhere. `bitstream` needs the
# open-source Gowin chain:
#
#   brew install yosys                      # or the distro package
#   pip install apycula                     # gowin_pack
#   # nextpnr-himbaechel: build from source, or use a prebuilt oss-cad-suite
#
# The vendor Gowin IDE is the alternative; point it at the same sources.

DEVICE   = GW1NR-LV9QN88PC6/I5
FAMILY   = GW1N-9C
BOARD    = tangnano9k

RTL_DIR  = ../..
TOP      = hcpu_gowin_top
PROGRAM  = $(RTL_DIR)/programs/test_bsm.hasm
PYTHON  ?= python3

SOURCES  = hcpu_gowin_top.v \
           $(RTL_DIR)/hcpu_top.v      $(RTL_DIR)/hcpu_fetch.v   \
           $(RTL_DIR)/hcpu_decode.v   $(RTL_DIR)/hcpu_execute.v \
           $(RTL_DIR)/hcpu_memory.v   $(RTL_DIR)/hcpu_writeback.v \
           $(RTL_DIR)/hcpu_regfile.v  $(RTL_DIR)/hcpu_forward.v \
           $(RTL_DIR)/hcpu_controller.v $(RTL_DIR)/hcpu_rom.v   \
           $(RTL_DIR)/hcpu_guard.v    $(RTL_DIR)/hcpu_codex_alu.v \
           $(RTL_DIR)/hcpu_dataram.v  $(RTL_DIR)/hcpu_uart_tx.v \
           $(RTL_DIR)/hcpu_mul.v      $(RTL_DIR)/hcpu_hisab.v

.PHONY: all sim synth bitstream flash clean

all: sim

# ── Program image ───────────────────────────────────────────────
# Written as plain ASCII. The Xilinx copy of this file was UTF-16, which
# $readmemh refuses outright — the instruction memory stayed uninitialised and
# nothing said so.
program.hex: $(PROGRAM)
	$(PYTHON) $(RTL_DIR)/scripts/asm2hex.py $< > $@

# ── Simulation ──────────────────────────────────────────────────
# Runs the wrapper at the board's real 27 MHz and decodes the serial pin at
# 115200, so a mis-parameterised clock fails here rather than on the desk.
sim: program.hex
	iverilog -g2012 -I $(RTL_DIR) -o tb_gowin_top.vvp \
	    $(RTL_DIR)/tb/tb_gowin_top.v $(SOURCES)
	vvp tb_gowin_top.vvp

# ── Synthesis, place and route, pack ────────────────────────────
synth: program.hex
	yosys -p "read_verilog -I $(RTL_DIR) $(SOURCES); \
	          synth_gowin -top $(TOP) -json $(TOP).json"

$(TOP)_pnr.json: synth
	nextpnr-himbaechel --json $(TOP).json --write $@ \
	    --device $(DEVICE) --vopt cst=hcpu_gowin.cst \
	    --vopt family=$(FAMILY)

bitstream: $(TOP)_pnr.json
	gowin_pack -d $(FAMILY) -o $(TOP).fs $<

flash: bitstream
	openFPGALoader -b $(BOARD) $(TOP).fs

clean:
	rm -f program.hex *.json *.fs *.vvp *.vcd
