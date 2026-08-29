#!/usr/bin/env python3
"""
HCVM: Hijaiyyah Codex Virtual Machine — Standalone
Can run independently: python hcvm.py [script.hcvm]
"""

from __future__ import annotations

import os
import sys
from typing import Any, Callable, Dict, List, Optional

# Runtime path setup for standalone execution
# Pyright resolves this via pyrightconfig.json executionEnvironments
_src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

from hijaiyyah.core.guards import compute_U, guard_check  # noqa: E402
from hijaiyyah.core.master_table import MASTER_TABLE  # noqa: E402

# ── Data types ───────────────────────────────────────────────────

H28: List[str] = [e.char for e in MASTER_TABLE.all_entries()]


class Codex:
    """Wrapper for a hybit vector in the HCVM."""

    def __init__(self, v: List[int]) -> None:
        self.v: List[int] = list(v)

    def pretty(self) -> str:
        return f"Codex({self.v})"

    def __repr__(self) -> str:
        return self.pretty()


# ── Utility functions ────────────────────────────────────────────

def encode(ch: str) -> Optional[Codex]:
    """Encode a Hijaiyyah character to a Codex."""
    entry = MASTER_TABLE.get_by_char(ch)
    if entry is not None:
        return Codex(list(entry.vector))
    return None


def seal() -> str:
    """Compute dataset seal (SHA-256)."""
    return MASTER_TABLE.compute_sha256()


# ── Demo scripts ─────────────────────────────────────────────────

DEMOS: Dict[str, str] = {
    "hello": (
        'EMIT("Hello from HCVM!")\n'
        'LET x = COD18("ب")\n'
        'EMIT(x)'
    ),
    "financial": (
        'LET t = AGGREGATE("بسم الله")\n'
        'EMIT("Seal:", t)\n'
        'VERIFY_CHECKSUM(t)'
    ),
}


# ── Lexer / Parser (line-based) ──────────────────────────────────

class Lexer:
    """Simple line-based lexer for HCVM scripts."""

    def __init__(self, src: str) -> None:
        self.tokens: List[str] = src.strip().split("\n")


class Parser:
    """Simple line-based parser for HCVM scripts."""

    def __init__(self, tokens: List[str]) -> None:
        self.lines: List[str] = tokens

    def parse(self) -> List[str]:
        return self.lines


# ── Virtual Machine ──────────────────────────────────────────────

class VM:
    """HCVM virtual machine — executes HCVM script lines."""

    def __init__(self) -> None:
        self.vars: Dict[str, Any] = {}
        self.builtins: Dict[str, Callable[..., None]] = {
            "emit": self._default_emit,
        }

    @staticmethod
    def _default_emit(args: List[Any]) -> None:
        parts: List[str] = []
        for a in args:
            if isinstance(a, Codex):
                parts.append(a.pretty())
            else:
                parts.append(str(a))
        print(" ".join(parts))

    def exec(self, lines: List[str]) -> None:
        """Execute a list of HCVM instruction lines."""
        for raw_line in lines:
            line = raw_line.strip()

            # Skip empty lines and comments
            if not line:
                continue
            if line.startswith("(--") or line.startswith("--"):
                continue

            # EMIT(...)
            if line.startswith("EMIT(") and line.endswith(")"):
                content = line[5:-1]
                self.builtins["emit"]([content])
                continue

            # LET name = expr
            if line.startswith("LET "):
                self._exec_let(line[4:])
                continue

            # VERIFY_CHECKSUM(var)
            if line.startswith("VERIFY_CHECKSUM(") and line.endswith(")"):
                var_name = line[16:-1]
                self._exec_verify_checksum(var_name)
                continue

            # VERIFY_MOD4(var)
            if line.startswith("VERIFY_MOD4(") and line.endswith(")"):
                var_name = line[12:-1]
                self._exec_verify_mod4(var_name)
                continue

            # DECOMPOSE(var)
            if line.startswith("DECOMPOSE(") and line.endswith(")"):
                var_name = line[10:-1]
                self._exec_decompose(var_name)
                continue

    def _exec_let(self, rest: str) -> None:
        """Execute a LET assignment."""
        parts = rest.split("=", 1)
        if len(parts) != 2:
            return

        name = parts[0].strip()
        expr = parts[1].strip()

        if expr.startswith('COD18("') and expr.endswith('")'):
            ch = expr[7:-2]
            entry = MASTER_TABLE.get_by_char(ch)
            if entry is not None:
                self.vars[name] = Codex(list(entry.vector))
            else:
                self.vars[name] = None

        elif expr.startswith('AGGREGATE("') and expr.endswith('")'):
            text = expr[11:-2]
            total = [0] * 18
            for c in text:
                entry = MASTER_TABLE.get_by_char(c)
                if entry is not None:
                    v = list(entry.vector)
                    total = [total[i] + v[i] for i in range(18)]
            self.vars[name] = Codex(total)

        elif expr == "SEAL()":
            self.vars[name] = seal()

        else:
            # Store as raw string
            self.vars[name] = expr

    def _exec_verify_checksum(self, var_name: str) -> None:
        """Execute VERIFY_CHECKSUM on a variable."""
        obj = self.vars.get(var_name)
        if obj is not None and isinstance(obj, Codex):
            ok = guard_check(obj.v)
            self.builtins["emit"]([f"Guard: {'PASS' if ok else 'FAIL'}"])
        else:
            self.builtins["emit"](
                [f"VERIFY_CHECKSUM: variable '{var_name}' not found or not a Codex"]
            )

    def _exec_verify_mod4(self, var_name: str) -> None:
        """Execute VERIFY_MOD4 on a variable."""
        obj = self.vars.get(var_name)
        if obj is not None and isinstance(obj, Codex):
            theta = obj.v[0]
            mod4 = theta % 4
            status = "CLOSED_POSSIBLE" if mod4 == 0 else "OPEN"
            self.builtins["emit"]([f"Mod-4: Θ̂={theta} mod4={mod4} → {status}"])

    def _exec_decompose(self, var_name: str) -> None:
        """Execute DECOMPOSE on a variable."""
        obj = self.vars.get(var_name)
        if obj is not None and isinstance(obj, Codex):
            U = compute_U(obj.v)
            rho = obj.v[0] - U
            self.builtins["emit"]([f"Θ̂={obj.v[0]} U={U} ρ={rho} (ρ≥0: {rho >= 0})"])


# ── Entry point ──────────────────────────────────────────────────

def main() -> None:
    """Entry point for standalone HCVM execution."""
    args = sys.argv
    if len(args) > 1:
        script_path = args[1]
        with open(script_path, encoding="utf-8") as f:
            src = f.read()
    else:
        src = DEMOS["hello"]

    vm = VM()
    lexer = Lexer(src)
    parser = Parser(lexer.tokens)
    instructions = parser.parse()
    vm.exec(instructions)


if __name__ == "__main__":
    main()
