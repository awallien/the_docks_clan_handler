import json
import os
from discord import Embed, Color
from entity import ClanMemberRank
from services import rank_service
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
    def get_skill_stats(cls, hiscore, rank: ClanMemberRank, joined_date: int) -> str:
        """Get skill stats - next rank, cmb avg, non-cmb avg"""
        if not hiscore:
            return "**No successful current hiscore refresh is available.**"
        stats = rank_service.get_skill_stats(hiscore, rank, joined_date)
        next_rank_str = f"* **Next Rank**: {stats.next_rank}"
        melee_name = stats.max_melee.name.capitalize() if stats.max_melee else "Melee"
        cmb_avg_str = (f"* **Cmb. Avg. ({melee_name}/Ranged/Magic)**: "
                       f"{stats.melee_level}/{stats.ranged_level}/{stats.magic_level} -> {stats.combat_average:.2f}")

        non_cmb_sk_lvls_str = "/".join(str(level) for level in stats.non_combat_levels)
        if stats.all_non_combat:
            non_cmb_sk_names = "ALL"
        else:
            non_cmb_sk_names = "/".join(skills_initials[sk.name].capitalize() for sk in stats.non_combat_skills)
        non_cmb_avg_str = f"* **Non-Cmb. Avg. ({non_cmb_sk_names})**: {non_cmb_sk_lvls_str} -> {stats.non_combat_average:.2f}"
        
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
