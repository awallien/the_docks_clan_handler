from pandas import isna
from clan_db.clan_database import ClanDatabase
from discord import Color, Embed, app_commands

from util import debug_print
from discord_bot.embed_util import err_embed, get_rank_icon_url, info_embed
from player_rank_script import PlayerRankHandler

OPTIONS = ["add", "delete", "detail"]

async def cb_player(BOT, ctx, player_name, option=None):   
    if option and option not in OPTIONS:
        return err_embed(f"Error: invalid input for option ({option})")

    is_detailed = False
    is_add = False
    is_deleted = False
    send_msg_to_mod = False

    if option == "add":
        is_add = True
    elif option == "delete":
        is_deleted = True
    elif option == "detail":
        is_detailed = True 

    debug_print(f"option: add({is_add}) delete({is_deleted}) detail({is_detailed}))")

    msg = ""
    player_info = BOT.db.get_player_data(player_name)
    if is_add:
        if not player_info:
            msg = f"Your request to add {player_name} has been submitted to Goose."
            embed = info_embed(msg)
            send_msg_to_mod = True
        else:
            embed = err_embed(f"{player_name} already exists in clan")
    elif player_info is None: 
        embed = err_embed(f"Player {player_name} is not found in clan database")
    elif is_deleted:
        msg = f"Your request to delete {player_name} has been submitted to Goose."
        embed = info_embed(msg)
        send_msg_to_mod = True
    else:
        embed = make_player_info_embed(player_name, player_info, is_detailed)
    
    if send_msg_to_mod:
        await BOT.mod.send(f"From {ctx.author}: {msg}")
    
    await ctx.send(embed=embed, ephemeral=True, reference=ctx.message)
    
async def opt_player_autocompletion(_, current):
    return [
        app_commands.Choice(name=option, value=option)
        for option in OPTIONS if current.lower() in option.lower()
    ]

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
