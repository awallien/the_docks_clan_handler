from discord import Embed, Color
from entity import ClanMemberRank

rank_to_icon = {
    '1':"Gnome_Child.png?b0561",    '2':"Kitten.png?9dc78",
    '3':"Adventurer.png?3630c",     '4':"Crew.png?6c963",
    '5':"Achiever.png?45aef",       '6':"Fire.png?f7cb3",
    '7':"Inquisitor.png?0f3a8",     '8':"Barbarian.png?f92d8",
    '9':"Diamond.png?f7cb3",        '10':"Crusader.png?87d1d",
    '11':"Beast.png?53696",         '12':"Epic.png?f3acc",
    '13':"Raider.png?fff9d",        '14':"Gamer.png?3630c",
    'A':"Administrator.png?9dc78", 
    'D':"Deputy_owner.png?b0561",
    'O':"Owner.png?53696"
}

class RankUtil:

    ICON_URI_PATH = "https://oldschool.runescape.wiki/images/Clan_icon_-_"

    rank_to_icon = {

    }

    @classmethod
    def get_rank_icon_url(cls, rank: ClanMemberRank):
        if rank not in rank_to_icon:
            raise NotImplementedError(f"Rank {rank} icon does not exist")
        return cls.ICON_URI_PATH + rank_to_icon[rank]

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