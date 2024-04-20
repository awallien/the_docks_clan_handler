from argparse import ArgumentParser
import os
import random as rand
from discord import ClientException, Intents, utils as dutils, app_commands
from discord.ext import commands
from clan_database import ClanDatabase
from dotenv import load_dotenv
from logger import debug_print, debug_set_enable
from the_docks_bot_embed import TheDocksBotEmbed

load_dotenv()

class TheDocksDiscordBot(commands.Bot):
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    def __init__(self):
        self.cmd_prefix = "/"
        intents = Intents.all()
        intents.message_content = True
        intents.members = True
        intents.emojis_and_stickers = True
        print(intents)

        super().__init__(self.cmd_prefix, intents=intents)

    async def on_ready(self):
        self.guild = dutils.get(self.guilds, name=self.guild_type)
        self.mod = dutils.get(self.guild.members, name=os.getenv("BOT_OWNER"))
        debug_print(f"{self.user} has connected to Discord!")
        if self.guild and self.mod:
            debug_print(f"'{self.user}' is connected to Guild(id:{self.guild.id})")
        else:
            self.close()
            if not self.guild:
                raise ClientException(f"{self.user} is not connected to designated guild!")
            else:
                raise ClientException(f"Bot owner {self.mod} is not found!")

    def run(self, db, production=False):
        self.mod = None
        self.db = db

        if production:
            self.guild_type = os.getenv("DISCORD_GUILD")
            self.drop_channel = os.getenv("DROPS_CHANNEL")
            self.general_channel = os.getenv("GENERAL_CHANNEL")
        else:
            self.guild_type = os.getenv("DISCORD_DEV_GUILD")
            self.drop_channel = os.getenv("DEV_DROPS_CHANNEL")
            self.general_channel = os.getenv("DEV_GENERAL_CHANNEL")

        super().run(self.TOKEN)

"""Discord Bot Initialization"""
BOT = TheDocksDiscordBot()

"""Discord Bot Commands"""

"""All commands would be under the tag: docks"""
@BOT.hybrid_group()
async def docks(ctx):
    embed = TheDocksBotEmbed.info_embed(["Honk", ":v"][rand.randint(0,1)])
    await ctx.send(embed=embed, ephemeral=True, reference=ctx.message)


@docks.command()
async def player(ctx, player_name, option=None):   

    is_detailed = False
    is_add = False
    is_deleted = False
    send_msg_to_mod = False

    if option == "add":
        is_add = True
    elif option == "delete":
        is_deleted = True
    elif option == "detail":
        is_detailed = True 

    msg = ""
    player_info = BOT.db.get_player_data(player_name)
    if is_add:
        if not player_info:
            msg = f"Your request to add {player_name} has been submitted to Goose."
            embed = TheDocksBotEmbed.info_embed(msg)
            send_msg_to_mod = True
        else:
            embed = TheDocksBotEmbed.err_embed(f"{player_name} already exists in clan")
    elif player_info is None: 
        embed = TheDocksBotEmbed.err_embed(f"Player {player_name} is not found in clan database")
    elif is_deleted:
        msg = f"Your request to delete {player_name} has been submitted to Goose."
        embed = TheDocksBotEmbed.info_embed(msg)
        send_msg_to_mod = True
    else:
        embed = TheDocksBotEmbed.make_player_info_embed(player_name, player_info, is_detailed)
    
    if send_msg_to_mod:
        await BOT.mod.send(f"From {ctx.author}: {msg}")
    
    await ctx.send(embed=embed, ephemeral=True, reference=ctx.message)
    

@player.autocomplete("option")
async def opt_player_autocompletion(_, current):
    options = ["add", "delete", "detail"]
    return [
        app_commands.Choice(name=option, value=option)
        for option in options if current.lower() in option.lower()
    ]

@docks.command(name="sync")
async def sync(_):
    await BOT.tree.sync()
    await BOT.mod.send("synced commands to " + str(BOT.guild))

if __name__ == "__main__":
    parser = ArgumentParser(
        prog="player_rank_script.py",
        description="The Docks Ranking Script",
        allow_abbrev=False
    )

    parser.add_argument('-d', action="store_true", default=False, 
                        help="enable debug info")
    
    parser.add_argument('-p', '--production', action='store_true', default=False, help='Enable bot for production server')

    args = parser.parse_args()

    debug_set_enable(args.d)
    debug_print("Debug print is ON")

    db = ClanDatabase(mode_chr="r")
    BOT.run(db, args.production)
