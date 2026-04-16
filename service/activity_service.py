
class ActivityService:
    def __init__(self, activity_repo, clan_activity_repo, clan_repo):
        self.activity_repo = activity_repo
        self.clan_activity_repo = clan_activity_repo
        self.clan_repo = clan_repo

    def _get_activity(self, name):
        activity = self.activity_repo.get_by_name(name)
        if not activity:
            raise ValueError(f"Activity '{name}' not found")
        return activity

    def _get_clan(self, name):
        clan = self.clan_repo.get_by_name(name)
        if not clan:
            raise ValueError(f"Clan member '{name}' not found")
        return clan

    def add_activity(self, member_name, activity_name, count=1):
        if count <= 0:
            raise ValueError("Count must be positive")

        clan = self._get_clan(member_name)
        activity = self._get_activity(activity_name)

        self.clan_activity_repo.increment(
            clan["id"],
            activity["id"],
            count
        )

    def get_activities(self, member_name):
        clan = self._get_clan(member_name)
        return self.clan_activity_repo.list_by_clan(clan["id"])
