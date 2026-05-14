
from datetime import datetime
from typing import Dict, List
from util.osrs_api import Hiscore, SKILLS as osrs_api_SKILLS, Skill
from entity import ClanMemberRank
    
class RankService:

    MELEE_CMB_SKILLS = {"attack", "strength", "defence"}
    CMB_SKILLS = MELEE_CMB_SKILLS | {"ranged", "magic"}
    NON_CMB_SKILLS = set(osrs_api_SKILLS) - (CMB_SKILLS | {"hitpoints"})

    PROMO_RANK_2_REQ_AVG = 80
    TOLERANCE_DAYS = 1
    DAYS_PER_MONTH = 30
    
    @classmethod
    def new_member_rank(cls, hiscore_data: Hiscore) -> ClanMemberRank:
        """Place new member rank in either RANK_1 or RANK_2"""
        if hiscore_data is None:
            return ClanMemberRank.RANK_1
        
        avg_cmb_lvl = cls.get_cmb_skills_avg(hiscore_data)
        avg_non_cmb_lvl = cls.get_non_cmb_skills_avg(hiscore_data)

        if ((avg_cmb_lvl >= cls.PROMO_RANK_2_REQ_AVG) or
            (avg_non_cmb_lvl >= cls.PROMO_RANK_2_REQ_AVG)):
           return ClanMemberRank.RANK_2
        
        return ClanMemberRank.RANK_1
    
    @classmethod
    def get_next_rank(cls, hiscore_data: Hiscore, current_rank: ClanMemberRank, current_joined_date: int) -> str:
        """Given the clan member's current, check and return the next rank"""       
        assert not current_rank == ClanMemberRank.RANK_INVALID, "Clan member's rank is invalid"
        if ((current_rank == ClanMemberRank.RANK_15) or
            (current_rank in ClanMemberRank.honorable_ranks()) or
            (current_rank in ClanMemberRank.administrative_ranks())):
            return current_rank
        
        # Transition happens during Rank 1,2->3->4->5+
        # Promotion to honor/admin ranks are assigned by the admins only
        if (current_rank in ClanMemberRank.activeness_ranks() and
            cls._can_promote_next_active_rank(current_joined_date)):
            if current_rank == ClanMemberRank.RANK_4:
                return cls._get_next_achieve_rank(hiscore_data)
            elif current_rank in ClanMemberRank.RANK_3:
                return ClanMemberRank.RANK_4
            else:
                return ClanMemberRank.RANK_3
        elif current_rank in ClanMemberRank.achievement_ranks():
            return cls._get_next_achieve_rank(hiscore_data)
        else:
            return current_rank

    @classmethod
    def _can_promote_next_active_rank(cls, joined_date: int) -> bool:
        """
        Promotion to next active rank - being in the clan for the next month
        Timezone isn't tracked with the joined date, so a tolerance is provided
        """
        days_diff = abs(datetime.now().date() - datetime.fromordinal(joined_date).date()).days

        min_tolerance = cls.DAYS_PER_MONTH - cls.TOLERANCE_DAYS
        max_tolerance = cls.DAYS_PER_MONTH + cls.TOLERANCE_DAYS

        return (min_tolerance <= days_diff <= max_tolerance) or (days_diff >= max_tolerance)
    
    @classmethod
    def _get_next_achieve_rank(cls, hiscore_data: Hiscore) -> ClanMemberRank:
        """Promotion to next achievement rank - based on the member's stats"""
        if not hiscore_data:
            return ClanMemberRank.RANK_5
        
        cmb_avg = cls.get_cmb_skills_avg(hiscore_data)
        non_cmb_avg = cls.get_non_cmb_skills_avg(hiscore_data)

        def chk_avg_range_or(left_val, right_val):
            max_avg = max(cmb_avg, non_cmb_avg)
            return left_val <= max_avg <= right_val
        
        def chk_avg_range_and(left_val, right_val, new_non_cmb_avg=None):
            nonlocal non_cmb_avg
            if new_non_cmb_avg:
                non_cmb_avg = new_non_cmb_avg
            return ((left_val <= cmb_avg <= right_val) and
                    (left_val <= non_cmb_avg <= right_val))
        
        def chk_achieve_rank_14(left_val, right_val):
            non_cmb_avg = cls.get_non_cmb_skills_avg(hiscore_data, n_highest=6)
            return chk_avg_range_and(left_val, right_val, non_cmb_avg)
        
        def chk_achieve_rank_15(left_val, right_val):
            non_cmb_avg = cls.get_non_cmb_skills_avg(hiscore_data, n_highest=len(cls.NON_CMB_SKILLS))
            return chk_avg_range_and(left_val, right_val, non_cmb_avg)

        achieve_rank_reqs = \
        (((0,69), chk_avg_range_or, ClanMemberRank.RANK_5),
         ((70,74), chk_avg_range_or, ClanMemberRank.RANK_6),
         ((75,79), chk_avg_range_or, ClanMemberRank.RANK_7),
         ((80,84), chk_avg_range_or, ClanMemberRank.RANK_8),
         ((85,89), chk_avg_range_or, ClanMemberRank.RANK_9),
         ((90,94), chk_avg_range_or, ClanMemberRank.RANK_10),
         ((95,98), chk_avg_range_or, ClanMemberRank.RANK_11),
         ((99,99), chk_achieve_rank_15, ClanMemberRank.RANK_15),
         ((99,99), chk_achieve_rank_14, ClanMemberRank.RANK_14),
         ((99,99), chk_avg_range_and, ClanMemberRank.RANK_13),
         ((99,99), chk_avg_range_or, ClanMemberRank.RANK_12))

        for params, func, rank in achieve_rank_reqs:
            if func(*params):
                return rank

        return ClanMemberRank.RANK_5

    @classmethod
    def get_cmb_skills(cls, hiscore_data: Hiscore) -> Dict[str, Skill]:
        """Get dict of combat skills"""
        skills = hiscore_data.skills
        attack = skills.attack
        strength = skills.strength
        defence = skills.defence

        return {
            "attack": attack,
            "strength": strength,
            "defence": defence,
            "ranged": skills.ranged,
            "magic": skills.magic,
        }
    
    @classmethod
    def get_cmb_skills_avg(cls, hiscore_data: Hiscore) -> int:
        """Get average combat skill levels from [max(attack, strength, defence), ranged, level]"""
        cmb_skills = cls.get_cmb_skills(hiscore_data)
        attack = cmb_skills["attack"]
        strength = cmb_skills["strength"]
        defence = cmb_skills["defence"]
        ranged = cmb_skills["ranged"]
        magic = cmb_skills["magic"]

        max_melee_skill = cls.get_max_skills(attack, strength, defence, n_highest=1)
        avg_cmb_lvl = cls._get_avg(max_melee_skill.level, ranged.level, magic.level)

        return int(avg_cmb_lvl)

    @classmethod
    def get_non_cmb_skills(cls, hiscore_data: Hiscore, n_highest=3) -> List[Skill]:
        """Get n_highest non-combat skills"""
        skills = [hiscore_data.skills.get(non_cmb_sk) for non_cmb_sk in cls.NON_CMB_SKILLS]
        return cls.get_max_skills(*skills, n_highest=n_highest)

    @classmethod
    def get_non_cmb_skills_avg(cls, hiscore_data: Hiscore, n_highest=3) -> int:
        """Get average of non-combat skill levels of n_highest skills"""
        highest_skills = cls.get_non_cmb_skills(hiscore_data, n_highest=n_highest)
        avg_non_cmb_lvl = cls._get_avg(*map(lambda sk: sk.level, highest_skills))
        return int(avg_non_cmb_lvl)

    @staticmethod
    def get_max_skills(*skills, n_highest=1) -> Skill|List[Skill]:
        """Compare skills and return the max skill or list of max skills"""
        skills_sorted = sorted(skills, key=lambda sk: sk.xp, reverse=True)
        if n_highest == 1:
            return skills_sorted[0]
        return skills_sorted[:min(len(osrs_api_SKILLS), n_highest)]

    @staticmethod
    def _get_avg(*args) -> float:
        return sum(args) / len(args)

rank_service: RankService = RankService()
