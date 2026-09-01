"""
Rendering HC errors so they point at the source.

The pieces were already there — the lexer and parser both carry line and column
— but nothing assembled them into something a reader can act on. An error that
says only `L1:9: Unexpected token` makes you count characters; one that shows
the line with a caret under it does not.

Semantic errors carry no position at all, so they render without the excerpt
rather than pretending to a precision they do not have.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from ..core.exceptions import HijaiyyahError, LexerError

__all__ = ["format_error", "position_of"]

def position_of(exc: BaseException) -> Optional[Tuple[int, int]]:
    """Extract (line, col) from an HC error, or None if it carries no position."""
    line = getattr(exc, "line", None)
    col = getattr(exc, "col", None)
    if isinstance(line, int) and isinstance(col, int) and line > 0:
        return line, col

    token = getattr(exc, "token", None)
    if token is not None:
        t_line = getattr(token, "line", None)
        t_col = getattr(token, "col", None)
        if isinstance(t_line, int) and isinstance(t_col, int) and t_line > 0:
            return t_line, t_col

    return None


def _headline(exc: BaseException) -> str:
    """The message without the `L1:9: ` prefix the error classes prepend."""
    text = str(exc)
    if isinstance(exc, LexerError) or getattr(exc, "token", None) is not None:
        _, sep, rest = text.partition(": ")
        if sep and text.startswith("L"):
            return rest
    return text


def format_error(
    exc: BaseException,
    source: str,
    filename: str = "<input>",
    *,
    hint: Optional[str] = None,
) -> str:
    """
    Render one error as a caret diagnostic:

        error: Unexpected token in expression (got SEMICOLON ';')
         --> program.hc:1:9
          |
        1 | let x = ;
          |         ^
    """
    kind = "error" if isinstance(exc, HijaiyyahError) else type(exc).__name__
    out: List[str] = [f"{kind}: {_headline(exc)}"]

    pos = position_of(exc)
    if pos is None:
        out.append(f" --> {filename}")
        if hint:
            out.append(f"  help: {hint}")
        return "\n".join(out)

    line_no, col = pos
    out.append(f" --> {filename}:{line_no}:{col}")

    lines = source.splitlines()
    if 1 <= line_no <= len(lines):
        text = lines[line_no - 1].replace("\t", " ")
        width = len(str(line_no))
        blank = " " * width
        out.append(f"{blank} |")
        out.append(f"{line_no} | {text}")
        # Columns are 1-based and may point just past the end of the line.
        caret_at = max(0, min(col, len(text) + 1) - 1)
        out.append(f"{blank} | " + " " * caret_at + "^")

    if hint:
        out.append(f"  help: {hint}")
    return "\n".join(out)
