"""
A Language Server Protocol server for HC.

docs/hc_language.md §19.3 lists LSP under v2.0. It arrives early because the
hard parts were already built: the lexer and parser carry line and column, and
diagnostics.py knows how to turn an error into a position. The server is the
thin layer that speaks the protocol.

Deliberately hand-written over JSON-RPC rather than built on pygls. The
capability set is small — diagnostics, hover, completion — and this project
keeps its dependency list to what the mathematics needs.

Run as `hc lsp`. It speaks over stdin/stdout, so nothing is printed to stdout
except protocol messages; logs go to stderr.

Supported:
  textDocument/publishDiagnostics   parse errors, as you type
  textDocument/hover                what a stdlib function or builtin does
  textDocument/completion           keywords, builtins, hm:: modules
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional, TextIO

from .core.exceptions import HijaiyyahError
from .language.diagnostics import position_of
from .language.grammar import BUILTIN_FUNCTIONS, STDLIB_MODULES
from .language.lexer import Lexer
from .language.parser import Parser
from .language.tokens import KEYWORDS

# LSP severities
ERROR = 1

# Completion item kinds
KIND_KEYWORD = 14
KIND_FUNCTION = 3
KIND_MODULE = 9


def _module_names() -> List[str]:
    return [name.split("::", 1)[1] for name in STDLIB_MODULES]


def _functions_of(module: str) -> List[str]:
    declared = STDLIB_MODULES.get(f"hm::{module}", [])
    return list(declared)


def _builtin_names() -> List[str]:
    return list(BUILTIN_FUNCTIONS)


class Server:
    """Minimal LSP server. One document store, no incremental sync."""

    def __init__(self, stdin: Optional[TextIO] = None, stdout: Optional[TextIO] = None):
        self._in = stdin if stdin is not None else sys.stdin
        self._out = stdout if stdout is not None else sys.stdout
        self._documents: Dict[str, str] = {}
        self._shutdown = False

    # ── Wire format ──────────────────────────────────────────────

    def _read_message(self) -> Optional[Dict[str, Any]]:
        """Read one framed JSON-RPC message, or None at end of stream."""
        length = 0
        while True:
            line = self._in.readline()
            if not line:
                return None
            line = line.strip()
            if not line:  # blank line ends the header block
                break
            if line.lower().startswith("content-length:"):
                length = int(line.split(":", 1)[1].strip())
        if length <= 0:
            return None
        return json.loads(self._in.read(length))

    def _send(self, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload)
        self._out.write(f"Content-Length: {len(body.encode('utf-8'))}\r\n\r\n{body}")
        self._out.flush()

    def _respond(self, request_id: Any, result: Any) -> None:
        self._send({"jsonrpc": "2.0", "id": request_id, "result": result})

    def _notify(self, method: str, params: Any) -> None:
        self._send({"jsonrpc": "2.0", "method": method, "params": params})

    # ── Analysis ─────────────────────────────────────────────────

    def diagnostics_for(self, source: str) -> List[Dict[str, Any]]:
        """Parse errors as LSP diagnostics. LSP positions are 0-based."""
        try:
            Parser(Lexer(source).tokenize()).parse()
        except HijaiyyahError as exc:
            pos = position_of(exc)
            line, col = (pos[0] - 1, pos[1] - 1) if pos else (0, 0)
            line = max(line, 0)
            col = max(col, 0)
            return [
                {
                    "range": {
                        "start": {"line": line, "character": col},
                        "end": {"line": line, "character": col + 1},
                    },
                    "severity": ERROR,
                    "source": "hc",
                    "message": str(exc),
                }
            ]
        except Exception as exc:  # a crash must not take the editor with it
            return [
                {
                    "range": {
                        "start": {"line": 0, "character": 0},
                        "end": {"line": 0, "character": 1},
                    },
                    "severity": ERROR,
                    "source": "hc",
                    "message": f"internal error: {exc}",
                }
            ]
        return []

    def _publish(self, uri: str) -> None:
        source = self._documents.get(uri, "")
        self._notify(
            "textDocument/publishDiagnostics",
            {"uri": uri, "diagnostics": self.diagnostics_for(source)},
        )

    def completions(self) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = [
            {"label": kw, "kind": KIND_KEYWORD} for kw in sorted(KEYWORDS)
        ]
        items += [
            {"label": name, "kind": KIND_FUNCTION, "detail": "builtin"}
            for name in sorted(_builtin_names())
        ]
        for module in _module_names():
            items.append(
                {"label": f"hm::{module}", "kind": KIND_MODULE, "detail": "stdlib module"}
            )
            items += [
                {
                    "label": f"hm::{module}::{fn}",
                    "kind": KIND_FUNCTION,
                    "detail": f"hm::{module}",
                }
                for fn in sorted(_functions_of(module))
            ]
        return items

    def hover_for(self, word: str) -> Optional[str]:
        if word in KEYWORDS:
            return f"**{word}** — HC keyword"
        if word in _builtin_names():
            return f"**{word}(…)** — built-in function"
        for module in _module_names():
            if word in _functions_of(module):
                return f"**hm::{module}::{word}(…)** — standard library"
            if word == module:
                fns = ", ".join(sorted(_functions_of(module)))
                return f"**hm::{module}** — standard library module\n\n{fns}"
        return None

    @staticmethod
    def word_at(source: str, line: int, character: int) -> str:
        """The identifier under a 0-based (line, character) position."""
        lines = source.splitlines()
        if not 0 <= line < len(lines):
            return ""
        text = lines[line]
        if not 0 <= character <= len(text):
            return ""
        start = character
        while start > 0 and (text[start - 1].isalnum() or text[start - 1] == "_"):
            start -= 1
        end = character
        while end < len(text) and (text[end].isalnum() or text[end] == "_"):
            end += 1
        return text[start:end]

    # ── Dispatch ─────────────────────────────────────────────────

    def handle(self, message: Dict[str, Any]) -> None:
        method = message.get("method")
        params = message.get("params") or {}
        request_id = message.get("id")

        if method == "initialize":
            self._respond(
                request_id,
                {
                    "capabilities": {
                        # 1 = full document sync; the parser is fast enough that
                        # incremental updates would buy nothing.
                        "textDocumentSync": 1,
                        "hoverProvider": True,
                        "completionProvider": {"triggerCharacters": [":", "."]},
                    },
                    "serverInfo": {"name": "hc-lsp"},
                },
            )
            return

        if method == "initialized":
            return

        if method == "shutdown":
            self._shutdown = True
            self._respond(request_id, None)
            return

        if method == "textDocument/didOpen":
            doc = params.get("textDocument", {})
            self._documents[doc.get("uri", "")] = doc.get("text", "")
            self._publish(doc.get("uri", ""))
            return

        if method == "textDocument/didChange":
            uri = params.get("textDocument", {}).get("uri", "")
            changes = params.get("contentChanges") or []
            if changes:
                self._documents[uri] = changes[-1].get("text", "")
            self._publish(uri)
            return

        if method == "textDocument/didSave":
            self._publish(params.get("textDocument", {}).get("uri", ""))
            return

        if method == "textDocument/didClose":
            self._documents.pop(params.get("textDocument", {}).get("uri", ""), None)
            return

        if method == "textDocument/hover":
            uri = params.get("textDocument", {}).get("uri", "")
            position = params.get("position", {})
            word = self.word_at(
                self._documents.get(uri, ""),
                position.get("line", 0),
                position.get("character", 0),
            )
            markdown = self.hover_for(word) if word else None
            self._respond(
                request_id,
                {"contents": {"kind": "markdown", "value": markdown}} if markdown else None,
            )
            return

        if method == "textDocument/completion":
            self._respond(request_id, {"isIncomplete": False, "items": self.completions()})
            return

        # Any other request still needs an answer, or the client waits forever.
        if request_id is not None:
            self._respond(request_id, None)

    def serve(self) -> int:
        while True:
            message = self._read_message()
            if message is None:
                return 0
            try:
                self.handle(message)
            except Exception as exc:  # never let one bad message end the session
                print(f"hc-lsp: {exc}", file=sys.stderr)
            if self._shutdown and message.get("method") == "exit":
                return 0
        return 0


def main() -> int:
    return Server().serve()


if __name__ == "__main__":
    sys.exit(main())
