import json
import os
from dataclasses import dataclass
from typing import List

from discord import Embed, Color
from entity import ClanMemberRank
from service import rank_service
from util import Skill, Hiscore
from resources import RANK_ICONS_JSON_PATH

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
            raise NotImplementedError(f"Rank {rank} icon does not exist")
        return cls._rank_to_icon[rank]
    
    @classmethod
    def get_skill_stats(cls, member: str, rank: ClanMemberRank, joined_date: int) -> RankSkillStats | None:
        try:
            hiscore = Hiscore(member)
            skills = hiscore.skills
        except Exception as e:
            return None

        max_melee = rank_service.get_max_skills(
            skills.attack, skills.strength, skills.defence
        )
        ranged_lvl = skills.ranged.level
        magic_lvl = skills.magic.level
        cmb_avg = (max_melee.level + ranged_lvl + magic_lvl) / 3

        n_highest = 3
        if rank == ClanMemberRank.RANK_14:
            n_highest = 6

        max_non_cmb_skills = rank_service.get_non_cmb_skills(hiscore, n_highest=n_highest)
        non_cmb_avg = sum([sk.level for sk in max_non_cmb_skills]) / n_highest
        next_rank = rank_service.get_next_rank(hiscore, rank, joined_date)

        return RankSkillStats(
            max_melee=max_melee,
            ranged_lvl=ranged_lvl,
            magic_lvl=magic_lvl,
            cmb_avg=cmb_avg,
            max_non_cmb_skills=max_non_cmb_skills,
            non_cmb_avg=non_cmb_avg,
            next_rank=next_rank
        )


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
