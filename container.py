from db import Database

from repositories import (
    ClanRepository,
    SkillRepository,
    ActivityRepository,
    BossRepository,
    ClanSkillRepository,
    ClanActivityRepository,
    ClanBossRepository,
)

from services import (
    ClanService,
    SkillService,
    ActivityService,
    BossService,
    RankService,
)


class Container:
    def __init__(self, db: Database):
        self.db = db

        # cache for singletons
        self._instances = {}

    # -------------------
    # Repository providers
    # -------------------

    def clan_repo(self):
        return self._get("clan_repo", lambda: ClanRepository(self.db))

    def skill_repo(self):
        return self._get("skill_repo", lambda: SkillRepository(self.db))

    def activity_repo(self):
        return self._get("activity_repo", lambda: ActivityRepository(self.db))

    def boss_repo(self):
        return self._get("boss_repo", lambda: BossRepository(self.db))

    def clan_skill_repo(self):
        return self._get("clan_skill_repo", lambda: ClanSkillRepository(self.db))

    def clan_activity_repo(self):
        return self._get("clan_activity_repo", lambda: ClanActivityRepository(self.db))

    def clan_boss_repo(self):
        return self._get("clan_boss_repo", lambda: ClanBossRepository(self.db))

    # -------------------
    # Service providers
    # -------------------

    def clan_service(self) -> ClanService:
        return self._get(
            "clan_service",
            lambda: ClanService(self.clan_repo())
        )

    def skill_service(self) -> SkillService:
        return self._get(
            "skill_service",
            lambda: SkillService(
                self.skill_repo(),
                self.clan_skill_repo(),
                self.clan_repo(),
            )
        )

    def activity_service(self) -> ActivityService:
        return self._get(
            "activity_service",
            lambda: ActivityService(
                self.activity_repo(),
                self.clan_activity_repo(),
                self.clan_repo(),
            )
        )

    def boss_service(self) -> BossService:
        return self._get(
            "boss_service",
            lambda: BossService(
                self.boss_repo(),
                self.clan_boss_repo(),
                self.clan_repo(),
            )
        )
    
    def rank_service(self) -> RankService:
        return self._get(
            "rank_service",
            lambda: RankService()
        )

    # -------------------
    # Internal helper
    # -------------------

    def _get(self, key, factory):
        if key not in self._instances:
            self._instances[key] = factory()
        return self._instances[key]
