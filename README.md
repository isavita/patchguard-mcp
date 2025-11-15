# PatchGuard MCP

A minimal MCP server that provides universal code scanning using:

* **security_static_analysis** (e.g. Bandit for Python)
* **style_static_analysis** (e.g. Ruff for Python)
* **llm_review** (Gemini via LiteLLM)

Works for any language and returns a unified analysis format.

---

## Install

```bash
pip install -r requirements.txt
```

Optional for LLM review:

```bash
export GEMINI_API_KEY="your_key_here"
```

---

## Use with Gemini CLI

Register the MCP server:

```bash
gemini mcp add patchguard python server.py
```

Start a session with PatchGuard enabled:

```bash
gemini --allowed-mcp-server-names patchguard --approval-mode yolo
```

---

## Example prompt

Inside Gemini CLI:

> Write a function that runs a user-provided shell command with a 5-second timeout.

Gemini will:

1. Generate the code
2. Automatically call `scan_code(language, code)`
3. Display `security_static_analysis`, `style_static_analysis`, and `llm_review`

---

## Run tests

```bash
pytest -q
```
