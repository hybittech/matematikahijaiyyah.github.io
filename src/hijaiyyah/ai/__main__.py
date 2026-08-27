"""Command-line entry point for ``python -m hijaiyyah.ai``."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runtime import HybitAIProgram, OllamaClient, run_program


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local Hybit AI program")
    parser.add_argument("program", type=Path, help="Path to a .hcai program")
    parser.add_argument("--ollama", default="http://127.0.0.1:11434")
    args = parser.parse_args()
    program = HybitAIProgram.parse(args.program.read_text(encoding="utf-8"))
    result = run_program(program, OllamaClient(args.ollama))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()