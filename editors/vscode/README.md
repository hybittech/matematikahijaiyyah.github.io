# HC — Hijaiyyah Codex, for VS Code

Syntax highlighting and a language server for `.hc` files.

## What it gives you

**Highlighting** works on its own, with nothing installed. The grammar is
generated from the lexer's own tables — keywords from `tokens.py`, built-ins
and `hm::` modules from `grammar.py`, letters from the sealed Master Table —
and `tests/test_language/test_vscode_grammar.py` fails if the two drift apart.

Letter literals are checked, not merely coloured. Only the 28 canonical letters
are valid, and the table stores Haa as HEH + TATWEEL (`هـ`), so a bare `ه`
is marked illegal — the same answer the lexer gives.

**The language server** adds live parse errors, hover, and completion across
keywords, built-ins and the whole standard library. It is the `hc` toolchain
speaking LSP over stdio, so diagnostics in the editor are the same diagnostics
`hc check` prints.

## Installing

The extension has no npm dependencies; it can be loaded straight from disk.

```sh
ln -s "$(pwd)/editors/vscode" ~/.vscode/extensions/hc-hijaiyyah
```

Then reload VS Code. For the language server, `hc` must be on PATH:

```sh
pip install -e .
hc --version
```

Without it, highlighting still works and the extension says so once rather
than failing.

## Settings

| Setting | Default | Meaning |
|---|---|---|
| `hc.languageServer.enabled` | `true` | Report parse errors as you type |
| `hc.languageServer.command` | `hc` | Command to run; invoked as `<command> lsp` |

## Scope

Diagnostics cover parse errors — what `hc check` catches. Semantic errors
(an undefined variable, a misspelled stdlib function) surface when the program
runs under `hc run`, not while typing, because the evaluator has no position
information to report them against.
