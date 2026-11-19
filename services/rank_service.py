
from datetime import date
from typing import Dict, List

from util.osrs_api import Hiscore, SKILLS as osrs_api_SKILLS, Skill
from entity import ClanMemberRank
    
class RankService:

    MELEE_CMB_SKILLS = {"attack", "strength", "defence"}
    CMB_SKILLS = MELEE_CMB_SKILLS | {"ranged", "magic"}
    NON_COMBAT_SKILLS = set(osrs_api_SKILLS) - (CMB_SKILLS | {"hitpoints"})

    DAYS_PER_MONTH = 30
    
    @classmethod
    def new_member_rank(cls, hiscore_data: Hiscore | None = None) -> ClanMemberRank:
        """All new members start at rank 1."""
        return ClanMemberRank.RANK_1
    
    @classmethod
    def get_next_rank(
        cls,
        hiscore: Hiscore | None,
        current_rank: ClanMemberRank,
        joined_date: int,
    ) -> ClanMemberRank:
        """Return the next rank a member currently qualifies for."""

        if current_rank not in ClanMemberRank.values() or current_rank == ClanMemberRank.RANK_INVALID:
            raise ValueError("Clan member's rank is invalid")

        if (current_rank in ClanMemberRank.special_rank()
            or current_rank in ClanMemberRank.honorable_ranks()
            or current_rank in ClanMemberRank.administrative_ranks()):
            return current_rank

        # None represents a failed or unavailable lookup, not incomplete data.
        if hiscore is None:
            return current_rank

        days_since_join = (date.today() - date.fromordinal(joined_date)).days
        if days_since_join < 0:
            raise ValueError("Join date cannot be in the future")
        if days_since_join < 4 * cls.DAYS_PER_MONTH:
            return str(1 + days_since_join // cls.DAYS_PER_MONTH)
        return cls._get_next_achievement_rank(hiscore)
    
    @classmethod
    def _get_next_achievement_rank(
        cls,
        hiscore: Hiscore | None,
    ) -> ClanMemberRank:
        """Return the highest achievement rank currently qualified for."""
        if any(
            (skill := hiscore.skills.get(name)) is None
            or skill.level is None or skill.xp is None
            or skill.level < 0 or skill.xp < 0
            for name in osrs_api_SKILLS
        ):
            return ClanMemberRank.RANK_5

        combat_avg = cls.get_combat_avg(hiscore)
        non_combat_avg = cls.get_non_combat_avg(hiscore)

        highest_avg = max(combat_avg, non_combat_avg)

        # Ranks 5-11 are based on either combat or non-combat average.
        average_rank_ranges = (
            (0, 69, ClanMemberRank.RANK_5),
            (70, 74, ClanMemberRank.RANK_6),
            (75, 79, ClanMemberRank.RANK_7),
            (80, 84, ClanMemberRank.RANK_8),
            (85, 89, ClanMemberRank.RANK_9),
            (90, 94, ClanMemberRank.RANK_10),
            (95, 98, ClanMemberRank.RANK_11),
        )

        for minimum, maximum, rank in average_rank_ranges:
            if minimum <= highest_avg <= maximum:
                return rank

        # All remaining achievement ranks require 99s.
        if all(hiscore.skills.get(name).level >= 99 for name in osrs_api_SKILLS):
            return ClanMemberRank.RANK_15

        if combat_avg >= 99 and cls.get_non_combat_avg(
            hiscore,
            n_highest=6,
        ) >= 99:
            return ClanMemberRank.RANK_14

        if combat_avg >= 99 and non_combat_avg >= 99:
            return ClanMemberRank.RANK_13

        if highest_avg >= 99:
            return ClanMemberRank.RANK_12

        return ClanMemberRank.RANK_5

    @classmethod
    def get_combat_skills(cls, hiscore: Hiscore) -> Dict[str, Skill]:
        """Return the combat skills used for rank calculations."""
        skills = hiscore.skills

        return {
            "attack": skills.attack,
            "strength": skills.strength,
            "defence": skills.defence,
            "ranged": skills.ranged,
            "magic": skills.magic,
        }

    @classmethod
    def get_combat_avg(cls, hiscore: Hiscore) -> int:
        """
        Return the combat average using:
        max(attack, strength, defence), ranged, magic.
        """
        skills = cls.get_combat_skills(hiscore)

        strongest_melee = cls.get_max_skills(
            skills["attack"],
            skills["strength"],
            skills["defence"],
        )

        return int(
            cls._get_avg(
                strongest_melee.level,
                skills["ranged"].level,
                skills["magic"].level,
            )
        )

    @classmethod
    def get_non_combat_skills(
        cls,
        hiscore: Hiscore,
        n_highest: int = 3,
    ) -> List[Skill]:
        """Return the highest-XP non-combat skills."""
        skills = [
            hiscore.skills.get(skill_name)
            for skill_name in cls.NON_COMBAT_SKILLS
        ]

        return cls.get_max_skills(*skills, n_highest=n_highest)

    @classmethod
    def get_non_combat_avg(
        cls,
        hiscore: Hiscore,
        n_highest: int = 3,
    ) -> int:
        """Return the average level of the highest non-combat skills."""
        skills = cls.get_non_combat_skills(
            hiscore,
            n_highest=n_highest,
        )

        return int(cls._get_avg(*(skill.level for skill in skills)))

    @staticmethod
    def get_max_skills(
        *skills: Skill,
        n_highest: int = 1,
    ) -> Skill | List[Skill]:
        """Return the skill(s) with the highest XP."""
        skills_sorted = sorted(
            skills,
            key=lambda skill: skill.xp,
            reverse=True,
        )

        if n_highest == 1:
            return skills_sorted[0]

        return skills_sorted[:n_highest]

    @staticmethod
    def _get_avg(*values: float) -> float:
        return sum(values) / len(values)

rank_service: RankService = RankService()
