import pathlib
import re


header = \
"""\"\"\"
###########################################################

AUTO-GENERATED AUTO-GENERATED AUTO-GENERATED AUTO-GENERATED

###########################################################
\"\"\"

import re
"""

def make_init_vars(var_lst, var_val_lst):
    return f"\n{' '*8}".join([f"self._{var_lst[i]} = {var_val_lst[i]}" for i in range(len(var_lst))])

def make_getter(var):
    return \
f"""    @property
    def {var}(self):
        return self._{var}
"""

def make_setter(var):
    return \
f"""    @{var}.setter
    def {var}(self, value):
        self._{var} = value
"""


def make_get_function(mdata_list):
    return \
f"""    def get(self, key):
        def __convert_to_var_name(name):
            alnum_only = "".join([c.lower() for c in name if c.isalnum() or c.isspace()])
            remove_dup_spaces = re.sub(r'\s+', '_', alnum_only)
            return "_"+remove_dup_spaces.strip()
        if key not in {mdata_list}:
            return None
        return self.__dict__[__convert_to_var_name(key)]
"""

def make_class(class_name,
               init_params,
               init_val_vars,
               getters,
               setters=None,
               set_init_params=False,
               coll_get_fn=None):
    init_params_str = ''
    self_init_vars = ''
    if set_init_params:
        init_params_str = ','.join(init_params)
    
    self_init_vars = make_init_vars(init_params, init_val_vars)
    getters_str = '\n'.join(getters) if getters else ''
    setters_str = '\n'.join(setters) if setters else ''

    return \
f"""
class {class_name}:
    def __init__(self,{init_params_str}):
        {self_init_vars}

{getters_str}
{setters_str}    
    def __str__(self):
        return f\"{class_name}({{[str(v) for v in self.__dict__.values()]}})\"

{coll_get_fn if coll_get_fn else ''}"""

SKILLS = [
    "attack", "defence", "strength",
    "hitpoints", "ranged", "prayer",
    "magic", "cooking", "woodcutting",
    "fletching", "fishing", "firemaking",
    "crafting", "smithing", "mining",
    "herblore", "agility", "thieving",
    "slayer", "farming", "runecrafting",
    "hunter", "construction"
]

ACTIVITIES = [
    "League Points", "Deadman Points",
    "Bounty Hunter - Hunter", "Bounty Hunter - Rogue",
    "Bounty Hunter (Legacy) - Hunter", "Bounty Hunter (Legacy) - Rogue",
    "Clue Scrolls (all)", "Clue Scrolls (beginner)", "Clue Scrolls (easy)",
    "Clue Scrolls (medium)", "Clue Scrolls (hard)", "Clue Scrolls (elite)", "Clue Scrolls (master)",
    "LMS - Rank", "PvP Arena - Rank", "Soul Wars Zeal", "Rifts closed", "Colosseum Glory"
]

BOSSES = [
    "Abyssal Sire", "Alchemical Hydra", "Artio",
    "Barrows Chests", "Bryophyta",
    "Callisto", "Cal'varion", "Cerberus", 
    "Chambers of Xeric", "Chambers of Xeric: Challenge Mode", 
    "Chaos Elemental", "Chaos Fanatic", "Commander Zilyana",
    "Corporeal Beast", "Crazy Archaeologist",
    "Dagannoth Prime", "Dagannoth Rex", "Dagannoth Supreme",
    "Deranged Archaeologist", "Duke Sucellus",
    "General Graardor", "Giant Mole",
    "Grotesque Guardians", "Hespori",
    "Kalphite Queen", "King Black Dragon", "Kraken",
    "Kree'Arra", "K'ril Tsutsaroth",
    "Lunar Chests", "Mimic",
    "Nex", "Nightmare", "Phosani's Nightmare",
    "Obor", "Phantom Muspah",
    "Sarachnis", "Scorpia", "Scurrius", "Skotizo", "Sol Heredit", "Spindel",
    "Tempoross", "The Gauntlet", "The Corrupted Gauntlet",
    "The Leviathan", "The Whisperer",
    "Theatre of Blood", "Theatre of Blood: Hard Mode", "Thermonuclear Smoke Devil",
    "Tombs of Amascut", "Tombs of Amascut: Expert Mode",
    "TzKal-Zuk", "TzTok-Jad", "Vardorvis", "Venenatis", "Vet'ion", "Vorkath",
    "Wintertodt", "Zalcano", "Zulrah",
]


def generate_mdata_list(name, mdata_lst):
    mdata_str = '\n\t'.join([f"\"{mdata}\"," for mdata in mdata_lst])
    return f"{name} = [\n\t{mdata_str}\n]\n"

def convert_to_var_name(name):
    alnum_only = "".join([c.lower() for c in name if c.isalnum() or c.isspace()])
    remove_dup_spaces = re.sub(r'\s+', '_', alnum_only)
    return remove_dup_spaces.strip()

generated_file_names = {
    "skills": {
        "mdata_list": SKILLS,
        "mdata_base_cls": {
            "mdata_base_name": "Skill",
            "vars":["name", "level", "rank", "xp"],
            "setters": [False, True, True, True],
            "init_call_fn": lambda name : f"Skill(\"{name}\", 1, -1, -1)"
        }
    },
    "activities": {
        "mdata_list": ACTIVITIES, 
        "mdata_base_cls": {
            "mdata_base_name": "Activity",
            "vars": ["name", "score", "rank"],
            "setters": [False, True, True],
            "init_call_fn": lambda name : f"Activity(\"{name}\", -1, -1)"
        }
    },
    "bosses": {
        "mdata_list": BOSSES,
        "mdata_base_cls": {
            "mdata_base_name": "Boss",
            "vars": ["name", "score", "rank"],
            "setters": [False, True, True],
            "init_call_fn": lambda name : f"Boss(\"{name}\", -1, -1)"
        }
    }
}

if __name__ == "__main__":
    for name in generated_file_names:
        vals = generated_file_names[name]
        mdata_list = vals["mdata_list"]

        mdata_base_cls = vals["mdata_base_cls"]
        mdata_base_name = mdata_base_cls["mdata_base_name"]
        mdata_base_vars = mdata_base_cls["vars"]
        mdata_base_setters = mdata_base_cls["setters"]
        mdata_init_vars_fn = mdata_base_cls["init_call_fn"]

        pyfile = str(pathlib.Path(__file__).parent.absolute()) + f"/{name}.py"
        with open(pyfile, "w") as pyf:
            # Base class
            base_getters = [make_getter(mdata) for mdata in mdata_base_vars]
            base_setters = [make_setter(mdata_base_vars[idx]) for idx in range(len(mdata_base_vars)) if mdata_base_setters[idx]]

            # Base Collection class
            coll_vars = [convert_to_var_name(v) for v in mdata_list]
            coll_vars_vals = [mdata_init_vars_fn(v) for v in mdata_list]
            coll_getters = [make_getter(v) for v in coll_vars]
            get_fn = make_get_function(name.upper())

            # Bring it all together into one file
            pyf.write(header)
            pyf.write(make_class(mdata_base_name, mdata_base_vars, mdata_base_vars, base_getters, base_setters, set_init_params=True))
            pyf.write(generate_mdata_list(name.upper(), mdata_list))
            pyf.write(make_class(name.capitalize(), coll_vars, coll_vars_vals, coll_getters,coll_get_fn=get_fn))
