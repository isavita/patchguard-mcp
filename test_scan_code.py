import server
from server import scan_code_impl, LLM_TEMPERATURE, LLM_MAX_TOKENS

# Override model to use faster model for testing
server.LLM_MODEL = "gemini/gemini-2.5-flash-lite"


def test_scan_code_basic_shape():
    code = "print('hello world')\n"
    result = scan_code_impl("python", code)

    # Top-level keys
    assert result["language"] == "python"
    assert "security_static_analysis" in result
    assert "style_static_analysis" in result
    assert "llm_review" in result

    # Types
    assert isinstance(result["security_static_analysis"], str)
    assert isinstance(result["style_static_analysis"], str)
    assert isinstance(result["llm_review"], str)


def test_detects_security_issue_in_security_static_analysis():
    bad_code = """
import sqlite3

def run_query(user_input):
    conn = sqlite3.connect("db.sqlite")
    cur = conn.cursor()
    # INTENTIONALLY INSECURE: SQL injection
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    cur.execute(query)
"""
    result = scan_code_impl("python", bad_code)

    sec_output = result["security_static_analysis"]

    # We expect the security scan to report something for this code
    assert isinstance(sec_output, str)
    assert sec_output != ""

    # Usually includes B608 and/or "SQL injection" for this pattern
    assert ("B608" in sec_output) or ("SQL injection" in sec_output)


def test_non_python_language_universal_shape():
    """
    For non-Python languages, we still get the same universal structure.
    Static analysis fields may be empty, but are present and strings.
    """
    result = scan_code_impl("javascript", "console.log('hello');")

    assert result["language"] == "javascript"
    assert "security_static_analysis" in result
    assert "style_static_analysis" in result
    assert isinstance(result["security_static_analysis"], str)
    assert isinstance(result["style_static_analysis"], str)
    assert isinstance(result["llm_review"], str)


def test_with_faster_model():
    """
    Verify that the faster model is being used for testing.
    """
    assert server.LLM_MODEL == "gemini/gemini-2.5-flash-lite"
    assert isinstance(LLM_TEMPERATURE, float)
    assert isinstance(LLM_MAX_TOKENS, int)
