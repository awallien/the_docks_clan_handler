from discord import Embed, Color
from pandas import isna
from clan_database import ClanDatabase
from player_rank_script import PlayerRankHandler

ICON_URI_PATH = "https://oldschool.runescape.wiki/images/Clan_icon_-_"
rank_to_icon = {
    '1':"Gnome_Child.png?b0561",    '2':"Kitten.png?9dc78",
    '3':"Adventurer.png?3630c",     '4':"Crew.png?6c963",
    '5':"Adventurer.png?3630c",     '6':"Fire.png?f7cb3",
    '7':"Inquisitor.png?0f3a8",     '8':"Barbarian.png?f92d8",
    '9':"Diamond.png?f7cb3",        '10':"Crusader.png?87d1d",
    '11':"Beast.png?53696",         '12':"Epic.png?f3acc",
    '13':"Raider.png?fff9d",        '14':"Gamer.png?3630c",
    'A':"Administrator.png?9dc78", 
    'D':"Deputy_owner.png?b0561",
    'O':"Owner.png?53696"
}

def get_rank_icon_url(rank):
    if rank not in rank_to_icon:
        raise Exception(f"Rank not found: {rank}")
    return ICON_URI_PATH + rank_to_icon[rank]

class TheDocksBotEmbed:
    
    def err_embed(msg):
        return Embed(
            title=msg,
            color=Color.dark_red()
        )
    
    def info_embed(msg):
        return Embed(
            title=msg,
            color=Color.blue()
        )
    
    def make_player_info_embed(p_name, p_info, is_detailed):
        embed = Embed(
            title=p_name,
            color=Color.blue()
        )

        rank = p_info[ClanDatabase.RANK]
        date_joined = p_info[ClanDatabase.JOINED]
        parent = p_info[ClanDatabase.PARENT]

        if isna(parent):
            parent = "N/A"

        embed.set_thumbnail(url=get_rank_icon_url(rank))

        embed.add_field(name="Rank", value=rank, inline=True) \
             .add_field(name="Date Joined", value=date_joined, inline=True) \
             .add_field(name="Parent", value=parent, inline=True)
        
        if is_detailed:
            last_rank_date = p_info[ClanDatabase.LAST_RANKED_DATE]
            total_xp = p_info[ClanDatabase.TOTAL_XP]
            act_cnt = p_info[ClanDatabase.ACTIVE_CNT]
            footer_note = ""

            if total_xp < 0:
                total_xp = "**-1xp"
                footer_note = "**Total XP is not available in OSRS Hiscores since last clan rank update"
            else:
                total_xp = int(total_xp)

            if isna(last_rank_date):
                last_rank_date = "N/A"

            embed.add_field(name="Total XP", value=total_xp, inline=True) \
                 .add_field(name="Last Rank Date", value=last_rank_date, inline=True) \
                 .add_field(name="Active Count", value=act_cnt, inline=True)
            
            if footer_note:
                embed.set_footer(text=footer_note)
            
            rank = p_info[ClanDatabase.RANK]
            if rank.isnumeric():
                rank = int(rank)

            if rank in PlayerRankHandler.MOD_RANKS or rank > PlayerRankHandler.ACTIVENESS_RANK_4:
                p_data = PlayerRankHandler.player_hiscore_get(p_name)
                if p_data:
                    p_lvls_info = PlayerRankHandler(p_data).get_max_levels_info()

                    embed.add_field(name="Combat Skills", 
                                    value="\n".join([f"**{skill.capitalize()}**: {lvl}" for skill,lvl in p_lvls_info["cmb"].values()]),
                                    inline=True)

                    embed.add_field(name="Top 3 Highest Other Skills",
                                    value="\n".join([f"**{skill.capitalize()}**: {lvl}" for skill,lvl in p_lvls_info["other"].items()]),
                                    inline=True)

        return embed
