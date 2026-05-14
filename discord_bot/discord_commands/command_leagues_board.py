import discord

from discord_bot import EmbedUtil

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import TheDocksDiscordBot


async def discord_bot_leagues_board(BOT: "TheDocksDiscordBot", interaction: discord.Interaction):
    await interaction.response.send_message(
        embed=EmbedUtil.info_embed("Leagues board is not implemented yet."),
        ephemeral=True,
    )
