
from datetime import datetime
from util.osrs_api import Hiscore, SKILLS as osrs_api_SKILLS
from entity import ClanMemberRankEnum, ClanMember
    
class RankService:

    MELEE_CMB_SKILLS = {"attack", "strength", "defence"}
    CMB_SKILLS = MELEE_CMB_SKILLS | {"ranged", "magic"}
    NON_CMB_SKILLS = set(osrs_api_SKILLS) - (CMB_SKILLS | {"hitpoints"})

    PROMO_RANK_2_REQ_AVG = 80
    TOLERANCE_DAYS = 2
    DAYS_PER_MONTH = 30
    
    def __init__(self, hiscore_data: Hiscore, clan_member: ClanMember):   
        self._hiscore_data = hiscore_data
        self._clan_member = clan_member

    def new_member_rank(self) -> ClanMemberRankEnum:
        """Place new member rank in either RANK_1 or RANK_2"""
        if self._hiscore_data is None:
            return ClanMemberRankEnum.RANK_1
        
        avg_cmb_lvl = self._get_cmb_skills_avg()
        avg_non_cmb_lvl = self._get_non_cmb_skills_avg()

        if ((avg_cmb_lvl >= self.PROMO_RANK_2_REQ_AVG) or
            (avg_non_cmb_lvl >= self.PROMO_RANK_2_REQ_AVG)):
           return ClanMemberRankEnum.RANK_2
        
        return ClanMemberRankEnum.RANK_1
    
    def get_next_rank(self) -> ClanMemberRankEnum:
        """Given the clan member's current, check and return the next rank"""       
        current_rank = self._clan_member.rank
        
        assert not current_rank == ClanMemberRankEnum.RANK_INVALID, "Clan member's rank is invalid"
        if ((current_rank == ClanMemberRankEnum.RANK_15)
            (current_rank in ClanMemberRankEnum.honorable_ranks_challenged()) or
            (current_rank in ClanMemberRankEnum.honorable_ranks_non_challenged()) or
            (current_rank in ClanMemberRankEnum.administrative_ranks())):
            return current_rank
        
        # Transition happens during Rank 1,2->3->4->5+
        # Promotion to honor/admin ranks are assigned by the admins only
        if (current_rank in ClanMemberRankEnum.activeness_ranks() and
            self._can_promote_next_active_rank()):
            if current_rank == ClanMemberRankEnum.RANK_4:
                return self._get_next_achieve_rank()
            elif current_rank in ClanMemberRankEnum.RANK_3:
                return ClanMemberRankEnum.RANK_4
            else:
                return ClanMemberRankEnum.RANK_3
        elif current_rank in ClanMemberRankEnum.achievement_ranks():
            return self._get_next_achieve_rank()
        else:
            return current_rank

    def _can_promote_next_active_rank(self) -> bool:
        """
        Promotion to next active rank - being in the clan for the next month
        Timezone isn't tracked with the joined date, so a tolerance is provided
        """
        joined_date = self._clan_member.joined_date
        days_diff = abs(datetime.now().date() - joined_date).days

        min_tolerance = self.DAYS_PER_MONTH - self.TOLERANCE_DAYS
        max_tolerance = self.DAYS_PER_MONTH + self.TOLERANCE_DAYS

        return (min_tolerance <= days_diff <= max_tolerance)
    
    def _get_next_achieve_rank(self) -> ClanMemberRankEnum:
        """Promotion to next achievement rank - based on the member's stats"""
        if not self._hiscore_data:
            return ClanMemberRankEnum.RANK_5
        
        cmb_avg = self._get_cmb_skills_avg()
        non_cmb_avg = self._get_non_cmb_skills_avg()

        def chk_avg_range_or(left_val, right_val):
            return ((left_val <= cmb_avg <= right_val) or
                    (left_val <= non_cmb_avg <= right_val))
        
        def chk_avg_range_and(left_val, right_val, non_cmb_avg_int=None):
            if not non_cmb_avg_int:
                non_cmb_avg_int = non_cmb_avg
            return ((left_val <= cmb_avg <= right_val) and
                    (left_val <= non_cmb_avg_int <= right_val))
        
        def chk_achieve_rank_14(left_val, right_val):
            non_cmb_avg = self._get_non_cmb_skills_avg(n_highest=6)
            return chk_avg_range_and(left_val, right_val, non_cmb_avg)
        
        def chk_achieve_rank_15(left_val, right_val):
            non_cmb_avg = self._get_non_cmb_skills_avg(n_highest=len(self.NON_CMB_SKILLS))
            return chk_avg_range_and(left_val, right_val, non_cmb_avg)

        achieve_rank_reqs = \
        (((0,69), chk_avg_range_or, ClanMemberRankEnum.RANK_5)
         ((70,74), chk_avg_range_or, ClanMemberRankEnum.RANK_6),
         ((75,79), chk_avg_range_or, ClanMemberRankEnum.RANK_7),
         ((80,84), chk_avg_range_or, ClanMemberRankEnum.RANK_8),
         ((85,89), chk_avg_range_or, ClanMemberRankEnum.RANK_9),
         ((90,94), chk_avg_range_or, ClanMemberRankEnum.RANK_10),
         ((95,98), chk_avg_range_or, ClanMemberRankEnum.RANK_11),
         ((99,99), chk_achieve_rank_15, ClanMemberRankEnum.RANK_15),
         ((99,99), chk_achieve_rank_14, ClanMemberRankEnum.RANK_14),
         ((99,99), chk_avg_range_and, ClanMemberRankEnum.RANK_13),
         ((99,99), chk_avg_range_or, ClanMemberRankEnum.RANK_12))

        for params, func, rank in achieve_rank_reqs:
            if func(*params):
                return rank

        return ClanMemberRankEnum.RANK_5

    def _get_cmb_skills_avg(self) -> int:
        """Get average combat skill levels from [max(attack, strength, defence), ranged, level]"""
        skills = self._hiscore_data.skills
        
        attack_lvl = skills.attack.level
        strength_lvl = skills.strength.level
        defence_lvl = skills.defence.level
        ranged_lvl = skills.ranged.level
        magic_lvl = skills.magic.level

        max_melee_lvl = max(attack_lvl, strength_lvl, defence_lvl)
        avg_cmb_lvl = self._get_avg(max_melee_lvl, ranged_lvl, magic_lvl)

        return int(avg_cmb_lvl)

    def _get_non_cmb_skills_avg(self, n_highest=3) -> int:
        """Get average of non-combat skill levels of n_highest skills"""
        skill_lvls = [(skill, self._hiscore_data.skills.get(skill)) for skill in self.NON_CMB_SKILLS]
        skill_lvls.sort(key=lambda item: item[1], reverse=True)

        highest_skills = skill_lvls[:n_highest]
        avg_non_cmb_lvl = self._get_avg(*highest_skills)

        return int(avg_non_cmb_lvl)

    @staticmethod
    def _get_avg(*args) -> float:
        return sum(args) / len(args)
