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

def _format_ordinal(value):
    if not value:
        return "Unknown"
    try:
        return datetime.fromordinal(int(value)).strftime("%m-%d-%Y")
    except (TypeError, ValueError):
        return "Unknown"


async def _new_member(bot: "TheDocksDiscordBot",
                      interaction: discord.Interaction,
                      member: str,
                      **kwargs):
    await bot.mod.send(f"New member add: {member}, called by {interaction.user}")

async def _delete_member(bot: "TheDocksDiscordBot",
                         interaction: discord.Interaction,
                         member: str,
                         **kwargs):
    await bot.mod.send(f"Member delete: {member}, called by {interaction.user}")

async def _update_member(bot: "TheDocksDiscordBot",
                         interaction: discord.Interaction,
                         member: str,
                         **kwargs):
    if (name_change := kwargs.get("name_change")):
        await bot.mod.send(f"Update member {member} to name change {name_change}, called by {interaction.user}")

async def _clan_stats_member(bot: "TheDocksDiscordBot",
                             interaction: discord.Interaction,
                             member: str,
                             **kwargs):
    # Defer in case hiscore is needed
    await interaction.response.defer(ephemeral=True)

    try:
        clan_stats = bot.container.clan_service().get_member(member)
    except ValueError:
        await interaction.edit_original_response(embed=EmbedUtil.error_embed(msg=f"Member '{member}' not found in the clan system."))
        return
    
    embed = discord.Embed(
        title=member,
        color=discord.Color.blue(),
    )

    rank = clan_stats.get("rank") or "Unknown"
    joined_date = _format_ordinal(clan_stats.get("joined_date"))
    last_rank_date = _format_ordinal(clan_stats.get("last_rank_date"))

    embed.set_thumbnail(url=RankUtil.get_rank_icon_url(rank))
    (
        embed.add_field(name="Rank", value=rank, inline=True)
        .add_field(name="Joined Date", value=joined_date, inline=True)
        .add_field(name="Last Rank Date", value=last_rank_date, inline=True)
    )

    if kwargs.get("verbose"):
        detail_stats = RankUtil.get_skill_stats(member, rank, clan_stats.get("joined_date"))
        embed.add_field(name="\"Hidden\" Stats", value=detail_stats, inline=False)

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
    handler = clan_member_options.get(option)
    if handler is None:
        await bot.mod.send(f"Error: Unsupported option in discord bot command member: {option}")
        return
    await handler(bot=bot, interaction=interaction, member=member, **kwargs)

async def discord_bot_command_challenge(bot: "TheDocksDiscordBot",
                                        interaction: discord.Interaction):
    caller = interaction.user
    await interaction.response.send_message(content="Request sent to Goose. Please allow 1-2 days for Goose to get back to you with a spicy challenge.")
    await bot.mod.send(f"{caller} requests a challenge :)")
