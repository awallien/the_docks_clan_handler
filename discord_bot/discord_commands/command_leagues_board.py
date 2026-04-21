import discord
import asyncio

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import TheDocksDiscordBot


async def discord_bot_leagues_board(BOT: "TheDocksDiscordBot", interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    members = BOT.container.clan_service().list_members()
    members = ["FakeDrXenome", "CV6 66", "F arting", "VeloPWR"]
    ...
