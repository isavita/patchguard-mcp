from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP

# Optional: LiteLLM for LLM-based review
try:
    from litellm import completion as litellm_completion
except ImportError:
    litellm_completion = None

mcp = FastMCP("patchguard-mcp")


def _run_bandit(path: Path) -> str:
    """
    Run bandit with text output and return raw output (stdout or stderr).
    Command: bandit -f txt -q <FILE_PATH>
    """
    proc = subprocess.run(
        ["bandit", "-f", "txt", "-q", str(path)],
        capture_output=True,
        text=True,
    )

    if proc.stdout:
        return proc.stdout.strip()
    if proc.stderr:
        return proc.stderr.strip()
    return ""


def _run_ruff(path: Path) -> str:
    """
    Run ruff with concise output and return raw output (stdout or stderr).
    Command: ruff check --output-format concise <FILE_PATH>
    """
    proc = subprocess.run(
        ["ruff", "check", "--output-format", "concise", str(path)],
        capture_output=True,
        text=True,
    )

    if proc.stdout:
        return proc.stdout.strip()
    if proc.stderr:
        return proc.stderr.strip()
    return ""


def _run_llm_review(code: str) -> str:
    """
    Optional LLM-based review using LiteLLM and Gemini.
    Hardcoded model: gemini/gemini-2.5-pro.

    Returns a short text summary or a fallback message if unavailable.
    """
    if litellm_completion is None:
        return "LLM review not available: litellm is not installed in this environment."

    if not os.getenv("GEMINI_API_KEY"):
        return "LLM review not available: GEMINI_API_KEY environment variable is not set."

    try:
        response = litellm_completion(
            model="gemini/gemini-2.5-pro",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior security engineer reviewing Python code. "
                        "Focus on security vulnerabilities, unsafe patterns, and clear remediation advice."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Review the following Python code for security issues, bad practices, "
                        "and any risky patterns. Reply in a short, concise bullet list.\n\n"
                        f"```python\n{code}\n```"
                    ),
                },
            ],
            max_tokens=4096,
            temperature=0.1,
        )

        # LiteLLM usually returns OpenAI-style responses
        msg = response["choices"][0]["message"]["content"]

        # Some providers may return content parts as a list
        if isinstance(msg, list):
            parts = []
            for part in msg:
                if isinstance(part, dict) and "text" in part:
                    parts.append(part["text"])
                else:
                    parts.append(str(part))
            msg = "".join(parts)

        return str(msg).strip()

    except Exception as e:
        return f"LLM review not available: {type(e).__name__}: {e}"


def scan_code_impl(language: str, code: str) -> dict:
    """
    Core logic used by both the MCP tool and demo/tests.

    Returns:
      - bandit_output: raw bandit text
      - ruff_output: raw ruff text
      - llm_review: optional LLM-based review summary
    """
    if language != "python":
        return {
            "error": "Only Python is supported in this MVP.",
        }

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "snippet.py"
        path.write_text(code)

        bandit_output = _run_bandit(path)
        ruff_output = _run_ruff(path)
        llm_review = _run_llm_review(code)

        return {
            "bandit_output": bandit_output,
            "ruff_output": ruff_output,
            "llm_review": llm_review,
        }


@mcp.tool()
def scan_code(
    language: Literal["python"],
    code: str,
) -> dict:
    """
    MCP tool wrapper that calls the core implementation.

    The MCP result looks like:
    {
        "bandit_output": "<raw bandit text>",
        "ruff_output": "<raw ruff text>",
        "llm_review": "<short LLM review or fallback message>"
    }
    """
    return scan_code_impl(language, code)


if __name__ == "__main__":
    mcp.run(transport="stdio")
