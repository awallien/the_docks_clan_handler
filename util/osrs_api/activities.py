"""
###########################################################

AUTO-GENERATED AUTO-GENERATED AUTO-GENERATED AUTO-GENERATED

###########################################################
"""

import re

class Activity:
    def __init__(self,name,score,rank):
        self._name = name
        self._score = score
        self._rank = rank

    @property
    def name(self):
        return self._name

    @property
    def score(self):
        return self._score

    @property
    def rank(self):
        return self._rank

    @score.setter
    def score(self, value):
        self._score = value

    @rank.setter
    def rank(self, value):
        self._rank = value
    
    def __str__(self):
        return f"Activity({[str(v) for v in self.__dict__.values()]})"

ACTIVITIES = [
	"League Points",
	"Deadman Points",
	"Bounty Hunter - Hunter",
	"Bounty Hunter - Rogue",
	"Bounty Hunter (Legacy) - Hunter",
	"Bounty Hunter (Legacy) - Rogue",
	"Clue Scrolls (all)",
	"Clue Scrolls (beginner)",
	"Clue Scrolls (easy)",
	"Clue Scrolls (medium)",
	"Clue Scrolls (hard)",
	"Clue Scrolls (elite)",
	"Clue Scrolls (master)",
	"LMS - Rank",
	"PvP Arena - Rank",
	"Soul Wars Zeal",
	"Rifts closed",
	"Colosseum Glory",
]

class Activities:
    def __init__(self,):
        self._league_points = Activity("League Points", -1, -1)
        self._deadman_points = Activity("Deadman Points", -1, -1)
        self._bounty_hunter_hunter = Activity("Bounty Hunter - Hunter", -1, -1)
        self._bounty_hunter_rogue = Activity("Bounty Hunter - Rogue", -1, -1)
        self._bounty_hunter_legacy_hunter = Activity("Bounty Hunter (Legacy) - Hunter", -1, -1)
        self._bounty_hunter_legacy_rogue = Activity("Bounty Hunter (Legacy) - Rogue", -1, -1)
        self._clue_scrolls_all = Activity("Clue Scrolls (all)", -1, -1)
        self._clue_scrolls_beginner = Activity("Clue Scrolls (beginner)", -1, -1)
        self._clue_scrolls_easy = Activity("Clue Scrolls (easy)", -1, -1)
        self._clue_scrolls_medium = Activity("Clue Scrolls (medium)", -1, -1)
        self._clue_scrolls_hard = Activity("Clue Scrolls (hard)", -1, -1)
        self._clue_scrolls_elite = Activity("Clue Scrolls (elite)", -1, -1)
        self._clue_scrolls_master = Activity("Clue Scrolls (master)", -1, -1)
        self._lms_rank = Activity("LMS - Rank", -1, -1)
        self._pvp_arena_rank = Activity("PvP Arena - Rank", -1, -1)
        self._soul_wars_zeal = Activity("Soul Wars Zeal", -1, -1)
        self._rifts_closed = Activity("Rifts closed", -1, -1)
        self._colosseum_glory = Activity("Colosseum Glory", -1, -1)

    @property
    def league_points(self):
        return self._league_points

    @property
    def deadman_points(self):
        return self._deadman_points

    @property
    def bounty_hunter_hunter(self):
        return self._bounty_hunter_hunter

    @property
    def bounty_hunter_rogue(self):
        return self._bounty_hunter_rogue

    @property
    def bounty_hunter_legacy_hunter(self):
        return self._bounty_hunter_legacy_hunter

    @property
    def bounty_hunter_legacy_rogue(self):
        return self._bounty_hunter_legacy_rogue

    @property
    def clue_scrolls_all(self):
        return self._clue_scrolls_all

    @property
    def clue_scrolls_beginner(self):
        return self._clue_scrolls_beginner

    @property
    def clue_scrolls_easy(self):
        return self._clue_scrolls_easy

    @property
    def clue_scrolls_medium(self):
        return self._clue_scrolls_medium

    @property
    def clue_scrolls_hard(self):
        return self._clue_scrolls_hard

    @property
    def clue_scrolls_elite(self):
        return self._clue_scrolls_elite

    @property
    def clue_scrolls_master(self):
        return self._clue_scrolls_master

    @property
    def lms_rank(self):
        return self._lms_rank

    @property
    def pvp_arena_rank(self):
        return self._pvp_arena_rank

    @property
    def soul_wars_zeal(self):
        return self._soul_wars_zeal

    @property
    def rifts_closed(self):
        return self._rifts_closed

    @property
    def colosseum_glory(self):
        return self._colosseum_glory

    
    def __str__(self):
        return f"Activities({[str(v) for v in self.__dict__.values()]})"

    def get(self, key):
        def __convert_to_var_name(name):
            alnum_only = "".join([c.lower() for c in name if c.isalnum() or c.isspace()])
            remove_dup_spaces = re.sub(r'\s+', '_', alnum_only)
            return "_"+remove_dup_spaces.strip()
        if key not in ACTIVITIES:
            return None
        return self.__dict__[__convert_to_var_name(key)]
