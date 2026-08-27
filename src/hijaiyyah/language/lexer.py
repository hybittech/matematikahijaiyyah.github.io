"""
HC v1.0 LEXER
==============
Tokenizer for HL-18E / HC v1.0.
Imports token definitions from tokens.py (canonical source).
"""

from __future__ import annotations

from typing import List, Optional

from hijaiyyah.core.constants import H28_SINGLE_CHARS, HAA_FIRST, HAA_SECOND, HAA_SEQUENCE
from hijaiyyah.core.exceptions import LexerError
from hijaiyyah.language.tokens import (
    ESCAPE_MAP,
    KEYWORDS,
    MULTI_CHAR_OPS,
    SINGLE_CHAR_OPS,
    Token,
    TokenType,
)


class Lexer:
    """
    Tokenizer for HC v1.0.
    Converts source code into a list of Token objects.
    """

    def __init__(self, source: str):
        self._src = source
        self._pos = 0
        self._line = 1
        self._col = 1
        self._tokens: List[Token] = []

    @property
    def tokens(self) -> List[Token]:
        if not self._tokens:
            self.tokenize()
        return self._tokens

    def tokenize(self) -> List[Token]:
        self._tokens = []
        self._pos = 0
        self._line = 1
        self._col = 1

        while self._pos < len(self._src):
            self._skip_whitespace()
            if self._pos >= len(self._src):
                break

            ch = self._src[self._pos]

            if ch == "\n":
                self._emit(TokenType.NEWLINE, "\n")
                self._advance()
                self._line += 1
                self._col = 1
                continue

            if ch == "/" and self._peek(1) == "/":
                self._skip_line_comment()
                continue

            if ch == "(" and self._peek(1) == "-" and self._peek(2) == "-":
                self._skip_block_comment()
                continue

            if self._try_multi_char_op():
                continue

            if self._try_single_char_op(ch):
                continue

            if ch == '"':
                self._read_string()
                continue

            if ch == "'":
                self._read_char_literal()
                continue

            if ch.isdigit():
                self._read_number()
                continue

            if self._is_hijaiyyah_start(ch):
                self._read_bare_hijaiyyah()
                continue

            if ch.isalpha() or ch == "_":
                self._read_identifier()
                continue

            self._emit(TokenType.UNKNOWN, ch)
            self._advance()

        self._emit(TokenType.EOF, "")
        return self._tokens

    def _advance(self) -> str:
        ch = self._src[self._pos]
        self._pos += 1
        self._col += 1
        return ch

    def _peek(self, offset: int = 0) -> Optional[str]:
        idx = self._pos + offset
        if idx < len(self._src):
            return self._src[idx]
        return None

    def _remaining(self) -> str:
        return self._src[self._pos :]

    def _emit(self, token_type: TokenType, value: str) -> None:
        self._tokens.append(Token(token_type, value, self._line, self._col))

    def _skip_whitespace(self) -> None:
        while self._pos < len(self._src) and self._src[self._pos] in " \t\r":
            self._advance()

    def _skip_line_comment(self) -> None:
        while self._pos < len(self._src) and self._src[self._pos] != "\n":
            self._pos += 1
            self._col += 1

    def _skip_block_comment(self) -> None:
        self._pos += 3
        self._col += 3
        depth = 1
        while self._pos < len(self._src) and depth > 0:
            if self._src[self._pos] == "-" and self._peek(1) == "-" and self._peek(2) == ")":
                depth -= 1
                self._pos += 3
                self._col += 3
            elif self._src[self._pos] == "(" and self._peek(1) == "-" and self._peek(2) == "-":
                depth += 1
                self._pos += 3
                self._col += 3
            else:
                if self._src[self._pos] == "\n":
                    self._line += 1
                    self._col = 0
                self._pos += 1
                self._col += 1

    def _try_multi_char_op(self) -> bool:
        remaining = self._remaining()
        for op_str, op_type in MULTI_CHAR_OPS:
            if remaining.startswith(op_str):
                self._emit(op_type, op_str)
                self._pos += len(op_str)
                self._col += len(op_str)
                return True
        return False

    def _try_single_char_op(self, ch: str) -> bool:
        if ch in SINGLE_CHAR_OPS:
            self._emit(SINGLE_CHAR_OPS[ch], ch)
            self._advance()
            return True
        return False

    def _read_string(self) -> None:
        start_line = self._line
        start_col = self._col
        self._advance()
        chars: List[str] = []
        while self._pos < len(self._src):
            ch = self._src[self._pos]
            if ch == '"':
                self._advance()
                self._emit(TokenType.STRING_LIT, "".join(chars))
                return
            if ch == "\\":
                self._advance()
                if self._pos >= len(self._src):
                    raise LexerError("Unterminated escape", self._line, self._col)
                esc = self._src[self._pos]
                chars.append(ESCAPE_MAP.get(esc, esc))
                self._advance()
                continue
            if ch == "\n":
                self._line += 1
                self._col = 0
            chars.append(ch)
            self._advance()
        raise LexerError(
            f"Unterminated string (started L{start_line}:{start_col})", self._line, self._col
        )

    def _read_char_literal(self) -> None:
        start_col = self._col
        self._advance()
        if self._pos >= len(self._src):
            raise LexerError("Unterminated char literal", self._line, start_col)
        ch = self._src[self._pos]
        if ch == HAA_FIRST and self._peek(1) == HAA_SECOND:
            if self._peek(2) == "'":
                self._emit(TokenType.HIJAIYYAH, HAA_SEQUENCE)
                self._pos += 3
                self._col += 3
                return
        if ch in H28_SINGLE_CHARS:
            if self._peek(1) == "'":
                self._emit(TokenType.HIJAIYYAH, ch)
                self._pos += 2
                self._col += 2
                return
        raise LexerError(f"Invalid char literal: '{ch}'", self._line, start_col)

    def _is_hijaiyyah_start(self, ch: str) -> bool:
        return ch in H28_SINGLE_CHARS or ch == HAA_FIRST

    def _read_bare_hijaiyyah(self) -> None:
        ch = self._src[self._pos]
        if ch == HAA_FIRST and self._peek(1) == HAA_SECOND:
            self._emit(TokenType.HIJAIYYAH, HAA_SEQUENCE)
            self._pos += 2
            self._col += 2
        elif ch in H28_SINGLE_CHARS:
            self._emit(TokenType.HIJAIYYAH, ch)
            self._advance()

    def _read_number(self) -> None:
        start = self._pos
        while self._pos < len(self._src) and self._src[self._pos].isdigit():
            self._pos += 1
            self._col += 1
        p1 = self._peek(1)
        if (
            self._pos < len(self._src)
            and self._src[self._pos] == "."
            and p1 is not None
            and p1.isdigit()
        ):
            self._pos += 1
            self._col += 1
            while self._pos < len(self._src) and self._src[self._pos].isdigit():
                self._pos += 1
                self._col += 1
            self._emit(TokenType.FLOAT, self._src[start : self._pos])
        else:
            self._emit(TokenType.INTEGER, self._src[start : self._pos])

    def _read_identifier(self) -> None:
        start = self._pos
        while self._pos < len(self._src) and (
            self._src[self._pos].isalnum() or self._src[self._pos] in "_*Θ"
        ):
            self._pos += 1
            self._col += 1
        word = self._src[start : self._pos]
        if word == "_":
            self._emit(TokenType.UNDERSCORE, word)
            return
        if word in KEYWORDS:
            self._emit(KEYWORDS[word], word)
            return
        if word.lower() in KEYWORDS:
            self._emit(KEYWORDS[word.lower()], word)
            return
        self._emit(TokenType.IDENTIFIER, word)


# Convenience function
def tokenize(source: str) -> List[Token]:
    return Lexer(source).tokenize()
