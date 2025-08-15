import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    title TEXT,
    source TEXT,
    published_at TEXT,
    posted_at TEXT
);
"""


class DB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def seen(self, url: str) -> bool:
        cur = self.conn.execute("SELECT 1 FROM articles WHERE url = ?", (url,))
        return cur.fetchone() is not None

    def add_if_absent(self, url: str, title: str, source: str, published_at: Optional[str]):
        try:
            self.conn.execute(
                "INSERT OR IGNORE INTO articles(url, title, source, published_at) VALUES (?, ?, ?, ?)",
                (url, title, source, published_at),
            )
            self.conn.commit()
        except Exception:
            pass

    def mark_posted(self, url: str):
        self.conn.execute(
            "UPDATE articles SET posted_at = datetime('now') WHERE url = ?",
            (url,),
        )
        self.conn.commit()
