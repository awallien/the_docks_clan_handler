import discord

"""
⁠✅grand-exchange💭 (here) - main chat hub
⁠💰drops💰 - cool drops by the clan and other members with Dink plugin (see below), including threads
⁠⚙ Cloggers Cloggin' Clogs ⚙  - clog items
⁠🧩 Yooooo Clue Drop! 📜  - clue caskets opened
⁠💀haha-you-dead-noob💀  - funny deaths from Dink plugin (see below)
⁠🗡☠💥p-v-p💥☠🛡 - pvp deaths and glory from Dink plugin (see below)
⁠📜osrs-clan-forum📜 - organized chat and forum like discussions including
⁠How to Set up Dink Plugin for D… - set up Dink plugin
⁠unknown - doc on clan ranking
⁠📣announcement📣 - Goose has an annoucement
⁠🎥spotlight🔴 - if you are a streamer
⁠💎say-hi👋 - new discord members (OSRS players are yellow-coded)
⁠🦺earth - touching grass?
 Certified Jambo Enjoyers  - the scaper's main vc
"""

async def discord_bot_command_docs(BOT, interaction: discord.Interaction):
    embed = discord.Embed(
        title="The \"Docs\" Hub",
        description="**Docksy** here for guides, plugins, and support — everything you need in one place.",
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
