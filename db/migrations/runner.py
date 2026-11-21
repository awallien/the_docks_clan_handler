"""Discover and apply numbered database migrations within the caller's transaction."""

import importlib.util
import re
import sqlite3
from pathlib import Path


MIGRATIONS_DIR = Path(__file__).parent
MIGRATION_NAME = re.compile(r"^(\d+)_[a-z0-9_]+\.(sql|py)$")


def execute_sql(conn, script):
    # executescript() commits implicitly, so execute complete statements one at
    # a time to keep the migration and its ledger entry in one transaction.
    def authorize(action, _arg1, _arg2, _database, _trigger):
        if action in (sqlite3.SQLITE_TRANSACTION, sqlite3.SQLITE_SAVEPOINT):
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    conn.set_authorizer(authorize)
    try:
        statement = ""
        for char in script:
            statement += char
            if char == ";" and sqlite3.complete_statement(statement):
                conn.execute(statement)
                statement = ""
        if statement.strip():
            conn.execute(statement)
    finally:
        conn.set_authorizer(None)


def apply_migrations(conn, *, baseline=False):
    migrations = []
    for path in MIGRATIONS_DIR.iterdir():
        match = MIGRATION_NAME.fullmatch(path.name)
        if match and path.is_file():
            migrations.append((int(match.group(1)), path))
    migrations.sort(key=lambda item: item[0])
    versions = [version for version, _ in migrations]
    if len(set(versions)) != len(versions):
        raise ValueError("Duplicate database migration version")

    applied = {row["version"]: row["name"] for row in conn.execute("SELECT version, name FROM schema_migrations")}
    if set(applied) - set(versions):
        raise ValueError("Database has migrations not present in this version of Docksy")
    if sorted(applied) != versions[:len(applied)]:
        raise ValueError("Database migration history has a gap")
    for version, path in migrations:
        if version in applied:
            if applied[version] != path.name:
                raise ValueError(f"Database migration {version} has a different name")
            continue
        if not baseline:
            if path.suffix == ".sql":
                execute_sql(conn, path.read_text(encoding="utf-8"))
            else:
                spec = importlib.util.spec_from_file_location(f"{__name__}._migration_{version}", path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.apply(conn)
        conn.execute(
            "INSERT INTO schema_migrations (version, name, applied_at) "
            "VALUES (?, ?, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))",
            (version, path.name),
        )
