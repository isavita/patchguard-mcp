# PatchGuard MCP

You have access to an MCP server named `patchguard` with the tool:

```
scan_code(language, code)
```

It performs:

* `security_static_analysis`
* `style_static_analysis`
* `llm_review` (LLM-based security/code-quality review)

Outputs are universal for all languages.

---

## Required behavior

Whenever you generate or modify **any source code**, you MUST:

1. Call `scan_code` with:

   * `language` = the code’s language (e.g., `"python"`, `"javascript"`, `"go"`)
   * `code` = the full file contents

2. Read all returned fields:

   * `security_static_analysis`
   * `style_static_analysis`
   * `llm_review`

3. Fix any issues the tool reports, especially security risks.

4. Re-run `scan_code` after making changes until no significant issues remain.

---

## Response requirements

* Always state when you ran `scan_code`.
* Summarize the issues found.
* Provide updated code reflecting the fixes.

This ensures all generated code is checked and improved by PatchGuard.
