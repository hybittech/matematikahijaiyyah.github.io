import json

import pytest

from hijaiyyah.ai.runtime import HybitAIProgram, OllamaClient, run_program


def test_parse_and_validate_hcai_program():
    program = HybitAIProgram.parse("MODEL hermes3:8b\nHLOAD ا\nHGRD\nASK hello")
    program.validate_hybits()
    assert program.model == "hermes3:8b"
    assert program.letters == ["ا"]
    assert program.prompts == ["hello"]


def test_parse_rejects_unknown_instruction():
    with pytest.raises(ValueError, match="unknown instruction"):
        HybitAIProgram.parse("MAGIC no")


def test_parse_rejects_unknown_letter():
    with pytest.raises(ValueError, match="unknown Hijaiyyah letter"):
        HybitAIProgram.parse("HLOAD x")


def test_ollama_client_posts_local_chat_request():
    seen = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"message": {"content": "ok"}}).encode()

    def opener(request, timeout):
        seen["url"] = request.full_url
        seen["body"] = json.loads(request.data)
        seen["timeout"] = timeout
        return Response()

    answer = OllamaClient(opener=opener).chat("hermes3:8b", "system", "hello")
    assert answer == "ok"
    assert seen["url"] == "http://127.0.0.1:11434/api/chat"
    assert seen["body"]["model"] == "hermes3:8b"
    assert seen["body"]["stream"] is False


def test_run_program_returns_local_answers():
    class FakeClient:
        def chat(self, model, system, prompt):
            return f"{model}: {prompt}"

    program = HybitAIProgram.parse("HLOAD ا\nASK hello")
    result = run_program(program, FakeClient())
    assert result["answers"] == ["hermes3:8b: hello"]