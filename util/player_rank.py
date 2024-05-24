import heapq
from util.osrs_api import *

class PlayerRankHandler:
    """Handles Rank Calculations for a clan member"""

    CMB_SKILLS = ['attack', 'defence', 'strength', 'magic', 'ranged']
    MELEE_CMB_SKILLS = ['attack', 'defence', 'strength']
    MOD_RANKS = ["A","D","O"]
    NEW_PLAYER_RANKS = [1, 2]
    ACTIVENESS_RANK_3 = 3
    ACTIVENESS_RANK_4 = 4
    ACTIVENESS_RANKS = [ACTIVENESS_RANK_3, ACTIVENESS_RANK_4]
    ACHIEVEMENT_RANK_10 = 10
    ACHIEVEMENT_RANKS = [5, 6, 7, 8, 9, ACHIEVEMENT_RANK_10]
    HONOR_RANKS = [11, 12, 13, 14] + MOD_RANKS

    def __init__(self, player) -> None:
        assert(isinstance(player, Hiscore))
        self.player: Hiscore = player

    def get_new_player_rank(self):
        max_levels_info = self.get_max_levels_info()
        if max_levels_info["rank"] >= 9:
            return 2
        return 1
        
    def get_max_levels_info(self):
        skills = {"combat": {}, "other": {}}

        for skill in SKILLS:
            if skill in self.CMB_SKILLS:
                skills["combat"][skill] = self.player.skills.get(skill).level
            elif skill != "hitpoints":
                skills["other"][skill] = self.player.skills.get(skill).level

        melee_lvls = [(name,skills["combat"][name]) for name in self.MELEE_CMB_SKILLS]
        melee_max_lvl = max(melee_lvls, key=lambda x: x[1])
        ranged_lvl = ("ranged", skills["combat"]["ranged"])
        magic_lvl = ("magic", skills["combat"]["magic"])
        cmb_avg = self.calc_avg(melee_max_lvl[1], ranged_lvl[1], magic_lvl[1])

        max_others = heapq.nlargest(3, skills["other"].items(), key=lambda x: x[1]) 
        others_avg = self.calc_avg(*[other[1] for other in max_others])        

        return ({
            "cmb": {"melee": melee_max_lvl, "ranged": ranged_lvl, "magic": magic_lvl},
            "other": {name:lvl for name,lvl in max_others},
            "avg": {"cmb": cmb_avg, "other": others_avg},
            "rank": max(cmb_avg//10, others_avg//10) + 1
        })

    @staticmethod
    def calc_avg(*args): 
        return sum(args)//len(args)
    
    @classmethod
    def player_hiscore_get(cls, player):
        try:
            p_hiscore = Hiscore(player, AccountTypes.NORMAL)
            return p_hiscore
        except Exception as e:
            return None

def sanitize_player_rank(rank):
    if str(rank).isnumeric():
        rank = int(rank)
    return rank
