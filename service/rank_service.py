
from datetime import datetime
from util.osrs_api import Hiscore, SKILLS as osrs_api_SKILLS
from entity import ClanMemberRank
    
class _RankService:

    MELEE_CMB_SKILLS = {"attack", "strength", "defence"}
    CMB_SKILLS = MELEE_CMB_SKILLS | {"ranged", "magic"}
    NON_CMB_SKILLS = set(osrs_api_SKILLS) - (CMB_SKILLS | {"hitpoints"})

    PROMO_RANK_2_REQ_AVG = 80
    TOLERANCE_DAYS = 1
    DAYS_PER_MONTH = 30
    
    def __init__(self):   
        if hasattr(self.__class__, "_has_instance"):
            raise RuntimeError("Cannot create another instance")
        self.__class__._has_instance = True            

    @classmethod
    def new_member_rank(cls, hiscore_data: Hiscore) -> ClanMemberRank:
        """Place new member rank in either RANK_1 or RANK_2"""
        if hiscore_data is None:
            return ClanMemberRank.RANK_1
        
        avg_cmb_lvl = cls._get_cmb_skills_avg(hiscore_data)
        avg_non_cmb_lvl = cls._get_non_cmb_skills_avg(hiscore_data)

        if ((avg_cmb_lvl >= cls.PROMO_RANK_2_REQ_AVG) or
            (avg_non_cmb_lvl >= cls.PROMO_RANK_2_REQ_AVG)):
           return ClanMemberRank.RANK_2
        
        return ClanMemberRank.RANK_1
    
    @classmethod
    def get_next_rank(cls, hiscore_data: Hiscore, current_rank: ClanMemberRank, current_joined_date: int) -> ClanMemberRank:
        """Given the clan member's current, check and return the next rank"""       
        assert not current_rank == ClanMemberRank.RANK_INVALID, "Clan member's rank is invalid"
        if ((current_rank == ClanMemberRank.RANK_15) or
            (current_rank in ClanMemberRank.honorable_ranks_challenged()) or
            (current_rank in ClanMemberRank.honorable_ranks_non_challenged()) or
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
        
        cmb_avg = cls._get_cmb_skills_avg(hiscore_data)
        non_cmb_avg = cls._get_non_cmb_skills_avg(hiscore_data)

        def chk_avg_range_or(left_val, right_val):
            max_avg = max(cmb_avg, non_cmb_avg)
            return left_val <= max_avg <= right_val
        
        def chk_avg_range_and(left_val, right_val, new_non_cmb_avg=None):
            global non_cmb_avg
            if new_non_cmb_avg:
                non_cmb_avg = new_non_cmb_avg
            return ((left_val <= cmb_avg <= right_val) and
                    (left_val <= non_cmb_avg <= right_val))
        
        def chk_achieve_rank_14(left_val, right_val):
            non_cmb_avg = cls._get_non_cmb_skills_avg(hiscore_data, n_highest=6)
            return chk_avg_range_and(left_val, right_val, non_cmb_avg)
        
        def chk_achieve_rank_15(left_val, right_val):
            non_cmb_avg = cls._get_non_cmb_skills_avg(hiscore_data, n_highest=len(cls.NON_CMB_SKILLS))
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
    def _get_cmb_skills_avg(cls, hiscore_data: Hiscore) -> int:
        """Get average combat skill levels from [max(attack, strength, defence), ranged, level]"""
        skills = hiscore_data.skills
        
        attack_lvl = skills.attack.level
        strength_lvl = skills.strength.level
        defence_lvl = skills.defence.level
        ranged_lvl = skills.ranged.level
        magic_lvl = skills.magic.level

        max_melee_lvl = max(attack_lvl, strength_lvl, defence_lvl)
        avg_cmb_lvl = cls._get_avg(max_melee_lvl, ranged_lvl, magic_lvl)

        return int(avg_cmb_lvl)

    @classmethod
    def _get_non_cmb_skills_avg(cls, hiscore_data: Hiscore, n_highest=3) -> int:
        """Get average of non-combat skill levels of n_highest skills"""
        skills = hiscore_data.skills
        skill_lvls = [skills.get(skill) for skill in cls.NON_CMB_SKILLS]
        skill_lvls.sort(key=lambda item: item.level, reverse=True)

        highest_skills = map(lambda s: s.level, skill_lvls[:n_highest])
        avg_non_cmb_lvl = cls._get_avg(*highest_skills)

        return int(avg_non_cmb_lvl)

    @staticmethod
    def _get_avg(*args) -> float:
        return sum(args) / len(args)

rank_service: _RankService = _RankService()
