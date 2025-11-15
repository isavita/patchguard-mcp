from server import scan_code_impl


def test_scan_code_basic_shape():
    code = "print('hello world')\n"
    result = scan_code_impl("python", code)

    # Keys exist
    assert "bandit_output" in result
    assert "ruff_output" in result

    # Both are strings (may be empty if no issues)
    assert isinstance(result["bandit_output"], str)
    assert isinstance(result["ruff_output"], str)


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

    # Make the assertion a bit robust across versions:
    # usually includes B608 and/or "SQL injection".
    assert ("B608" in bandit_output) or ("SQL injection" in bandit_output)


def test_non_python_language_error():
    result = scan_code_impl("javascript", "console.log('hello');")

    assert "error" in result
    assert result["error"].startswith("Only Python is supported")
