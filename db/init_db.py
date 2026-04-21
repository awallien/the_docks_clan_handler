
from pathlib import Path

from .database import Database
from util.osrs_api import SKILLS, BOSSES, ACTIVITIES


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

        # Seed data safely
        for table, params in tables_and_params:
            if not params:
                continue

            query = f"INSERT OR IGNORE INTO {table} (name) VALUES (?)"
            conn.executemany(query, params)

        conn.commit()