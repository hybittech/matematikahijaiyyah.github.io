"""
HCC — HC Compiler
==================
Facade module: .hc → .hasm/.hbc

Pipeline 6-tahap:
  1. Lexer      (from language/)
  2. Parser     (from language/)
  3. Semantic   (from hisa/compiler)
  4. Ψ-Injector (optional)
  5. Codegen    (from hisa/compiler)
  6. Assembler  (inline, from hisa/assembler)

This package re-exports from language/ and hisa/compiler
to present the unified HCC interface described in Bab III §3.28.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, ClassVar, Dict, List, Optional

# ── Re-export from language/ ──────────────────────────────────

try:
    from hijaiyyah.language.lexer import Lexer as HCLexer
except ImportError:
    HCLexer = None

try:
    from hijaiyyah.language.parser import Parser as HCParser
except ImportError:
    HCParser = None

# ── Re-export from hisa/compiler ──────────────────────────────

# hisa.compiler holds HL18ECompiler, itself a placeholder whose compile()
# returns []; there has never been a HISACompiler to delegate to, and wiring
# the one that exists would gain nothing. Code generation is genuinely not
# implemented, and compile_source now says so instead of reporting success
# over an empty result.
#
# hisa.assembler exports assemble() as a function rather than a class, and
# _assemble below calls it directly.


# ── Public types ──────────────────────────────────────────────

class CompileStage(Enum):
    LEXER = auto()
    PARSER = auto()
    SEMANTIC = auto()
    PSI_INJECT = auto()
    CODEGEN = auto()
    ASSEMBLE = auto()


@dataclass
class CompileResult:
    """Result of an HCC compilation."""
    success: bool
    output_format: str = ""          # "hasm" | "hbc"
    output_path: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stages_completed: List[CompileStage] = field(default_factory=list)
    token_count: int = 0
    instruction_count: int = 0

    @property
    def failed(self) -> bool:
        return not self.success


@dataclass
class CompileOptions:
    """Options for HCC compilation."""
    emit_asm: bool = False           # --emit-asm: stop at .hasm
    psi_mode: bool = False           # --psi: enable Ψ-injection
    guard_strict: bool = False       # --guard-strict: flag bit 2
    har_path: Optional[str] = None   # --har: path to HAR directory
    debug: bool = False              # --debug: include debug info
    output_path: Optional[str] = None


# ── HCC Compiler class ───────────────────────────────────────

class HCCompiler:
    """
    HC Compiler — .hc → .hbc (or .hc → .hasm → .hbc)

    Wraps language/lexer, language/parser, hisa/compiler,
    and hisa/assembler into the 6-stage pipeline defined
    in Bab III §3.28.
    """

    VERSION = "1.0.0"
    STAGES: ClassVar[list[CompileStage]] = list(CompileStage)

    def __init__(self, options: Optional[CompileOptions] = None):
        self.options = options or CompileOptions()
        self._lexer_cls = HCLexer
        self._parser_cls = HCParser

    # ── Public API ────────────────────────────────────────

    def compile_source(self, source: str) -> CompileResult:
        """Compile HC source string through the full pipeline."""
        result = CompileResult(success=True)
        try:
            # Stage 1: Lex
            tokens = self._lex(source)
            result.stages_completed.append(CompileStage.LEXER)
            result.token_count = len(tokens) if tokens else 0

            # Stage 2: Parse
            ast = self._parse(tokens)
            result.stages_completed.append(CompileStage.PARSER)

            # Stage 3: Semantic analysis
            typed_ast = self._analyze(ast)
            result.stages_completed.append(CompileStage.SEMANTIC)

            # Stage 4: Ψ-injection (optional)
            if self.options.psi_mode:
                typed_ast = self._psi_inject(typed_ast)
            result.stages_completed.append(CompileStage.PSI_INJECT)

            # Stage 5: Codegen → assembly
            asm_text = self._codegen(typed_ast)
            result.stages_completed.append(CompileStage.CODEGEN)

            # Code generation is not implemented, so this is where the pipeline
            # actually stops. Reporting success over an empty result told
            # callers the source had compiled when nothing had been produced.
            if not asm_text.strip():
                result.success = False
                result.errors.append(
                    "code generation is not implemented — the front end "
                    "(lexer, parser) runs, but no H-ISA assembly is emitted. "
                    "Use hijaiyyah.assembler to assemble .hasm directly."
                )
                return result

            if self.options.emit_asm:
                result.output_format = "hasm"
                return result

            # Stage 6: Assemble → bytecode
            bytecode = self._assemble(asm_text)
            result.stages_completed.append(CompileStage.ASSEMBLE)
            result.output_format = "hbc"
            # Each instruction is a 32-bit word; len(bytecode) is bytes.
            result.instruction_count = len(bytecode) // 4 if bytecode else 0

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def compile_file(self, path: str,
                     output: Optional[str] = None) -> CompileResult:
        """Compile an .hc file."""
        if not os.path.isfile(path):
            return CompileResult(
                success=False,
                errors=[f"File not found: {path}"]
            )
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        result = self.compile_source(source)
        if output:
            result.output_path = output
        return result

    @property
    def available_stages(self) -> Dict[str, bool]:
        """Check which pipeline stages are available."""
        return {
            "lexer": self._lexer_cls is not None,
            "parser": self._parser_cls is not None,
            # Semantic analysis is a pass-through and code generation is not
            # implemented; only the assembler is real.
            "semantic": False,
            "psi_inject": self.options.psi_mode,
            "codegen": False,
            "assembler": True,
        }

    # ── Internal stages ───────────────────────────────────

    def _lex(self, source: str):
        if self._lexer_cls is None:
            raise RuntimeError("HCLexer not available — "
                               "install hijaiyyah.language")
        lexer = self._lexer_cls(source)
        return lexer.tokenize()

    def _parse(self, tokens):
        if self._parser_cls is None:
            raise RuntimeError("HCParser not available")
        return self._parser_cls(tokens).parse()

    def _analyze(self, ast):
        """Semantic analysis — not implemented; the AST passes through."""
        return ast

    def _psi_inject(self, ast):
        """Ψ-Injection: attach hybit metadata to tokens."""
        # Ψ-injection does NOT change semantics
        return ast

    def _codegen(self, ast):
        """
        Generate H-ISA assembly from the AST.

        Not implemented. It returns nothing rather than pretending, and
        compile_source refuses to report success on an empty result.
        """
        return ""

    def _assemble(self, asm_text: str) -> bytes:
        """Assemble H-ISA text into bytecode, one 32-bit word per instruction."""
        if not asm_text.strip():
            return b""
        from ..hisa.assembler import assemble

        return b"".join(word.to_bytes(4, "big") for word in assemble(asm_text))


# ── Module-level convenience ──────────────────────────────────

def compile_hc(source: str, **kwargs) -> CompileResult:
    """Convenience: compile HC source with default options."""
    opts = CompileOptions(**kwargs)
    return HCCompiler(opts).compile_source(source)


__all__ = [
    "CompileOptions",
    "CompileResult",
    "CompileStage",
    "HCCompiler",
    "HCLexer",
    "HCParser",
    "compile_hc",
]
