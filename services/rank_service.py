
from datetime import date
from dataclasses import dataclass
from typing import Dict, List

from util.osrs_api import Hiscore, SKILLS as osrs_api_SKILLS, Skill
from entity import ClanMemberRank


@dataclass(frozen=True)
class RankSkillStats:
    max_melee: Skill | None
    melee_level: int
    ranged_level: int
    magic_level: int
    combat_average: float
    non_combat_skills: List[Skill]
    non_combat_levels: List[int]
    non_combat_average: float
    all_non_combat: bool
    next_rank: str
    
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
        available = {}
        for name in osrs_api_SKILLS:
            skill = hiscore.skills.get(name)
            if (skill is not None and skill.level is not None and skill.xp is not None
                    and skill.level >= 0 and skill.xp >= 0):
                available[name] = skill

        if len(available) == len(osrs_api_SKILLS) and all(
            skill.level >= 99 for skill in available.values()
        ):
            return ClanMemberRank.RANK_15

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
        if combat_avg >= 99 and cls.get_non_combat_avg(hiscore, n_highest=6) >= 99:
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
        _, melee, ranged, magic = cls._combat_levels(hiscore)
        return int(cls._get_avg(melee, ranged, magic))

    @classmethod
    def _combat_levels(cls, hiscore: Hiscore):
        skills = cls.get_combat_skills(hiscore)

        def valid(skill):
            return (skill is not None and skill.level is not None and skill.xp is not None
                    and skill.level >= 0 and skill.xp >= 0)

        melee = [skills[name] for name in ("attack", "strength", "defence") if valid(skills[name])]
        strongest_melee = cls.get_max_skills(*melee) if melee else None
        ranged = skills["ranged"].level if valid(skills["ranged"]) else 0
        magic = skills["magic"].level if valid(skills["magic"]) else 0

        return strongest_melee, strongest_melee.level if strongest_melee else 0, ranged, magic

    @classmethod
    def get_non_combat_skills(
        cls,
        hiscore: Hiscore,
        n_highest: int = 3,
    ) -> List[Skill]:
        """Return the highest-XP non-combat skills."""
        if not 1 <= n_highest <= len(cls.NON_COMBAT_SKILLS):
            raise ValueError("Invalid number of non-combat skills")
        skills = [skill for name in cls.NON_COMBAT_SKILLS
                  if (skill := hiscore.skills.get(name)) is not None]
        return sorted(skills, key=lambda skill: skill.xp if skill.xp is not None else -1, reverse=True)[:n_highest]

    @classmethod
    def get_non_combat_avg(
        cls,
        hiscore: Hiscore,
        n_highest: int = 3,
    ) -> int:
        """Return the average level of the highest non-combat skills."""
        _, _, average = cls._non_combat_details(hiscore, n_highest)
        return int(average)

    @classmethod
    def _non_combat_details(cls, hiscore: Hiscore, n_highest: int):
        skills = cls.get_non_combat_skills(hiscore, n_highest=n_highest)
        levels = [max(skill.level, 0) if skill.level is not None else 0 for skill in skills]
        return skills, levels, sum(levels) / n_highest

    @classmethod
    def get_skill_stats(cls, hiscore: Hiscore, current_rank: ClanMemberRank, joined_date: int) -> RankSkillStats:
        """Return rank calculation details for presentation by a client."""
        next_rank = cls.get_next_rank(hiscore, current_rank, joined_date)
        max_melee, melee, ranged, magic = cls._combat_levels(hiscore)
        n_highest = 3
        if next_rank == ClanMemberRank.RANK_14:
            n_highest = 6
        elif next_rank == ClanMemberRank.RANK_15:
            n_highest = len(cls.NON_COMBAT_SKILLS)
        skills, levels, non_combat_average = cls._non_combat_details(hiscore, n_highest)
        return RankSkillStats(
            max_melee=max_melee, melee_level=melee, ranged_level=ranged,
            magic_level=magic, combat_average=cls._get_avg(melee, ranged, magic),
            non_combat_skills=skills, non_combat_levels=levels,
            non_combat_average=non_combat_average,
            all_non_combat=n_highest > 6, next_rank=next_rank,
        )

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
