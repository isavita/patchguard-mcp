import sqlite3

def run_query(user_input):
    conn = sqlite3.connect("db.sqlite")
    cur = conn.cursor()

    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    cur.execute(query)

    return cur.fetchall()
