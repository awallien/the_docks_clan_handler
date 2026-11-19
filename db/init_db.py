
from pathlib import Path

from .database import Database
from resources import SKILLS, BOSSES, ACTIVITIES


def init_schema(db: Database, schema_path: str = None):
    if schema_path is None:
        schema_path = Path(__file__).parent / "schema.sql"

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    bosses_params = [(boss,) for boss in BOSSES]
    skills_params = [(skill,) for skill in SKILLS]
    activities_params = [(activity,) for activity in ACTIVITIES]

    tables_and_params = [
        ("bosses", bosses_params),
        ("skills", skills_params),
        ("activities", activities_params),
    ]

    with db.connection() as conn:
        # Create tables
        conn.executescript(schema_sql)

        # Acquire the write lock before checking so concurrent processes migrate only once.
        conn.execute("BEGIN IMMEDIATE")
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(clan)")}
        if "rank_update" not in columns:
            conn.execute("ALTER TABLE clan ADD COLUMN rank_update INTEGER NOT NULL DEFAULT 0 CHECK(rank_update IN (0, 1))")
        if "last_rank_date" in columns:
            conn.execute("ALTER TABLE clan DROP COLUMN last_rank_date")

        # Seed data safely
        for table, params in tables_and_params:
            if not params:
                continue

            query = f"INSERT OR IGNORE INTO {table} (name) VALUES (?)"
            conn.executemany(query, params)

        conn.commit()
