# Database migrations

Add a file named `NNNN_description.sql` or `NNNN_description.py` under
`db/migrations/` for each new database change. Use a
unique, increasing version number, and update `db/schema.sql` so new databases
also have the latest schema. A new, empty database is created from that schema
and records the existing migrations as already applied. Include any required
initial data in the schema or initialization seed data as well as in the
migration for existing databases. Migrations must tolerate the latest schema
having already created any new tables.

For example, to add an optional `notes` column to `clan`, add it to the
`clan` table definition in `db/schema.sql`:

```sql
notes TEXT
```

Then create a migration file such as `0001_add_clan_notes.sql`, using the next
available version number:

```sql
ALTER TABLE clan ADD COLUMN notes TEXT;
```

Existing databases receive the column when the migration runs. New databases
get it from `schema.sql` and record the migration without running it again.

SQL files are executed one statement at a time in the initialization
transaction. Do not include `BEGIN`, `COMMIT`, `ROLLBACK`, or savepoints; the
migration runner owns the transaction. Each successful migration is recorded
in `schema_migrations` and is not run again. Do not edit or rename a migration
after it has been applied; add a new migration instead.

If a change needs conditional logic that SQLite SQL cannot express, use a
numbered `.py` file with an `apply(conn)` function. Use `conn.execute` and do
not call `commit`, `rollback`, or `executescript`.

For example, suppose some existing databases have a `legacy_notes` column and
others do not. A Python migration can add `notes` and replace the old column
when it exists. After adding `notes` to `db/schema.sql`, create
`db/migrations/0001_add_clan_notes.py`:

```python
def apply(conn):
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(clan)")}
    if "notes" not in columns:
        conn.execute("ALTER TABLE clan ADD COLUMN notes TEXT")
    if "legacy_notes" in columns:
        conflict = conn.execute(
            "SELECT 1 FROM clan WHERE notes IS NOT NULL "
            "AND legacy_notes IS NOT NULL AND notes != legacy_notes LIMIT 1"
        ).fetchone()
        if conflict:
            raise ValueError("Conflicting note values must be resolved first")
        conn.execute(
            "UPDATE clan SET notes = legacy_notes WHERE notes IS NULL"
        )
        conn.execute("ALTER TABLE clan DROP COLUMN legacy_notes")
```

The migration checks for conflicting values before dropping the old column.
Also remove `legacy_notes` from `db/schema.sql` so new databases use only the
replacement column.

Choose either the SQL or Python file for a change; migration version numbers
must be unique across both formats.

Stop all Docksy processes before deploying a migration and restart them after
the update, so old and new code do not use incompatible schemas concurrently.
