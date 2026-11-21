from datetime import datetime, timezone
from uuid import uuid4


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


class HiscoreRepository:
    """Persist refresh outcomes and snapshots without changing ranks."""

    def __init__(self, db):
        self.db = db

    def begin_refresh(self, member_id, member_name):
        token, now = uuid4().hex, utc_now()
        with self.db.connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            member = conn.execute("SELECT member FROM clan WHERE id = ?", (member_id,)).fetchone()
            if member is None or member["member"] != member_name:
                return None
            conn.execute(
                "INSERT INTO hiscore_refresh (clan_id, status, attempted_at, attempt_id) VALUES (?, 'pending', ?, ?) "
                "ON CONFLICT(clan_id) DO UPDATE SET status = 'pending', attempted_at = excluded.attempted_at, attempt_id = excluded.attempt_id",
                (member_id, now, token),
            )
            conn.commit()
        return token

    def fail_refresh(self, member_id, member_name, token):
        self.db.execute(
            "UPDATE hiscore_refresh SET status = 'failed' WHERE clan_id = ? AND attempt_id = ? "
            "AND EXISTS (SELECT 1 FROM clan WHERE id = ? AND member = ?)",
            (member_id, token, member_id, member_name),
        )

    def save_snapshot(self, member_id, member_name, token, skills, activities, bosses):
        with self.db.connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            member = conn.execute(
                "SELECT c.member, h.attempt_id FROM clan c JOIN hiscore_refresh h ON h.clan_id = c.id WHERE c.id = ?",
                (member_id,),
            ).fetchone()
            if member is None or member["member"] != member_name or member["attempt_id"] != token:
                return False
            for table, ref_table, ref_column, values in (
                ("clan_skills", "skills", "skill_id", skills),
                ("clan_activities", "activities", "activity_id", activities),
                ("clan_bosses", "bosses", "boss_id", bosses),
            ):
                ids = {row["name"]: row["id"] for row in conn.execute(f"SELECT id, name FROM {ref_table}")}
                for name, value in values.items():
                    if name not in ids:
                        raise ValueError(f"{ref_table} reference '{name}' not found")
                    if value is None:
                        conn.execute(f"DELETE FROM {table} WHERE clan_id = ? AND {ref_column} = ?", (member_id, ids[name]))
                    elif table == "clan_skills":
                        conn.execute(
                            "INSERT INTO clan_skills (clan_id, skill_id, level, total_xp) VALUES (?, ?, ?, ?) "
                            "ON CONFLICT(clan_id, skill_id) DO UPDATE SET level = excluded.level, total_xp = excluded.total_xp",
                            (member_id, ids[name], *value),
                        )
                    else:
                        conn.execute(
                            f"INSERT INTO {table} (clan_id, {ref_column}, count) VALUES (?, ?, ?) "
                            f"ON CONFLICT(clan_id, {ref_column}) DO UPDATE SET count = excluded.count",
                            (member_id, ids[name], value),
                        )
            status = "incomplete" if any(value is None for value in skills.values()) else "complete"
            conn.execute("UPDATE hiscore_refresh SET status = ?, succeeded_at = ? WHERE clan_id = ? AND attempt_id = ?",
                         (status, utc_now(), member_id, token))
            conn.commit()
        return True
