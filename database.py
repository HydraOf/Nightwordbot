import sqlite3

def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS stats (
        user_id INTEGER PRIMARY KEY,
        mood_logs TEXT DEFAULT '',
        ratings TEXT DEFAULT '',
        feedbacks TEXT DEFAULT ''
    )
    """)

    conn.commit()
    conn.close()


def append_value(user_id, field, value):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()

    c.execute("SELECT * FROM stats WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if not row:
        c.execute("INSERT INTO stats (user_id) VALUES (?)", (user_id,))

    c.execute(f"UPDATE stats SET {field} = COALESCE({field}, '') || ? WHERE user_id = ?",
              (f"{value};", user_id))

    conn.commit()
    conn.close()


def get_user_stats(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()

    c.execute("SELECT * FROM stats WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    conn.close()
    return row
