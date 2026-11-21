# Database migrations

Add a file named `NNNN_description.sql` for each new database change. Use a
unique, increasing version number, and update `db/schema.sql` so new databases
also have the latest schema. A new, empty database is created from that schema
and records the existing migrations as already applied. Include any required
initial data in the schema or initialization seed data as well as in the
migration for existing databases. Migrations must tolerate the latest schema
having already created any new tables.

SQL files are executed one statement at a time in the initialization
transaction. Do not include `BEGIN`, `COMMIT`, `ROLLBACK`, or savepoints; the
migration runner owns the transaction. Each successful migration is recorded
in `schema_migrations` and is not run again. Do not edit or rename a migration
after it has been applied; add a new migration instead.

If a change needs conditional logic that SQLite SQL cannot express, use a
numbered `.py` file with an `apply(conn)` function. Use `conn.execute` and do
not call `commit`, `rollback`, or `executescript`. Migration `0001` uses this
format to handle the different legacy schemas.

Stop all Docksy processes before deploying a migration and restart them after
the update, so old and new code do not use incompatible schemas concurrently.
