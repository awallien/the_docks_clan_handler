
from datetime import date, datetime
from typing import Dict, List

from util.osrs_api import Hiscore, SKILLS as osrs_api_SKILLS, Skill
from entity import ClanMemberRank
    
class RankService:

    MELEE_CMB_SKILLS = {"attack", "strength", "defence"}
    CMB_SKILLS = MELEE_CMB_SKILLS | {"ranged", "magic"}
    NON_COMBAT_SKILLS = set(osrs_api_SKILLS) - (CMB_SKILLS | {"hitpoints"})

    RANK_2_AVG_REQUIREMENT = 80
    DATE_TOLERANCE_DAYS = 1
    DAYS_PER_MONTH = 30
    
    @classmethod
    def new_member_rank(cls, hiscore_data: Hiscore) -> ClanMemberRank:
        """Place new member rank in either RANK_1 or RANK_2"""
        if hiscore_data is None:
            return ClanMemberRank.RANK_1
        
        combat_avg = cls.get_combat_avg(hiscore_data)
        non_combat_avg = cls.get_non_combat_avg(hiscore_data)

        if max(combat_avg, non_combat_avg) >= cls.RANK_2_AVG_REQUIREMENT:
           return ClanMemberRank.RANK_2
        
        return ClanMemberRank.RANK_1
    
    @classmethod
    def get_next_rank(
        cls,
        hiscore: Hiscore | None,
        current_rank: ClanMemberRank,
        joined_date: int,
    ) -> ClanMemberRank:
        """Return the next rank a member currently qualifies for."""

        if current_rank == ClanMemberRank.RANK_INVALID:
            raise ValueError("Clan member's rank is invalid")

        # Honorary/admin ranks and RANK_15 do not auto-promote.
        if (
            current_rank == ClanMemberRank.RANK_15
            or current_rank in ClanMemberRank.honorable_ranks()
            or current_rank in ClanMemberRank.administrative_ranks()
        ):
            return current_rank

        # Active-rank progression is time-based.
        if current_rank in ClanMemberRank.activeness_ranks():
            if not cls._has_been_active_long_enough(joined_date):
                return current_rank

            active_rank_progression = {
                ClanMemberRank.RANK_1: ClanMemberRank.RANK_3,
                ClanMemberRank.RANK_2: ClanMemberRank.RANK_3,
                ClanMemberRank.RANK_3: ClanMemberRank.RANK_4,
            }

            if current_rank in active_rank_progression:
                return active_rank_progression[current_rank]

            # RANK_4 transitions into achievement ranks.
            if current_rank == ClanMemberRank.RANK_4:
                return cls._get_next_achievement_rank(hiscore)

        if current_rank in ClanMemberRank.achievement_ranks():
            return cls._get_next_achievement_rank(hiscore)

        return current_rank

    @classmethod
    def _has_been_active_long_enough(cls, joined_date: int) -> bool:
        """
        Return whether enough time has passed for the next activity promotion.

        joined_date is stored as an ordinal. A small tolerance is allowed
        because the stored date does not include timezone information.
        """
        joined = datetime.fromordinal(joined_date).date()
        days_since_join = (date.today() - joined).days

        minimum_days = cls.DAYS_PER_MONTH - cls.DATE_TOLERANCE_DAYS

        return days_since_join >= minimum_days
    
    @classmethod
    def _get_next_achievement_rank(
        cls,
        hiscore: Hiscore | None,
    ) -> ClanMemberRank:
        """Return the highest achievement rank currently qualified for."""
        if hiscore is None:
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
        if combat_avg == 99 and cls.get_non_combat_avg(
            hiscore,
            n_highest=len(cls.NON_COMBAT_SKILLS),
        ) == 99:
            return ClanMemberRank.RANK_15

        if combat_avg == 99 and cls.get_non_combat_avg(
            hiscore,
            n_highest=6,
        ) == 99:
            return ClanMemberRank.RANK_14

        if combat_avg == 99 and non_combat_avg == 99:
            return ClanMemberRank.RANK_13

        if highest_avg == 99:
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
