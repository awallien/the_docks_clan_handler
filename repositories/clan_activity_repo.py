# repositories/clan_activity_repo.py
from .base.clan_metric_repo import ClanMetricRepository


class ClanActivityRepository(ClanMetricRepository):
    def __init__(self, db):
        super().__init__(db, "clan_activities", "activity_id")

    def increment(self, clan_id, activity_id, amount=1):
        self.increment_value(clan_id, activity_id, "count", amount)
