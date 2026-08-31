"""
The VS Code TextMate grammar, against the lexer it describes.

The grammar was generated from the lexer's own tables rather than typed out,
but a generated file still drifts once the source moves. A keyword added to
tokens.py or a function added to a stdlib module would leave the editor
colouring the language it used to be.

The letter pattern gets particular attention. The table stores Haa as HEH plus
TATWEEL, so bare U+0647 is not a valid literal — and a grammar that highlighted
it as one would contradict both the lexer and the hint `hc` prints.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

import pytest

from hijaiyyah.core.constants import H28_ALPHABET
from hijaiyyah.language.grammar import BUILTIN_FUNCTIONS, STDLIB_MODULES
from hijaiyyah.language.lexer import Lexer
from hijaiyyah.language.tokens import KEYWORDS

ROOT = Path(__file__).resolve().parents[2]
VSCODE = ROOT / "editors" / "vscode"
GRAMMAR_PATH = VSCODE / "syntaxes" / "hc.tmLanguage.json"


@pytest.fixture(scope="module")
def grammar() -> Dict[str, Any]:
    return json.loads(GRAMMAR_PATH.read_text(encoding="utf-8"))


def _patterns(grammar: Dict[str, Any], name: str) -> List[Dict[str, Any]]:
    entry = grammar["repository"][name]
    return entry.get("patterns", [entry])


def _all_matches(grammar: Dict[str, Any], name: str) -> str:
    return " ".join(p.get("match", "") for p in _patterns(grammar, name))


# ── The files exist and are well formed ──────────────────────────

def test_extension_files_are_present() -> None:
    for name in (
        "package.json",
        "language-configuration.json",
        "syntaxes/hc.tmLanguage.json",
        "client/extension.js",
    ):
        assert (VSCODE / name).exists(), f"missing {name}"


def test_manifest_points_at_the_files_it_declares(grammar: Dict[str, Any]) -> None:
    manifest = json.loads((VSCODE / "package.json").read_text(encoding="utf-8"))
    contributes = manifest["contributes"]

    (language,) = contributes["languages"]
    assert language["extensions"] == [".hc"]
    assert (VSCODE / language["configuration"]).exists()

    (declared,) = contributes["grammars"]
    assert declared["scopeName"] == grammar["scopeName"]
    assert (VSCODE / declared["path"]).exists()
    assert (VSCODE / manifest["main"]).exists()


def test_manifest_version_matches_the_package() -> None:
    from hijaiyyah.version import __version__

    manifest = json.loads((VSCODE / "package.json").read_text(encoding="utf-8"))
    assert manifest["version"] == __version__


# ── Token tables stay in step with the lexer ─────────────────────

@pytest.mark.parametrize("keyword", sorted(KEYWORDS), ids=sorted(KEYWORDS))
def test_every_keyword_is_highlighted(grammar: Dict[str, Any], keyword: str) -> None:
    assert keyword in _all_matches(grammar, "keywords"), (
        f"'{keyword}' is a keyword in tokens.py but the grammar does not know it"
    )


@pytest.mark.parametrize("name", sorted(BUILTIN_FUNCTIONS), ids=sorted(BUILTIN_FUNCTIONS))
def test_every_builtin_is_highlighted(grammar: Dict[str, Any], name: str) -> None:
    assert name in _all_matches(grammar, "builtins")


@pytest.mark.parametrize(
    "module",
    sorted(m.split("::", 1)[1] for m in STDLIB_MODULES),
    ids=sorted(m.split("::", 1)[1] for m in STDLIB_MODULES),
)
def test_every_stdlib_module_is_highlighted(grammar: Dict[str, Any], module: str) -> None:
    assert module in _all_matches(grammar, "stdlib")


# ── Letter literals ──────────────────────────────────────────────

def _letter_pattern(grammar: Dict[str, Any]) -> re.Pattern[str]:
    return re.compile(_patterns(grammar, "letters")[0]["match"])


@pytest.mark.parametrize("letter", list(H28_ALPHABET), ids=list(H28_ALPHABET))
def test_every_canonical_letter_is_a_valid_literal(
    grammar: Dict[str, Any], letter: str
) -> None:
    assert _letter_pattern(grammar).fullmatch(f"'{letter}'")


@pytest.mark.parametrize("text", ["ه", "Z", "أ", "ة", "", "جج"])
def test_the_grammar_agrees_with_the_lexer_on_rejections(
    grammar: Dict[str, Any], text: str
) -> None:
    """
    Bare ه (U+0647) is the one that matters: the table stores Haa with tatweel,
    so the lexer rejects it, and the grammar must not colour it as valid.
    """
    source = f"'{text}'"
    grammar_accepts = bool(_letter_pattern(grammar).fullmatch(source))

    try:
        Lexer(source).tokenize()
        lexer_accepts = True
    except Exception:
        lexer_accepts = False

    assert grammar_accepts == lexer_accepts, (
        f"{source!r}: grammar says {grammar_accepts}, lexer says {lexer_accepts}"
    )


# ── Comment syntax ───────────────────────────────────────────────

def test_comment_delimiters_match_the_lexer(grammar: Dict[str, Any]) -> None:
    """HC block comments are (-- --), which is unusual enough to get wrong."""
    config = json.loads((VSCODE / "language-configuration.json").read_text(encoding="utf-8"))
    assert config["comments"]["lineComment"] == "//"
    assert config["comments"]["blockComment"] == ["(--", "--)"]

    line, block = _patterns(grammar, "comments")
    assert line["begin"] == "//"
    assert block["begin"] == r"\(--"
    assert block["end"] == r"--\)"
    assert block.get("patterns"), "block comments nest, so the rule must recurse"
