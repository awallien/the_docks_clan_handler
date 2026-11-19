class HiscoreRepository:
    """Persist a member's hiscore snapshot in a single transaction."""

    def __init__(self, db):
        self.db = db

    def save_snapshot(self, member_id, member_name, skills, activities, bosses, calculate_rank):
        with self.db.connection() as conn:
            # Check identity under the write lock: the CLI may rename or delete a
            # member while the network request is in flight.
            conn.execute("BEGIN IMMEDIATE")
            member = conn.execute(
                "SELECT member, rank, joined_date FROM clan WHERE id = ?", (member_id,)
            ).fetchone()
            if member is None or member["member"] != member_name:
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
                    if table == "clan_skills":
                        level, xp = value
                        conn.execute(
                            "INSERT INTO clan_skills (clan_id, skill_id, level, total_xp) VALUES (?, ?, ?, ?) "
                            "ON CONFLICT(clan_id, skill_id) DO UPDATE SET level = excluded.level, total_xp = excluded.total_xp",
                            (member_id, ids[name], level, xp),
                        )
                    else:
                        conn.execute(
                            f"INSERT INTO {table} (clan_id, {ref_column}, count) VALUES (?, ?, ?) "
                            f"ON CONFLICT(clan_id, {ref_column}) DO UPDATE SET count = excluded.count",
                            (member_id, ids[name], value),
                        )
            new_rank = calculate_rank(member["rank"], member["joined_date"])
            if new_rank is not None and new_rank != member["rank"]:
                conn.execute("UPDATE clan SET rank = ?, rank_update = 1 WHERE id = ?", (new_rank, member_id))
            conn.commit()
            return True
