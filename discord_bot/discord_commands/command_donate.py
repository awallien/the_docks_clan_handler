import discord

from discord_bot_util import EmbedUtil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.bot import TheDocksDiscordBot


def try_float(value):
    try:
        return float(value)
    except Exception as e:
        return 0

async def discord_bot_command_donate(bot: "TheDocksDiscordBot",
                                     interaction: discord.Interaction,
                                     value: float):
    if (val := try_float(value)) <= 0 or val > 1000000:
        await interaction.response.send_message(
            embed=EmbedUtil.error_embed("The value you entered is invalid. Please enter a monetary value from 1..1000000"),
            ephemeral=True,
        )
        return
    
    await interaction.response.send_message(
        embed=EmbedUtil.info_embed(
            title="Thank you for your donation!",
            msg=f"We received your donation of {val}gp. Your contribution is greatly appreciated!"
        )
    )