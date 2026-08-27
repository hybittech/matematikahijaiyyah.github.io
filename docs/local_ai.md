# Hybit Local AI

`hybit-ai` runs small HC-style programs against an Ollama model on the local
machine. It does not require an API key or a cloud service.

## Run

```bash
source .venv-mac/bin/activate
hybit-ai examples/local_ai.hcai
```

The default endpoint is `http://127.0.0.1:11434` and the example uses
`hermes3:8b`.

## Program format

```text
MODEL hermes3:8b
SYSTEM You are a precise Hybit Mathematics assistant.
HLOAD ا
HGRD
ASK Explain the loaded hybit.
PRINT
```

Supported instructions are `MODEL`, `SYSTEM`, `HLOAD`, `HGRD`, `ASK`, and
`PRINT`. `HLOAD` resolves a canonical letter through the sealed master table,
and the runtime validates its guard constraints before sending prompts.

The application is intentionally auditable: it does not execute arbitrary
Python or shell commands from a program file. Use the existing HC/HASM/HVM
pipeline when you need full machine-level execution.