"""
The `hc` command line driver.

Before this existed, running a .hc program meant importing Lexer, Parser and
HCEvaluator from Python and wiring them together by hand — so every example in
the repository documented a language nobody could actually invoke.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from hijaiyyah.cli import cmd_check, cmd_repl, cmd_run, main
from hijaiyyah.language.diagnostics import format_error, position_of
from hijaiyyah.language.lexer import Lexer
from hijaiyyah.language.parser import ParseError, Parser

ROOT = Path(__file__).resolve().parents[2]


def _write(tmp_path: Path, name: str, source: str) -> Path:
    path = tmp_path / name
    path.write_text(source, encoding="utf-8")
    return path


# ── hc run ───────────────────────────────────────────────────────

def test_run_executes_a_program(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    prog = _write(tmp_path, "ok.hc", "let h = 'ج';\nprintln(h.theta());\n")
    assert cmd_run(prog) == 0
    assert "3" in capsys.readouterr().out


def test_run_reports_a_syntax_error_and_exits_nonzero(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    prog = _write(tmp_path, "bad.hc", "let a = 1;\nlet b = ;\n")
    assert cmd_run(prog) == 1
    err = capsys.readouterr().err
    assert "error:" in err
    assert "bad.hc:2:9" in err
    assert "^" in err, "the diagnostic should point at the column"


def test_run_reports_a_semantic_error(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    prog = _write(tmp_path, "undef.hc", "println(tidak_ada);\n")
    assert cmd_run(prog) == 1
    err = capsys.readouterr().err
    assert "Undefined variable" in err
    assert "help:" in err


def test_run_on_a_missing_file_is_a_clean_error(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    assert cmd_run(tmp_path / "nope.hc") == 2
    assert "cannot read" in capsys.readouterr().err


# ── hc check ─────────────────────────────────────────────────────

def test_check_accepts_every_example_in_the_repo(
    capsys: pytest.CaptureFixture,
) -> None:
    examples = sorted((ROOT / "examples").glob("*.hc")) + sorted(
        (ROOT / "docs" / "examples").glob("*.hc")
    )
    assert len(examples) >= 10
    assert cmd_check(examples) == 0
    assert capsys.readouterr().out.count("ok ") == len(examples)


def test_check_does_not_execute(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """A parse-only pass must not run the program's side effects."""
    prog = _write(tmp_path, "loud.hc", 'println("SHOULD NOT APPEAR");\n')
    assert cmd_check([prog]) == 0
    assert "SHOULD NOT APPEAR" not in capsys.readouterr().out


def test_check_counts_failures(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    good = _write(tmp_path, "good.hc", 'println("hi");\n')
    bad = _write(tmp_path, "bad.hc", "let x = ;\n")
    assert cmd_check([good, bad]) == 1
    assert "1 file(s) failed" in capsys.readouterr().err


# ── hc repl ──────────────────────────────────────────────────────

def _repl(script: str) -> str:
    out = io.StringIO()
    assert cmd_repl(stdin=io.StringIO(script), stdout=out) == 0
    return out.getvalue()


def test_repl_evaluates_and_keeps_state() -> None:
    output = _repl("let h = 'ج';\nprintln(h.theta());\nprintln(h.norm2());\n")
    assert "3" in output
    assert "12" in output


def test_repl_makes_the_semicolon_optional() -> None:
    assert "7" in _repl("println(3 + 4)\n")


def test_repl_survives_a_bad_line(capsys: pytest.CaptureFixture) -> None:
    """One mistake must not end the session."""
    output = _repl("println(rusak);\nprintln(1 + 1);\n")
    assert "2" in output
    assert "Undefined variable" in capsys.readouterr().err


def test_repl_quits_on_command() -> None:
    output = _repl(':quit\nprintln("unreachable");\n')
    assert "unreachable" not in output


def test_repl_ignores_blank_lines_and_comments() -> None:
    assert "5" in _repl('\n// a comment\nprintln(5);\n')


# ── Diagnostics ──────────────────────────────────────────────────

def test_diagnostic_points_at_the_offending_column() -> None:
    source = "let a = 1;\nlet b = ;\n"
    with pytest.raises(ParseError) as excinfo:
        Parser(Lexer(source).tokenize()).parse()

    rendered = format_error(excinfo.value, source, "demo.hc")
    lines = rendered.splitlines()

    assert lines[0].startswith("error: ")
    assert lines[1] == " --> demo.hc:2:9"
    assert lines[3] == "2 | let b = ;"
    # The caret must sit under column 9, and the gutters must line up.
    assert lines[4].index("^") == lines[3].index(";")
    assert lines[2].index("|") == lines[3].index("|") == lines[4].index("|")


def test_diagnostic_survives_a_position_past_end_of_line() -> None:
    """A column one past the last character must not raise while rendering."""
    err = ParseError("boom", None)
    err.line, err.col = 1, 999
    assert "boom" in format_error(err, "x;\n", "demo.hc")


def test_position_of_returns_none_without_a_position() -> None:
    assert position_of(ValueError("no position here")) is None


# ── argv wiring ──────────────────────────────────────────────────

def test_main_dispatches_run(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    prog = _write(tmp_path, "m.hc", 'println("via main");\n')
    assert main(["run", str(prog)]) == 0
    assert "via main" in capsys.readouterr().out


def test_main_without_a_command_prints_help(capsys: pytest.CaptureFixture) -> None:
    assert main([]) == 0
    assert "usage" in capsys.readouterr().out.lower()
