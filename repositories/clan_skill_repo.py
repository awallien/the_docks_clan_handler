# repositories/clan_skill_repo.py
from .base.clan_metric_repo import ClanMetricRepository


class ClanSkillRepository(ClanMetricRepository):
    def __init__(self, db):
        super().__init__(db, "clan_skills", "skill_id")

    def upsert(self, clan_id, skill_id, level, xp):
        self.execute("""
            INSERT INTO clan_skills (clan_id, skill_id, level, total_xp)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(clan_id, skill_id)
            DO UPDATE SET
                level = excluded.level,
                total_xp = excluded.total_xp
        """, (clan_id, skill_id, level, xp))
