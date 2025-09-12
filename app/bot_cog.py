import discord

from discord import app_commands, Interaction
from discord.ext import commands

from discord_bot import *
from .config import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .bot import TheDocksDiscordBot

class DocksGroupCog(commands.GroupCog, name="docks"):
    def __init__(self, bot: TheDocksDiscordBot) -> None:
        self.bot = bot
        super().__init__()


    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingRole):
            role = error.missing_role
            await interaction.response.send_message(
                embed = DiscordBotUtils.error_embed(
                    f"You don't have the required role: **{role}** to use this command!",
                    "Well... this is awkward."
                ), 
                ephemeral = True
            )
        else:
            await self.bot.mod.send(
                content=f"Error occurred, {interaction.user} executed {interaction.command} with error: {error}"
            )


    @app_commands.command(name="docs", description="Shows guides, references, and useful docs for the server and clan.")
    @app_commands.checks.has_role(settings.ALLOWED_ROLE)
    async def _docs(self, interaction: Interaction):
        await discord_bot_command_docs(self.bot, interaction)


    @app_commands.command(name="drops", description="Fetch a summary of players' drops from the drops channel.")
    @app_commands.checks.has_role(settings.ALLOWED_ROLE)
    @app_commands.describe(
        historical_days="How many days back to collect drop data (default: 30).",
        member="Optional: Only show drops for a specific player."
    )
    @app_commands.choices(
        historical_days=[
            app_commands.Choice(name=f"{days}", value=days)
            for days in [7, 14, 30, 60, 90, 180]
        ]
    )
    async def _drops(self, 
                     interaction: Interaction, 
                     historical_days: app_commands.Choice[int]=30, 
                     member: str=None):
        await discord_bot_command_drops(self.bot, interaction, historical_days, member)


    @app_commands.command(name="spin", description="Let me decide what to pick!")
    @app_commands.checks.has_role(settings.ALLOWED_ROLE)
    async def _spin(self, interaction: Interaction):
        pass