# PatchGuard MCP

You have access to an MCP server named `patchguard` with a tool `scan_code(language, code)`.

## Required behavior

Whenever you:
- generate new Python code, or
- significantly modify an existing Python file,

you MUST:

1. Call the `scan_code` MCP tool with:
   - language = "python"
   - code = the full contents of the file
2. Inspect `bandit_output` for any security issues (e.g. SQL injection, eval, etc.).
3. If there are issues, fix the code and call `scan_code` again until no high/medium severity problems remain.

Always mention in your response when you ran `scan_code` and summarize any issues found.
