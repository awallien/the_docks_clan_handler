"""Migrate databases created before rank reports used change records."""


def apply(conn):
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(clan)")}
    if "last_rank_update" not in columns:
        conn.execute("ALTER TABLE clan ADD COLUMN last_rank_update DATE")
    if "last_rank_date" in columns:
        conn.execute("ALTER TABLE clan DROP COLUMN last_rank_date")

    rank_columns = {row["name"] for row in conn.execute("PRAGMA table_info(rank_changes)")}
    if "superseded_at" not in rank_columns:
        conn.execute("ALTER TABLE rank_changes ADD COLUMN superseded_at TEXT")

    if "rank_update" in columns:
        if conn.execute("SELECT 1 FROM clan WHERE rank_update = 1 AND rank IS NULL LIMIT 1").fetchone():
            raise ValueError("Cannot migrate a pending rank update without a rank")
        conn.execute(
            "INSERT INTO rank_changes (clan_id, previous_rank, new_rank, created_at) "
            "SELECT id, NULL, rank, strftime('%Y-%m-%dT%H:%M:%SZ', 'now') FROM clan "
            "WHERE rank_update = 1 AND rank IS NOT NULL"
        )
        conn.execute("ALTER TABLE clan DROP COLUMN rank_update")
