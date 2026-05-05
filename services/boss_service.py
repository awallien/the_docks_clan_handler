from repositories import BossRepository, ClanBossRepository, ClanRepository

class BossService:
    def __init__(self, boss_repo, clan_boss_repo, clan_repo):
        self.boss_repo: BossRepository = boss_repo
        self.clan_boss_repo: ClanBossRepository = clan_boss_repo
        self.clan_repo: ClanRepository = clan_repo

    def _get_boss(self, name):
        boss = self.boss_repo.get_by_name(name)
        if not boss:
            raise ValueError(f"Boss '{name}' not found")
        return boss

    def _get_clan(self, name):
        clan = self.clan_repo.get_by_name(name)
        if not clan:
            raise ValueError(f"Clan member '{name}' not found")
        return clan

    def add_kill(self, member_name, boss_name, count=1):
        if count <= 0:
            raise ValueError("Count must be positive")

        clan = self._get_clan(member_name)
        boss = self._get_boss(boss_name)

        self.clan_boss_repo.increment(
            clan["id"],
            boss["id"],
            count
        )

    def get_bosses(self, member_name):
        clan = self._get_clan(member_name)
        return self.clan_boss_repo.list_by_clan(clan["id"])
