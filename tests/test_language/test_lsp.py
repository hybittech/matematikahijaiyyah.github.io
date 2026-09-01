"""
The HC language server.

docs/hc_language.md §19.3 listed LSP under v2.0. It arrived early because the
hard parts existed already: the lexer and parser carry line and column, and
diagnostics.py knows how to read a position off an error. The server is the
thin layer that speaks the protocol, so these tests concentrate on the wire
format and on positions — the places a hand-written server gets things wrong.
"""

from __future__ import annotations

import io
import json
from typing import Any, Dict, List

from hijaiyyah.lsp import Server


def frame(message: Dict[str, Any]) -> str:
    body = json.dumps(message)
    return f"Content-Length: {len(body.encode('utf-8'))}\r\n\r\n{body}"


def run_session(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Feed a whole session in and decode everything the server writes back."""
    out = io.StringIO()
    Server(stdin=io.StringIO("".join(frame(m) for m in messages)), stdout=out).serve()

    raw = out.getvalue()
    decoded: List[Dict[str, Any]] = []
    cursor = 0
    while cursor < len(raw):
        split = raw.index("\r\n\r\n", cursor)
        length = int(raw[cursor:split].split(":", 1)[1])
        body = raw[split + 4 : split + 4 + length]
        decoded.append(json.loads(body))
        cursor = split + 4 + length
    return decoded


def did_open(uri: str, text: str) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "method": "textDocument/didOpen",
        "params": {"textDocument": {"uri": uri, "text": text}},
    }


def diagnostics_from(replies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        r["params"]["diagnostics"]
        for r in replies
        if r.get("method") == "textDocument/publishDiagnostics"
    ]


# ── Handshake ────────────────────────────────────────────────────

def test_initialize_advertises_its_capabilities() -> None:
    replies = run_session([{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}])
    caps = replies[0]["result"]["capabilities"]
    assert caps["textDocumentSync"] == 1
    assert caps["hoverProvider"] is True
    assert "completionProvider" in caps


def test_every_request_gets_a_reply() -> None:
    """An unanswered request leaves the editor waiting forever."""
    replies = run_session(
        [{"jsonrpc": "2.0", "id": 7, "method": "textDocument/somethingUnsupported"}]
    )
    assert [r for r in replies if r.get("id") == 7]


def test_notifications_get_no_reply() -> None:
    replies = run_session([{"jsonrpc": "2.0", "method": "initialized", "params": {}}])
    assert replies == []


# ── Diagnostics ──────────────────────────────────────────────────

def test_clean_document_reports_no_diagnostics() -> None:
    replies = run_session([did_open("file:///ok.hc", "let h = 'ج';\nprintln(h.theta());\n")])
    assert diagnostics_from(replies) == [[]]


def test_syntax_error_is_reported_at_a_zero_based_position() -> None:
    """
    LSP positions are 0-based; the parser's are 1-based. Getting this wrong
    puts the squiggle one line and one column off, which is the classic
    hand-written-server bug.
    """
    replies = run_session([did_open("file:///bad.hc", "let a = 1;\nlet b = ;\n")])
    (items,) = diagnostics_from(replies)

    assert len(items) == 1
    start = items[0]["range"]["start"]
    assert start["line"] == 1, "parser line 2 must become LSP line 1"
    assert start["character"] == 8, "parser column 9 must become LSP character 8"
    assert items[0]["severity"] == 1
    assert items[0]["source"] == "hc"


def test_an_invalid_letter_is_reported() -> None:
    replies = run_session([did_open("file:///l.hc", "let h = 'Z';\n")])
    (items,) = diagnostics_from(replies)
    assert len(items) == 1
    assert "char literal" in items[0]["message"]


def test_editing_republishes_diagnostics() -> None:
    replies = run_session(
        [
            did_open("file:///e.hc", "let b = ;\n"),
            {
                "jsonrpc": "2.0",
                "method": "textDocument/didChange",
                "params": {
                    "textDocument": {"uri": "file:///e.hc"},
                    "contentChanges": [{"text": "let b = 1;\n"}],
                },
            },
        ]
    )
    published = diagnostics_from(replies)
    assert len(published[0]) == 1, "the broken version should report an error"
    assert published[1] == [], "the fixed version should clear it"


def test_diagnostics_never_raise() -> None:
    """Whatever the buffer holds mid-keystroke, the server must keep serving."""
    server = Server()
    for source in ["", "let", "'", "((((", "}", "let x = ", "\x00", "fn"]:
        assert isinstance(server.diagnostics_for(source), list)


# ── Hover ────────────────────────────────────────────────────────

def test_hover_over_a_keyword() -> None:
    replies = run_session(
        [
            did_open("file:///h.hc", "let x = 1;\n"),
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "textDocument/hover",
                "params": {
                    "textDocument": {"uri": "file:///h.hc"},
                    "position": {"line": 0, "character": 1},
                },
            },
        ]
    )
    hover = next(r for r in replies if r.get("id") == 2)["result"]
    assert "keyword" in hover["contents"]["value"]


def test_hover_over_a_stdlib_function() -> None:
    server = Server()
    assert "hm::geometry::manhattan" in (server.hover_for("manhattan") or "")


def test_hover_over_nothing_returns_null() -> None:
    replies = run_session(
        [
            did_open("file:///n.hc", "let qqq = 1;\n"),
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "textDocument/hover",
                "params": {
                    "textDocument": {"uri": "file:///n.hc"},
                    "position": {"line": 0, "character": 5},
                },
            },
        ]
    )
    assert next(r for r in replies if r.get("id") == 3)["result"] is None


def test_word_at_handles_positions_off_the_end() -> None:
    server = Server()
    assert server.word_at("let x = 1;", 0, 4) == "x"
    assert server.word_at("let x = 1;", 99, 0) == ""
    assert server.word_at("let x = 1;", 0, 999) == ""
    assert server.word_at("", 0, 0) == ""


# ── Completion ───────────────────────────────────────────────────

def test_completion_covers_keywords_builtins_and_the_stdlib() -> None:
    labels = {item["label"] for item in Server().completions()}

    assert "let" in labels and "for" in labels
    assert "println" in labels and "load_id" in labels
    assert "hm::geometry" in labels
    assert "hm::geometry::manhattan" in labels
    assert "hm::exomatrix::audit" in labels


def test_completion_offers_every_stdlib_function() -> None:
    """The advertised surface and what the editor offers must be the same set."""
    from hijaiyyah.language.grammar import STDLIB_MODULES

    labels = {item["label"] for item in Server().completions()}
    for module, functions in STDLIB_MODULES.items():
        for name in functions:
            assert f"{module}::{name}" in labels, f"{module}::{name} missing"
