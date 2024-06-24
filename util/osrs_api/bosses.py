"""
###########################################################

AUTO-GENERATED AUTO-GENERATED AUTO-GENERATED AUTO-GENERATED

###########################################################
"""

import re

class Boss:
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
        return f"Boss({[str(v) for v in self.__dict__.values()]})"

BOSSES = [
	"Abyssal Sire",
	"Alchemical Hydra",
	"Artio",
	"Barrows Chests",
	"Bryophyta",
	"Callisto",
	"Cal'varion",
	"Cerberus",
	"Chambers of Xeric",
	"Chambers of Xeric: Challenge Mode",
	"Chaos Elemental",
	"Chaos Fanatic",
	"Commander Zilyana",
	"Corporeal Beast",
	"Crazy Archaeologist",
	"Dagannoth Prime",
	"Dagannoth Rex",
	"Dagannoth Supreme",
	"Deranged Archaeologist",
	"Duke Sucellus",
	"General Graardor",
	"Giant Mole",
	"Grotesque Guardians",
	"Hespori",
	"Kalphite Queen",
	"King Black Dragon",
	"Kraken",
	"Kree'Arra",
	"K'ril Tsutsaroth",
	"Lunar Chests",
	"Mimic",
	"Nex",
	"Nightmare",
	"Phosani's Nightmare",
	"Obor",
	"Phantom Muspah",
	"Sarachnis",
	"Scorpia",
	"Scurrius",
	"Skotizo",
	"Sol Heredit",
	"Spindel",
	"Tempoross",
	"The Gauntlet",
	"The Corrupted Gauntlet",
	"The Leviathan",
	"The Whisperer",
	"Theatre of Blood",
	"Theatre of Blood: Hard Mode",
	"Thermonuclear Smoke Devil",
	"Tombs of Amascut",
	"Tombs of Amascut: Expert Mode",
	"TzKal-Zuk",
	"TzTok-Jad",
	"Vardorvis",
	"Venenatis",
	"Vet'ion",
	"Vorkath",
	"Wintertodt",
	"Zalcano",
	"Zulrah",
]

class Bosses:
    def __init__(self,):
        self._abyssal_sire = Boss("Abyssal Sire", -1, -1)
        self._alchemical_hydra = Boss("Alchemical Hydra", -1, -1)
        self._artio = Boss("Artio", -1, -1)
        self._barrows_chests = Boss("Barrows Chests", -1, -1)
        self._bryophyta = Boss("Bryophyta", -1, -1)
        self._callisto = Boss("Callisto", -1, -1)
        self._calvarion = Boss("Cal'varion", -1, -1)
        self._cerberus = Boss("Cerberus", -1, -1)
        self._chambers_of_xeric = Boss("Chambers of Xeric", -1, -1)
        self._chambers_of_xeric_challenge_mode = Boss("Chambers of Xeric: Challenge Mode", -1, -1)
        self._chaos_elemental = Boss("Chaos Elemental", -1, -1)
        self._chaos_fanatic = Boss("Chaos Fanatic", -1, -1)
        self._commander_zilyana = Boss("Commander Zilyana", -1, -1)
        self._corporeal_beast = Boss("Corporeal Beast", -1, -1)
        self._crazy_archaeologist = Boss("Crazy Archaeologist", -1, -1)
        self._dagannoth_prime = Boss("Dagannoth Prime", -1, -1)
        self._dagannoth_rex = Boss("Dagannoth Rex", -1, -1)
        self._dagannoth_supreme = Boss("Dagannoth Supreme", -1, -1)
        self._deranged_archaeologist = Boss("Deranged Archaeologist", -1, -1)
        self._duke_sucellus = Boss("Duke Sucellus", -1, -1)
        self._general_graardor = Boss("General Graardor", -1, -1)
        self._giant_mole = Boss("Giant Mole", -1, -1)
        self._grotesque_guardians = Boss("Grotesque Guardians", -1, -1)
        self._hespori = Boss("Hespori", -1, -1)
        self._kalphite_queen = Boss("Kalphite Queen", -1, -1)
        self._king_black_dragon = Boss("King Black Dragon", -1, -1)
        self._kraken = Boss("Kraken", -1, -1)
        self._kreearra = Boss("Kree'Arra", -1, -1)
        self._kril_tsutsaroth = Boss("K'ril Tsutsaroth", -1, -1)
        self._lunar_chests = Boss("Lunar Chests", -1, -1)
        self._mimic = Boss("Mimic", -1, -1)
        self._nex = Boss("Nex", -1, -1)
        self._nightmare = Boss("Nightmare", -1, -1)
        self._phosanis_nightmare = Boss("Phosani's Nightmare", -1, -1)
        self._obor = Boss("Obor", -1, -1)
        self._phantom_muspah = Boss("Phantom Muspah", -1, -1)
        self._sarachnis = Boss("Sarachnis", -1, -1)
        self._scorpia = Boss("Scorpia", -1, -1)
        self._scurrius = Boss("Scurrius", -1, -1)
        self._skotizo = Boss("Skotizo", -1, -1)
        self._sol_heredit = Boss("Sol Heredit", -1, -1)
        self._spindel = Boss("Spindel", -1, -1)
        self._tempoross = Boss("Tempoross", -1, -1)
        self._the_gauntlet = Boss("The Gauntlet", -1, -1)
        self._the_corrupted_gauntlet = Boss("The Corrupted Gauntlet", -1, -1)
        self._the_leviathan = Boss("The Leviathan", -1, -1)
        self._the_whisperer = Boss("The Whisperer", -1, -1)
        self._theatre_of_blood = Boss("Theatre of Blood", -1, -1)
        self._theatre_of_blood_hard_mode = Boss("Theatre of Blood: Hard Mode", -1, -1)
        self._thermonuclear_smoke_devil = Boss("Thermonuclear Smoke Devil", -1, -1)
        self._tombs_of_amascut = Boss("Tombs of Amascut", -1, -1)
        self._tombs_of_amascut_expert_mode = Boss("Tombs of Amascut: Expert Mode", -1, -1)
        self._tzkalzuk = Boss("TzKal-Zuk", -1, -1)
        self._tztokjad = Boss("TzTok-Jad", -1, -1)
        self._vardorvis = Boss("Vardorvis", -1, -1)
        self._venenatis = Boss("Venenatis", -1, -1)
        self._vetion = Boss("Vet'ion", -1, -1)
        self._vorkath = Boss("Vorkath", -1, -1)
        self._wintertodt = Boss("Wintertodt", -1, -1)
        self._zalcano = Boss("Zalcano", -1, -1)
        self._zulrah = Boss("Zulrah", -1, -1)

    @property
    def abyssal_sire(self):
        return self._abyssal_sire

    @property
    def alchemical_hydra(self):
        return self._alchemical_hydra

    @property
    def artio(self):
        return self._artio

    @property
    def barrows_chests(self):
        return self._barrows_chests

    @property
    def bryophyta(self):
        return self._bryophyta

    @property
    def callisto(self):
        return self._callisto

    @property
    def calvarion(self):
        return self._calvarion

    @property
    def cerberus(self):
        return self._cerberus

    @property
    def chambers_of_xeric(self):
        return self._chambers_of_xeric

    @property
    def chambers_of_xeric_challenge_mode(self):
        return self._chambers_of_xeric_challenge_mode

    @property
    def chaos_elemental(self):
        return self._chaos_elemental

    @property
    def chaos_fanatic(self):
        return self._chaos_fanatic

    @property
    def commander_zilyana(self):
        return self._commander_zilyana

    @property
    def corporeal_beast(self):
        return self._corporeal_beast

    @property
    def crazy_archaeologist(self):
        return self._crazy_archaeologist

    @property
    def dagannoth_prime(self):
        return self._dagannoth_prime

    @property
    def dagannoth_rex(self):
        return self._dagannoth_rex

    @property
    def dagannoth_supreme(self):
        return self._dagannoth_supreme

    @property
    def deranged_archaeologist(self):
        return self._deranged_archaeologist

    @property
    def duke_sucellus(self):
        return self._duke_sucellus

    @property
    def general_graardor(self):
        return self._general_graardor

    @property
    def giant_mole(self):
        return self._giant_mole

    @property
    def grotesque_guardians(self):
        return self._grotesque_guardians

    @property
    def hespori(self):
        return self._hespori

    @property
    def kalphite_queen(self):
        return self._kalphite_queen

    @property
    def king_black_dragon(self):
        return self._king_black_dragon

    @property
    def kraken(self):
        return self._kraken

    @property
    def kreearra(self):
        return self._kreearra

    @property
    def kril_tsutsaroth(self):
        return self._kril_tsutsaroth

    @property
    def lunar_chests(self):
        return self._lunar_chests

    @property
    def mimic(self):
        return self._mimic

    @property
    def nex(self):
        return self._nex

    @property
    def nightmare(self):
        return self._nightmare

    @property
    def phosanis_nightmare(self):
        return self._phosanis_nightmare

    @property
    def obor(self):
        return self._obor

    @property
    def phantom_muspah(self):
        return self._phantom_muspah

    @property
    def sarachnis(self):
        return self._sarachnis

    @property
    def scorpia(self):
        return self._scorpia

    @property
    def scurrius(self):
        return self._scurrius

    @property
    def skotizo(self):
        return self._skotizo

    @property
    def sol_heredit(self):
        return self._sol_heredit

    @property
    def spindel(self):
        return self._spindel

    @property
    def tempoross(self):
        return self._tempoross

    @property
    def the_gauntlet(self):
        return self._the_gauntlet

    @property
    def the_corrupted_gauntlet(self):
        return self._the_corrupted_gauntlet

    @property
    def the_leviathan(self):
        return self._the_leviathan

    @property
    def the_whisperer(self):
        return self._the_whisperer

    @property
    def theatre_of_blood(self):
        return self._theatre_of_blood

    @property
    def theatre_of_blood_hard_mode(self):
        return self._theatre_of_blood_hard_mode

    @property
    def thermonuclear_smoke_devil(self):
        return self._thermonuclear_smoke_devil

    @property
    def tombs_of_amascut(self):
        return self._tombs_of_amascut

    @property
    def tombs_of_amascut_expert_mode(self):
        return self._tombs_of_amascut_expert_mode

    @property
    def tzkalzuk(self):
        return self._tzkalzuk

    @property
    def tztokjad(self):
        return self._tztokjad

    @property
    def vardorvis(self):
        return self._vardorvis

    @property
    def venenatis(self):
        return self._venenatis

    @property
    def vetion(self):
        return self._vetion

    @property
    def vorkath(self):
        return self._vorkath

    @property
    def wintertodt(self):
        return self._wintertodt

    @property
    def zalcano(self):
        return self._zalcano

    @property
    def zulrah(self):
        return self._zulrah

    
    def __str__(self):
        return f"Bosses({[str(v) for v in self.__dict__.values()]})"

    def get(self, key):
        def __convert_to_var_name(name):
            alnum_only = "".join([c.lower() for c in name if c.isalnum() or c.isspace()])
            remove_dup_spaces = re.sub(r'\s+', '_', alnum_only)
            return "_"+remove_dup_spaces.strip()
        if key not in BOSSES:
            return None
        return self.__dict__[__convert_to_var_name(key)]
