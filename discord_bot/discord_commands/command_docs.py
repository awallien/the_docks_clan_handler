import discord
from discord_bot.discord_bot_util import DiscordBotUtils


async def discord_bot_command_docs(BOT, interaction: discord.Interaction):
    embed = discord.Embed(
        title="Docs Hub",
        description="Dock here for guides, plugins, and support — everything you need in one place.",
        color=discord.Color.blue(),
    )

    embed.add_field(
        name="📊 **The Docks Ranking System & Permissions**",
        value="If you are a member of the clan, [learn more](https://discord.com/channels/773805654728900611/1215130179299442739) about the roles, ranks, and permissions work inside The Docks.",
        inline=False
    )
    embed.add_field(
        name="🔔 **Setting up Dink Plugin**",
        value="[Read the setup guide](https://discord.com/channels/773805654728900611/1358405081640341627) to set up drops, deaths, and other notifications.",
        inline=False
    )
    embed.add_field(
        name="🛠️ **The Docks Clan Bot Help Desk**",
        value="[Visit the help desk](https://discord.com/channels/773805654728900611/1254717570288717835) for FAQs and support for the Docks Clan Bot",
        inline=False
    )

    embed.set_footer(text="The Docks Clan Bot • Welcome aboard!")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
