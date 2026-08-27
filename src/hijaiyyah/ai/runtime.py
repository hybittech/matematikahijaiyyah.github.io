"""Run small HC-style programs against a local Ollama model."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field

from ..core.guards import guard_check
from ..core.master_table import MASTER_TABLE


@dataclass
class HybitAIProgram:
    """Parsed local-AI program.

    The language deliberately stays small and auditable: configuration and
    prompts are explicit, while Ollama remains the only external runtime.
    """

    model: str = "hermes3:8b"
    system: str = (
        "You are a local Hybit Mathematics assistant. Hybit is a constrained "
        "monoid object for Hijaiyyah codex data, not image processing. Each "
        "canonical letter maps to an 18D integer vector: Theta, Nuqthah(3), "
        "Khat(5), Qaws(5), and derived AN, AK, AQ, Hstar. Do not invent facts; "
        "say unknown when the supplied context is insufficient."
    )
    prompts: list[str] = field(default_factory=list)
    letters: list[str] = field(default_factory=list)

    @classmethod
    def parse(cls, source: str) -> HybitAIProgram:
        program = cls()
        for line_number, raw_line in enumerate(source.splitlines(), 1):
            line = raw_line.strip()
            if not line or line.startswith((";", "#")):
                continue
            command, separator, value = line.partition(" ")
            command = command.upper()
            value = value.strip() if separator else ""
            if command == "MODEL":
                if not value:
                    raise ValueError(f"Line {line_number}: MODEL needs a name")
                program.model = value
            elif command == "SYSTEM":
                if not value:
                    raise ValueError(f"Line {line_number}: SYSTEM needs text")
                program.system = value
            elif command == "ASK":
                if not value:
                    raise ValueError(f"Line {line_number}: ASK needs a prompt")
                program.prompts.append(value)
            elif command == "HLOAD":
                if len(value) != 1 or MASTER_TABLE.get_by_char(value) is None:
                    raise ValueError(f"Line {line_number}: unknown Hijaiyyah letter")
                program.letters.append(value)
            elif command in {"HGRD", "PRINT"}:
                continue
            else:
                raise ValueError(f"Line {line_number}: unknown instruction {command}")
        return program

    def validate_hybits(self) -> None:
        for char in self.letters:
            entry = MASTER_TABLE.get_by_char(char)
            if entry is None or not guard_check(list(entry.vector)):
                raise ValueError(f"Guard validation failed for {char}")


class OllamaClient:
    """Small dependency-free client for Ollama's local chat endpoint."""

    def __init__(self, base_url: str = "http://127.0.0.1:11434", timeout: int = 7200,
                 opener: Callable = urllib.request.urlopen):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._opener = opener

    def chat(self, model: str, system: str, prompt: str) -> str:
        payload = json.dumps({
            "model": model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self._opener(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Cannot reach Ollama at {self.base_url}: {exc.reason}"
            ) from exc
        content = result.get("message", {}).get("content")
        if not isinstance(content, str):
            raise TypeError("Ollama response did not contain message.content")
        return content


def run_program(program: HybitAIProgram, client: OllamaClient) -> dict[str, object]:
    """Validate hybits and execute every ASK instruction locally."""
    program.validate_hybits()
    answers = [client.chat(program.model, program.system, prompt) for prompt in program.prompts]
    return {"model": program.model, "letters": list(program.letters), "answers": answers}