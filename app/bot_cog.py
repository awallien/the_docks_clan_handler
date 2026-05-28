import discord

from discord import app_commands, Interaction
from discord.ext import commands

from discord_bot import (
    DiscordBotCommandMemberOptions,
    EmbedUtil,
    discord_bot_command_challenge,
    discord_bot_command_docs,
    discord_bot_command_drops,
    discord_bot_command_member,
    discord_bot_command_spin,
    discord_bot_command_donate
)
from .config import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .bot import TheDocksDiscordBot

class DocksGroupCog(commands.GroupCog, name="docks"):
    def __init__(self, bot: "TheDocksDiscordBot") -> None:
        self.bot = bot
        super().__init__()


    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingRole):
            role = error.missing_role
            await interaction.response.send_message(
                embed = EmbedUtil.error_embed(
                    f"You don't have the required role: **{role}** to use this command!",
                    "Well... this is awkward."
                ), 
                ephemeral = True
            )
        elif isinstance(error, app_commands.errors.NoPrivateMessage):
            await interaction.response.send_message(
                embed = EmbedUtil.error_embed(
                    "Oops! My commands don’t work in DMs — try again in one of the designated servers!",
                    "Trying to slide into my DMs?"
                )
            )
        else:
            await self.bot.mod.send(
                content=f"Error occurred:\nuser: {interaction.user}\ncommand: {interaction.command.name}\ntype: {type(error)}\nerror: {error}"
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
        if hasattr(historical_days, "value"):
            historical_days = historical_days.value
        await discord_bot_command_drops(self.bot, interaction, historical_days, member)


    @app_commands.command(name="spin", description="Let me decide what to pick!")
    @app_commands.checks.has_role(settings.ALLOWED_ROLE)
    @app_commands.describe(
        options="2 or more options to put on the spinner, separated by semi-colons (Ex: opt1;opt2;opt3)",
        weights="Weights associated to each option (i.e. weight 5000 is 1/5000 chance of choosing this option), in range 1 to 1000000",
        randomize_weights="Randomize weights, can be set with or without weights inputted"
    )
    async def _spin(self, 
                    interaction: Interaction,
                    options: str,
                    weights: str="",
                    randomize_weights: bool=False):
        await discord_bot_command_spin(interaction, options, weights, randomize_weights)

    
    @app_commands.command(name="new_member", description="Let me know if a new member joined the clan!")
    @app_commands.checks.has_role(settings.ALLOWED_ROLE)
    @app_commands.describe(
        member="RSN of new member"
    )
    async def new_member(self, 
                        interaction: Interaction,
                        member: str):
        await discord_bot_command_member(self.bot, interaction, DiscordBotCommandMemberOptions.NEW, member)

    @app_commands.command(name="update_member", description="You updated something about youself in the game, and it needs my attention.")
    @app_commands.checks.has_role(settings.ALLOWED_ROLE)
    @app_commands.describe(
        member="RSN of new member",
        name_change="I changed my RSN to..."
    )
    async def update_member(self,
                            interaction: Interaction,
                            member: str,
                            name_change: str = ""):
        await discord_bot_command_member(self.bot, interaction, DiscordBotCommandMemberOptions.UPDATE, member, name_change=name_change)

    @app_commands.command(name="delete_member", description="I am sad to see you go! :(")
    @app_commands.checks.has_role(settings.ALLOWED_ROLE)
    @app_commands.describe(
        member="RSN of member that left the clan"
    )
    async def delete_member(self,
                            interaction: Interaction,
                            member: str):
        await discord_bot_command_member(self.bot, interaction, DiscordBotCommandMemberOptions.DELETE, member)

    
    @app_commands.command(name="clan_stats", description="See your clan stats. I'll look away...")
    @app_commands.checks.has_role(settings.ALLOWED_ROLE)
    @app_commands.describe(
        member="RSN of clan member",
        verbose="Show Hiscore details behind this rank"
    )
    async def clan_stats(self,
                        interaction: Interaction,
                        member: str,
                        verbose: bool = False):
        await discord_bot_command_member(self.bot, interaction, DiscordBotCommandMemberOptions.CLAN_STATS, member, verbose=verbose)

    @app_commands.command(name="challenge", description="I see you are bored. Want a challenge?")
    @app_commands.checks.has_role(settings.ALLOWED_ROLE)
    async def _challenge(self, interaction: Interaction):
        await discord_bot_command_challenge(self.bot, interaction)

    # wiki for gear
    # get news of the week
    # donate
    @app_commands.command(name="donate", description="Donate for a good cause :)")
    @app_commands.checks.has_role(settings.ALLOWED_ROLE)
    async def _donate(self, interaction: Interaction, value: float):
        await discord_bot_command_donate(self.bot, interaction, value)