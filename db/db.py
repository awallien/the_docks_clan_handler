import sqlite3
from contextlib import contextmanager


class Database:

    def __init__(self, db_path: str):
        self.path = db_path

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")

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
