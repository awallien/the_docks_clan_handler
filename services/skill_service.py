class SkillService:
    def __init__(self, skill_repo, clan_skill_repo, clan_repo):
        self.skill_repo = skill_repo
        self.clan_skill_repo = clan_skill_repo
        self.clan_repo = clan_repo

    def _get_skill(self, name):
        skill = self.skill_repo.get_by_name(name)
        if not skill:
            raise ValueError(f"Skill '{name}' not found")
        return skill

    def _get_clan(self, name):
        clan = self.clan_repo.get_by_name(name)
        if not clan:
            raise ValueError(f"Clan member '{name}' not found")
        return clan

    def set_skill(self, member_name, skill_name, level, xp):
        clan = self._get_clan(member_name)
        skill = self._get_skill(skill_name)

        if level < 0 or xp < 0:
            raise ValueError("Invalid values")

        self.clan_skill_repo.upsert(
            clan["id"],
            skill["id"],
            level,
            xp
        )

    def get_skills(self, member_name):
        clan = self._get_clan(member_name)
        return self.clan_skill_repo.list_by_clan(clan["id"])
