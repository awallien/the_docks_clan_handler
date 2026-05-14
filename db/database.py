import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ExecuteResult:
    lastrowid: int
    rowcount: int

class Database:
    DB_CACHE_PATH = Path(__file__).parent.resolve() / "db_cache"

    def __init__(self, db_name: str, timeout: float = 5.0):
        self.path = self.DB_CACHE_PATH / db_name
        self.timeout = timeout

        self.DB_CACHE_PATH.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Connection layer
    # -------------------------
    @contextmanager
    def connection(self):
        conn = sqlite3.connect(
            self.path,
            timeout=self.timeout,
        )

        conn.row_factory = sqlite3.Row

        # Performance + concurrency settings
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA synchronous = NORMAL;")

        try:
            yield conn
        finally:
            conn.close()

    # -------------------------
    # INIT SCHEMA
    # -------------------------
    def init_schema(self, schema_path: str = None):
        if schema_path is None:
            schema_path = Path(__file__).parent / "schema.sql"

        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        with self.connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()

    # -------------------------
    # Core execute (WRITE)
    # -------------------------
    def execute(self, query, params=(), retries=5):
        last_error = None

        for i in range(retries):
            try:
                with self.connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    conn.commit()
                    return ExecuteResult(cursor.lastrowid, cursor.rowcount)

            except sqlite3.OperationalError as e:
                last_error = e

                if "locked" in str(e).lower():
                    time.sleep(0.05 * (i + 1))
                    continue

                raise  # other errors = real bugs

        raise RuntimeError(f"Database locked too long: {last_error}")

    # -------------------------
    # READ helpers
    # -------------------------
    def fetch_all(self, query, params=()):
        with self.connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()

    def fetch_one(self, query, params=()):
        with self.connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()

    # -------------------------
    # Optional convenience
    # -------------------------
    def executescript(self, script: str):
        with self.connection() as conn:
            conn.executescript(script)
            conn.commit()
