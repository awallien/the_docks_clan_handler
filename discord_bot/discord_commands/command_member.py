import discord

from datetime import datetime
from discord_bot.discord_bot_util import (
    DiscordBotCommandMemberOptions as dbcmo, 
    EmbedUtil,
    RankUtil
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import TheDocksDiscordBot


async def _new_member(bot: "TheDocksDiscordBot",
                      interaction: discord.Interaction,
                      member: str,
                      **kwargs):
    await bot.mod.send(f"New member add: {member}, called by {interaction.message.author}")

async def _delete_member(bot: "TheDocksDiscordBot",
                         interaction: discord.Interaction,
                         member: str,
                         **kwargs):
    await bot.mod.send(f"Member delete: {member}, called by {interaction.message.author}")

async def _update_member(bot: "TheDocksDiscordBot",
                         interaction: discord.Interaction,
                         member: str,
                         **kwargs):
    if (name_change := kwargs.get("name_change")):
        await bot.mod.send(f"Update member {member} to name change {name_change}, called by {interaction.message.author}")

async def _clan_stats_member(bot: "TheDocksDiscordBot",
                             interaction: discord.Interaction,
                             member: str,
                             **kwargs):
    # Defer in case hiscore is needed
    await interaction.response.defer(ephemeral=True)

    clan_stats = None
    
    if not clan_stats:
        await interaction.edit_original_response(embed=EmbedUtil.error_embed(msg=f"Member '{member}' not found in the clan system."))
        return
    
    embed = discord.Embed(
        title = member,
        color=discord.Color.blue()
    )

    rank = clan_stats.rank
    joined_date = datetime.fromordinal(clan_stats.joined_date).strftime("%m-%d-%Y")
    total_xp = clan_stats.total_xp
    last_rank_date = datetime.fromordinal(clan_stats.last_rank_date).strftime("%m-%d-%Y")

    footer_note = ""
    if total_xp < 0:
        total_xp = "**-1 xp"
        footer_note = "**Total XP is not available in OSRS Hiscores since last rank date, or clan member has just joined the clan"

    embed.set_thumbnail(url=RankUtil.get_rank_icon_url(rank))
    (
        embed.add_field(name="Rank", value=rank, inline=True)
        .add_field(name="Joined Date", value=joined_date, inline=True)
        .add_field(name="Total XP", value=f"{total_xp} xp", inline=True)
        .add_field(name="Last Rank Date", value=last_rank_date, inline=True)
    )

    if kwargs["verbose"]:
        detail_stats = RankUtil.get_skill_stats(member, rank, clan_stats.joined_date)
        embed.add_field(name="\"Hidden\" Stats", value=detail_stats, inline=False)

    if footer_note:
        embed.set_footer(text=footer_note)

    await interaction.edit_original_response(embed=embed)

clan_member_options = {
    dbcmo.NEW : _new_member,
    dbcmo.UPDATE : _update_member,
    dbcmo.DELETE : _delete_member,
    dbcmo.CLAN_STATS : _clan_stats_member
}
async def discord_bot_command_member(bot: "TheDocksDiscordBot",
                                     interaction: discord.Interaction,
                                     option: int,
                                     member: str,
                                     **kwargs):
    if option not in clan_member_options:
        await bot.mod.send(f"Error: Unsupported option in discort bot command member: {option}")
    await clan_member_options[option](bot=bot, interaction=interaction, member=member, **kwargs)

async def discord_bot_command_challenge(bot: "TheDocksDiscordBot",
                                        interaction: discord.Interaction):
    caller = interaction.message.author
    await interaction.response.send_message(content="Request sent to Goose. Please allow 1-2 days for Goose to get back to you with a spicy challenge.")
    bot.mod.send(f"{caller} requests a challenge :)")