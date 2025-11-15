import server
from server import scan_code_impl, LLM_TEMPERATURE, LLM_MAX_TOKENS

# Override model to use faster model for testing
server.LLM_MODEL = "gemini/gemini-2.5-flash-lite"


def test_scan_code_basic_shape():
    code = "print('hello world')\n"
    result = scan_code_impl("python", code)

    # Keys exist
    assert "bandit_output" in result
    assert "ruff_output" in result
    assert "llm_review" in result

    # Types
    assert isinstance(result["bandit_output"], str)
    assert isinstance(result["ruff_output"], str)
    assert isinstance(result["llm_review"], str)


def test_detects_security_issue_in_bandit_output():
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

    bandit_output = result["bandit_output"]

    # We expect Bandit to report at least something for this code
    assert isinstance(bandit_output, str)
    assert bandit_output != ""

    # Usually includes B608 and/or "SQL injection" for this pattern
    assert ("B608" in bandit_output) or ("SQL injection" in bandit_output)


def test_non_python_language_error():
    result = scan_code_impl("javascript", "console.log('hello');")

    assert "error" in result
    assert result["error"].startswith("Only Python is supported")


def test_with_faster_model():
    """
    Verify that the faster model is being used for testing.
    """
    # Verify the model override is in place
    assert server.LLM_MODEL == "gemini/gemini-2.5-flash-lite"
    assert LLM_TEMPERATURE is not None
    assert isinstance(LLM_TEMPERATURE, float)
    assert isinstance(LLM_MAX_TOKENS, int)
