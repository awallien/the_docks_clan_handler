import json

from discord import Embed, Color
from entity import ClanMemberRank
from resources import RANK_ICONS_JSON_PATH

class RankUtil:
    _rank_to_icon = dict()

    @classmethod
    def _load_data(cls):
        if cls._rank_to_icon:
            return
        
        with open(RANK_ICONS_JSON_PATH, "r", encoding="utf-8") as jsonfp:
            data = json.load(jsonfp)
        
        uri_path = data["uri_path"]
        cls._rank_to_icon = {
            entry["rank"]: uri_path + entry["icon_path"]
            for entry in data["ranks"]
        }

    @classmethod
    def get_rank_icon_url(cls, rank: ClanMemberRank):
        if not cls._rank_to_icon:
            cls._load_data()
        
        if rank not in cls._rank_to_icon:
            raise NotImplementedError(f"Rank {rank} icon does not exist")
        return cls._rank_to_icon[rank]

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
