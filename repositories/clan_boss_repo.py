from .base.clan_metric_repo import ClanMetricRepository


class ClanBossRepository(ClanMetricRepository):
    def __init__(self, db):
        super().__init__(db, "clan_bosses", "boss_id")

    def increment(self, clan_id, boss_id, amount=1):
        self.increment_value(clan_id, boss_id, "count", amount)
