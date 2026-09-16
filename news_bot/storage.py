import sqlite3
from contextlib import contextmanager

from config import DB_PATH


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_items (
                item_id TEXT PRIMARY KEY,
                source TEXT,
                title TEXT,
                link TEXT,
                sent_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def is_seen(item_id: str) -> bool:
    with get_conn() as conn:
        cur = conn.execute("SELECT 1 FROM seen_items WHERE item_id = ?", (item_id,))
        return cur.fetchone() is not None


def mark_seen(item_id: str, source: str, title: str, link: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO seen_items (item_id, source, title, link) VALUES (?, ?, ?, ?)",
            (item_id, source, title, link),
        )
        conn.commit()
