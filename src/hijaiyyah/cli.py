"""
`hc` — the command-line driver for the HC language.

Until now the only way to run a `.hc` program was to import the lexer, parser
and evaluator from Python and wire them together by hand. Every example in the
repository documented a language nobody could actually invoke.

    hc run program.hc     execute a program
    hc check program.hc   parse it and report errors, without running it
    hc repl               interactive session
    hc lsp                language server, over stdin/stdout
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from .core.exceptions import HijaiyyahError
from .language.diagnostics import format_error
from .language.evaluator import HCEvaluator
from .language.lexer import Lexer
from .language.parser import Parser
from .version import __version__

BANNER = f"HC {__version__} — Hijaiyyah Codex language.  :help for commands, :quit to exit."


def _hint_for(exc: BaseException) -> Optional[str]:
    """A short suggestion, where the error class makes one obvious."""
    text = str(exc)
    if "Invalid char literal" in text:
        return (
            "letter literals hold one of the 28 Hijaiyyah letters; "
            "note the table stores Haa as 'هـ' (with tatweel)"
        )
    if "Undefined variable" in text:
        return "declare it first with `let`"
    if "Module member" in text and "not found" in text:
        return (
            "check the spelling; the hm:: modules are vectronometry, "
            "differential, integral, geometry and exomatrix"
        )
    if isinstance(exc, ZeroDivisionError):
        return "guard the divisor before dividing"
    return None


def _report(exc: BaseException, source: str, filename: str) -> None:
    print(format_error(exc, source, filename, hint=_hint_for(exc)), file=sys.stderr)


def _parse(source: str):
    return Parser(Lexer(source).tokenize()).parse()


# ── Commands ─────────────────────────────────────────────────────

def cmd_run(path: Path) -> int:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {path}: {exc.strerror}", file=sys.stderr)
        return 2

    try:
        ast = _parse(source)
    except Exception as exc:  # the lexer and parser raise several types
        _report(exc, source, str(path))
        return 1

    try:
        HCEvaluator().evaluate(ast)
    except (HijaiyyahError, ZeroDivisionError, RecursionError) as exc:
        _report(exc, source, str(path))
        return 1
    return 0


def cmd_check(paths: Sequence[Path]) -> int:
    failures = 0
    for path in paths:
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot read {path}: {exc.strerror}", file=sys.stderr)
            failures += 1
            continue
        try:
            _parse(source)
            print(f"ok   {path}")
        except Exception as exc:  # report whatever the parser raises
            _report(exc, source, str(path))
            failures += 1
    if failures:
        print(f"\n{failures} file(s) failed to parse", file=sys.stderr)
    return 1 if failures else 0


_REPL_HELP = """Commands:
  :help     show this message
  :quit     leave the session (Ctrl-D also works)

A trailing semicolon is optional. State persists between lines, so a `let`
stays in scope for everything after it."""


def cmd_repl(stdin=None, stdout=None) -> int:
    """
    Interactive session. One statement per line; the evaluator is reused, so
    bindings persist.
    """
    inp = stdin or sys.stdin
    out = stdout or sys.stdout
    evaluator = HCEvaluator(print_func=lambda *a: print(*a, file=out))

    interactive = inp.isatty() if hasattr(inp, "isatty") else False
    if interactive:
        print(BANNER, file=out)

    while True:
        if interactive:
            print("hc> ", end="", file=out, flush=True)
        line = inp.readline()
        if not line:  # EOF
            if interactive:
                print(file=out)
            return 0

        text = line.strip()
        if not text or text.startswith("//"):
            continue
        if text in (":quit", ":q", ":exit"):
            return 0
        if text in (":help", ":h", ":?"):
            print(_REPL_HELP, file=out)
            continue

        if not text.endswith(("；", ";", "}")):
            text += ";"

        try:
            evaluator.evaluate(_parse(text))
        except Exception as exc:  # a bad line must not end the session
            print(
                format_error(exc, text, "<repl>", hint=_hint_for(exc)),
                file=sys.stderr,
            )


# ── Entry point ──────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hc",
        description="Run and inspect HC programs.",
    )
    parser.add_argument("--version", action="version", version=f"hc {__version__}")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="execute a .hc program")
    run.add_argument("file", type=Path)

    check = sub.add_parser("check", help="parse without running")
    check.add_argument("files", type=Path, nargs="+")

    sub.add_parser("repl", help="start an interactive session")
    sub.add_parser("lsp", help="run the language server on stdin/stdout")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return cmd_run(args.file)
    if args.command == "check":
        return cmd_check(args.files)
    if args.command == "repl":
        return cmd_repl()
    if args.command == "lsp":
        from .lsp import main as lsp_main

        return lsp_main()

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
