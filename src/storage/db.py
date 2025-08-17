import sqlite3
import os


class DB:
    def __init__(self, db_path: str = "storage/data.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self._init_tables()

    def _init_tables(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                url TEXT PRIMARY KEY,
                title TEXT,
                source TEXT,
                published_at TEXT,
                posted INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def seen(self, url: str) -> bool:
        self.cur.execute("SELECT 1 FROM posts WHERE url = ?", (url,))
        return self.cur.fetchone() is not None

    def add_if_absent(self, url: str, title: str, source: str, published_at: str):
        if not self.seen(url):
            self.cur.execute(
                "INSERT INTO posts (url, title, source, published_at) VALUES (?, ?, ?, ?)",
                (url, title, source, published_at)
            )
            self.conn.commit()

    def mark_posted(self, url: str):
        self.cur.execute("UPDATE posts SET posted = 1 WHERE url = ?", (url,))
        self.conn.commit()

    # === Новые методы для героев ===
    def used_heroes(self) -> list[str]:
        """Список героев, которые уже постились"""
        self.cur.execute("SELECT url FROM posts WHERE url LIKE 'hero:%'")
        rows = self.cur.fetchall()
        return [row[0].replace("hero:", "") for row in rows]

    def reset_heroes(self):
        """Удаляет все записи героев, оставляя только обычные новости/видео"""
        self.cur.execute("DELETE FROM posts WHERE url LIKE 'hero:%'")
        self.conn.commit()
