import json
import os
from dataclasses import dataclass
from typing import List

from discord import Embed, Color
from entity import ClanMemberRank
from services import rank_service
from util import Skill, Hiscore
from resources import RANK_ICONS_JSON_PATH

skills_initials = {
	"attack": "att",
	"defence": "def",
	"strength": "str",
	"hitpoints": "hp",
	"ranged": "rgd",
	"prayer": "pry",
	"magic": "mag",
	"cooking": "ckg",
	"woodcutting": "wc",
	"fletching": "flc",
	"fishing": "fsh",
	"firemaking": "fmk",
	"crafting": "cft",
	"smithing": "smt",
	"mining": "min",
	"herblore": "hrb",
	"agility": "agi",
	"thieving": "thv",
	"slayer": "sly",
	"farming": "frm",
	"runecrafting": "rc",
	"hunter": "hnt",
	"construction": "con",
	"sailing": "sal",
}


@dataclass
class RankSkillStats:
    max_melee: Skill
    ranged_lvl: int
    magic_lvl: int
    cmb_avg: float
    max_non_cmb_skills: List[Skill]
    non_cmb_avg: float
    next_rank: str

class RankUtil:
    _rank_to_icon = dict()
    _last_mtime: float | None = None

    @classmethod
    def _load_data(cls):
        mtime = os.path.getmtime(RANK_ICONS_JSON_PATH)
        
        if cls._rank_to_icon and mtime == cls._last_mtime:
            return
        
        with open(RANK_ICONS_JSON_PATH, "r", encoding="utf-8") as jsonfp:
            data = json.load(jsonfp)
        
        uri_path = data["uri_path"]
        cls._rank_to_icon = {
            entry["rank"]: uri_path + entry["icon_path"]
            for entry in data["ranks"]
        }
        cls._last_mtime = mtime

    @classmethod
    def get_rank_icon_url(cls, rank: ClanMemberRank):
        cls._load_data()
        
        if rank not in cls._rank_to_icon:
            return cls._rank_to_icon["default"]
        return cls._rank_to_icon[rank]
    
    @classmethod
    def get_skill_stats(cls, member: str, rank: ClanMemberRank, joined_date: int) -> str:
        """Get skill stats - next rank, cmb avg, non-cmb avg"""
        try:
            hiscore = Hiscore(member)
            skills = hiscore.skills
        except Exception:
            hiscore = None
        
        next_rank = rank_service.get_next_rank(hiscore, rank, joined_date)
        next_rank_str = f"* **Next Rank**: {next_rank}"

        if not hiscore:
            return "\n".join([
                "**Hiscore data unavailable. Using default rank.**",
                next_rank_str
            ])

        max_melee = rank_service.get_max_skills(
            skills.attack, skills.strength, skills.defence
        )
        ranged_lvl = skills.ranged.level
        magic_lvl = skills.magic.level
        cmb_avg = (max_melee.level + ranged_lvl + magic_lvl) / 3
        cmb_avg_str = f"* **Cmb. Avg. ({max_melee.name.capitalize()}/Ranged/Magic**: {max_melee.level}/{ranged_lvl}/{magic_lvl} ->  {cmb_avg:.2f})"

        n_highest = 3
        match next_rank:
            case ClanMemberRank.RANK_14:    n_highest = 6
            case ClanMemberRank.RANK_15:    n_highest = len(rank_service.NON_CMB_SKILLS)
        max_non_cmb_skills = rank_service.get_non_cmb_skills(hiscore, n_highest=n_highest)
        non_cmb_avg = sum([sk.level for sk in max_non_cmb_skills]) / n_highest
        non_cmb_sk_lvls_str = "/".join(str(max(0,sk.level)) for sk in max_non_cmb_skills)
        if n_highest > 6:
            non_cmb_sk_names = "ALL"
        else:
            non_cmb_sk_names = "/".join([skills_initials[sk.name].capitalize() for sk in max_non_cmb_skills])
        non_cmb_avg_str = f"* **Non-Cmb. Avg. ({non_cmb_sk_names})**: {non_cmb_sk_lvls_str} -> {non_cmb_avg:.2f}"
        
        return "\n".join([
            cmb_avg_str,
            non_cmb_avg_str,
            next_rank_str
        ])


class EmbedUtil:   

    @classmethod
    def info_embed(cls, msg, title="Info"):
        return Embed(
            title=title,
            description=msg,
            color=Color.blue()
        )

    @classmethod
    def error_embed(cls, msg, title="Error"):
        return Embed(
            title=title,
            description=msg,
            color=Color.dark_red()
        )

class DiscordBotCommandMemberOptions:
    NEW = 0
    UPDATE = 1
    DELETE = 2
    CLAN_STATS = 3
