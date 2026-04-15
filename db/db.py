import sqlite3
from contextlib import contextmanager
from pathlib import Path

class Database:
    DB_CACHE_PATH = Path(__file__).parent.resolve() / "db_cache"

    def __init__(self, db_name: str):
        self.path = self.DB_CACHE_PATH / db_name

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys = ON;")

        try:
            yield conn
        finally:
            conn.close()

    
    def execute(self, query, params=()):
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor
        
    def fetch_all(self, query, params=()):
        return self.execute(query, params).fetchall()
    
    def fetch_one(self, query, params=()):
        return self.execute(query, params).fetchone()
