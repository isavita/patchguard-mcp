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

# LLM configuration
# LLM_MODEL = "gemini/gemini-2.5-pro"
# LLM_MODEL = "gemini/gemini-2.5-flash"
# LLM_MODEL = "gemini/gemini-2.5-flash-lite"
LLM_MODEL = "groq/moonshotai/kimi-k2-instruct-0905"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 4096

mcp = FastMCP("patchguard-mcp")


def _run_bandit(path: Path) -> str:
    """
    Security-oriented static analysis using Bandit.
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
    Style/lint-oriented static analysis using Ruff.
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


def _run_llm_review(language: str, code: str) -> str:
    """
    Optional LLM-based review using LiteLLM and Gemini.

    Returns a short text summary or a fallback message if unavailable.
    """
    if litellm_completion is None:
        return "LLM review not available: litellm is not installed in this environment."

    if not os.getenv("GEMINI_API_KEY"):
        return "LLM review not available: GEMINI_API_KEY environment variable is not set."

    try:
        response = litellm_completion(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior security engineer reviewing source code. "
                        "Focus on security vulnerabilities, unsafe patterns, and clear remediation advice."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Language: {language}\n\n"
                        "Review the following code for security issues and risky patterns.\n"
                        "Respond with AT MOST 3 bullet points.\n"
                        "- Each bullet MUST be concise (ideally under 120 characters).\n"
                        "- Do NOT add any intro or outro text, only the bullets.\n\n"
                        f"```{language}\n{code}\n```"
                    ),
                },
            ],
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
        )

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
      - language: normalized language string
      - security_static_analysis: raw text from security-oriented static tools
      - style_static_analysis: raw text from style/lint-oriented tools
      - llm_review: optional LLM-based review summary

    For now:
      - Python: bandit (security) + ruff (style) + LLM review
      - Other languages: only LLM review (static outputs empty strings)
    """
    language_normalized = language.strip().lower()

    security_static_output = ""
    style_static_output = ""

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "snippet"
        if language_normalized == "python":
            path = path.with_suffix(".py")

        path.write_text(code)

        if language_normalized == "python":
            security_static_output = _run_bandit(path)
            style_static_output = _run_ruff(path)

            # Strip the temp path for cleaner output
            temp_path_str = str(path)
            security_static_output = security_static_output.replace(
                temp_path_str, "snippet.py"
            )
            style_static_output = style_static_output.replace(
                temp_path_str, "snippet.py"
            )

    llm_review = _run_llm_review(language_normalized, code)

    return {
        "language": language_normalized,
        "security_static_analysis": security_static_output,
        "style_static_analysis": style_static_output,
        "llm_review": llm_review,
    }


@mcp.tool()
def scan_code(
    language: Literal[
        "python",
        "javascript",
        "typescript",
        "go",
        "ruby",
        "java",
        "csharp",
        "php",
        "other",
    ],
    code: str,
) -> dict:
    """
    MCP tool wrapper that calls the core implementation.

    The MCP result is universal for any language:
    {
        "language": "<normalized language>",
        "security_static_analysis": "<security-oriented static analysis output>",
        "style_static_analysis": "<style/lint static analysis output>",
        "llm_review": "<short LLM review or fallback message>"
    }
    """
    return scan_code_impl(language, code)


if __name__ == "__main__":
    mcp.run(transport="stdio")
