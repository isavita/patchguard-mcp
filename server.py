from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP

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

    # Minimal processing: prefer stdout, fall back to stderr
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

    # Minimal processing: prefer stdout, fall back to stderr
    if proc.stdout:
        return proc.stdout.strip()
    if proc.stderr:
        return proc.stderr.strip()
    return ""


def scan_code_impl(language: str, code: str) -> dict:
    """
    Core logic used by both the MCP tool and demo/tests.

    Returns raw bandit and ruff outputs so the LLM can interpret them.
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

        return {
            "bandit_output": bandit_output,
            "ruff_output": ruff_output,
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
        "ruff_output": "<raw ruff text>"
    }
    """
    return scan_code_impl(language, code)


if __name__ == "__main__":
    mcp.run(transport="stdio")
