"""Tests for HCC — HC Compiler (facade)."""

from hijaiyyah.compiler import (
    CompileOptions,
    CompileResult,
    CompileStage,
    HCCompiler,
    compile_hc,
)


class TestHCCompilerImport:
    """Verify facade imports work."""

    def test_import_compiler(self):
        assert HCCompiler is not None

    def test_import_result(self):
        assert CompileResult is not None

    def test_import_options(self):
        assert CompileOptions is not None

    def test_import_stages(self):
        assert len(CompileStage) == 6

    def test_import_convenience(self):
        assert callable(compile_hc)


class TestHCCompilerInit:
    """Test compiler initialization."""

    def test_default_init(self):
        hcc = HCCompiler()
        assert hcc.VERSION == "1.0.0"
        assert hcc.options is not None

    def test_custom_options(self):
        opts = CompileOptions(emit_asm=True, guard_strict=True)
        hcc = HCCompiler(opts)
        assert hcc.options.emit_asm is True
        assert hcc.options.guard_strict is True

    def test_available_stages(self):
        hcc = HCCompiler()
        stages = hcc.available_stages
        assert isinstance(stages, dict)
        assert "lexer" in stages
        assert "parser" in stages
        assert "codegen" in stages


class TestCompileResult:
    """Test CompileResult dataclass."""

    def test_success_result(self):
        r = CompileResult(success=True, output_format="hbc")
        assert r.success is True
        assert r.failed is False

    def test_failed_result(self):
        r = CompileResult(success=False, errors=["syntax error"])
        assert r.failed is True
        assert len(r.errors) == 1

    def test_stages_tracked(self):
        r = CompileResult(success=True)
        r.stages_completed.append(CompileStage.LEXER)
        r.stages_completed.append(CompileStage.PARSER)
        assert len(r.stages_completed) == 2


class TestCompileOptions:
    """Test CompileOptions dataclass."""

    def test_defaults(self):
        o = CompileOptions()
        assert o.emit_asm is False
        assert o.psi_mode is False
        assert o.guard_strict is False
        assert o.har_path is None
        assert o.debug is False

    def test_psi_mode(self):
        o = CompileOptions(psi_mode=True, har_path="/path/har")
        assert o.psi_mode is True


class TestCompileSource:
    """Test source compilation."""

    def test_compile_empty(self):
        result = compile_hc("")
        assert isinstance(result, CompileResult)

    def test_compile_file_not_found(self):
        hcc = HCCompiler()
        result = hcc.compile_file("/nonexistent/file.hc")
        assert result.failed
        assert "not found" in result.errors[0].lower()

    def test_compile_stages_enum(self):
        assert CompileStage.LEXER.value == 1
        assert CompileStage.ASSEMBLE.value == 6
