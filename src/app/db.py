# connect: open the database file, create the table if missing
# save_posts: turn each dict into a row, save all in one go, report how many
# count_posts: count rows so I can prove it worked
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id      INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title   TEXT    NOT NULL,
    body    TEXT    NOT NULL
)
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    """Open the database and make sure the posts table exists."""
    conn = sqlite3.connect(db_path)  # creates the file if missing
    conn.execute(SCHEMA)
    return conn


def save_posts(conn: sqlite3.Connection, posts: list[dict]) -> int:
    """Insert or update posts. Return how many rows were written."""
    # translate: API dict -> database row (userId becomes user_id)
    rows = [(p["id"], p["userId"], p["title"], p["body"]) for p in posts]
    with conn:  # one transaction: all rows saved, or none
        conn.executemany(
            "INSERT OR REPLACE INTO posts (id, user_id, title, body) VALUES (?, ?, ?, ?)",
            rows,
        )
    return len(rows)


def count_posts(conn: sqlite3.Connection) -> int:
    """Return the number of rows in the posts table."""
    return conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
