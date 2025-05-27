"""
###########################################################

AUTO-GENERATED AUTO-GENERATED AUTO-GENERATED AUTO-GENERATED

###########################################################
"""

import re

class Skill:
    def __init__(self,name,level,rank,xp):
        self._name = name
        self._level = level
        self._rank = rank
        self._xp = xp

    @property
    def name(self):
        return self._name

    @property
    def level(self):
        return self._level

    @property
    def rank(self):
        return self._rank

    @property
    def xp(self):
        return self._xp

    @level.setter
    def level(self, value):
        self._level = value

    @rank.setter
    def rank(self, value):
        self._rank = value

    @xp.setter
    def xp(self, value):
        self._xp = value
    
    def __str__(self):
        return f"Skill({[str(v) for v in self.__dict__.values()]})"

SKILLS = [
	"attack",
	"defence",
	"strength",
	"hitpoints",
	"ranged",
	"prayer",
	"magic",
	"cooking",
	"woodcutting",
	"fletching",
	"fishing",
	"firemaking",
	"crafting",
	"smithing",
	"mining",
	"herblore",
	"agility",
	"thieving",
	"slayer",
	"farming",
	"runecrafting",
	"hunter",
	"construction",
]

class Skills:
    def __init__(self,):
        self._attack = Skill("attack", 1, -1, -1)
        self._defence = Skill("defence", 1, -1, -1)
        self._strength = Skill("strength", 1, -1, -1)
        self._hitpoints = Skill("hitpoints", 1, -1, -1)
        self._ranged = Skill("ranged", 1, -1, -1)
        self._prayer = Skill("prayer", 1, -1, -1)
        self._magic = Skill("magic", 1, -1, -1)
        self._cooking = Skill("cooking", 1, -1, -1)
        self._woodcutting = Skill("woodcutting", 1, -1, -1)
        self._fletching = Skill("fletching", 1, -1, -1)
        self._fishing = Skill("fishing", 1, -1, -1)
        self._firemaking = Skill("firemaking", 1, -1, -1)
        self._crafting = Skill("crafting", 1, -1, -1)
        self._smithing = Skill("smithing", 1, -1, -1)
        self._mining = Skill("mining", 1, -1, -1)
        self._herblore = Skill("herblore", 1, -1, -1)
        self._agility = Skill("agility", 1, -1, -1)
        self._thieving = Skill("thieving", 1, -1, -1)
        self._slayer = Skill("slayer", 1, -1, -1)
        self._farming = Skill("farming", 1, -1, -1)
        self._runecrafting = Skill("runecrafting", 1, -1, -1)
        self._hunter = Skill("hunter", 1, -1, -1)
        self._construction = Skill("construction", 1, -1, -1)

    @property
    def attack(self):
        return self._attack

    @property
    def defence(self):
        return self._defence

    @property
    def strength(self):
        return self._strength

    @property
    def hitpoints(self):
        return self._hitpoints

    @property
    def ranged(self):
        return self._ranged

    @property
    def prayer(self):
        return self._prayer

    @property
    def magic(self):
        return self._magic

    @property
    def cooking(self):
        return self._cooking

    @property
    def woodcutting(self):
        return self._woodcutting

    @property
    def fletching(self):
        return self._fletching

    @property
    def fishing(self):
        return self._fishing

    @property
    def firemaking(self):
        return self._firemaking

    @property
    def crafting(self):
        return self._crafting

    @property
    def smithing(self):
        return self._smithing

    @property
    def mining(self):
        return self._mining

    @property
    def herblore(self):
        return self._herblore

    @property
    def agility(self):
        return self._agility

    @property
    def thieving(self):
        return self._thieving

    @property
    def slayer(self):
        return self._slayer

    @property
    def farming(self):
        return self._farming

    @property
    def runecrafting(self):
        return self._runecrafting

    @property
    def hunter(self):
        return self._hunter

    @property
    def construction(self):
        return self._construction

    
    def __str__(self):
        return f"Skills({[str(v) for v in self.__dict__.values()]})"

    def get(self, key):
        def __convert_to_var_name(name):
            alnum_only = "".join([c.lower() for c in name if c.isalnum() or c.isspace()])
            remove_dup_spaces = re.sub(r'\s+', '_', alnum_only)
            return "_"+remove_dup_spaces.strip()
        if key not in SKILLS:
            return None
        return self.__dict__[__convert_to_var_name(key)]
