import discord

from discord_bot.discord_bot_util import DiscordBotCommandMemberOptions as dbcmo, EmbedUtil

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import TheDocksDiscordBot


async def _new_member(member: str):
    pass

async def _delete_member(member: str):
    pass

async def _update_member(member: str, name_change=None):
    pass

async def _clan_stats_member(member: str):
    pass


async def discord_bot_command_member(bot: "TheDocksDiscordBot",
                                     interaction: discord.Interaction,
                                     option: int,
                                     member: str,
                                     **kwargs):
    match (option):
        case dbcmo.NEW:
            await _new_member(member)
        case dbcmo.DELETE:
            await _delete_member(member)
        case dbcmo.CLAN_STATS:
            await _clan_stats_member(member)
        case dbcmo.UPDATE:
            if not (name_change := kwargs.get("name_change", "")):
                await interaction.response.send_message(emebd=EmbedUtil.error_embed("No options found to update"))
                return
            await _update_member(member, name_change=name_change)
        case _:
            print("shouldn't reach here")


async def discord_bot_command_challenge(bot: "TheDocksDiscordBot",
                                        interaction: discord.Interaction):
    caller = interaction.message.author
    await interaction.response.send_message(content="Request sent to Goose. Please allow 1-2 days for Goose to get back to ya with a spicy challenge.")
    bot.mod.send(f"{caller} requests a challenge :)")