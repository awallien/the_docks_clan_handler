import os
import random as rand
from argparse import ArgumentParser
from dotenv import load_dotenv
from discord import ClientException, Intents, utils as dutils, app_commands
from discord.ext import commands
from clan_db import ClanDatabase
from discord_bot import *
from util import debug_print, debug_set_enable

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
    
    def __init_discord_vars(self):
        def __discord_get_or_fail(iterable, name):
            res = dutils.get(iterable, name=name)
            if not res:
                raise ValueError(f"{name} returns None")
            return res
        
        # Associate env vars to discord bot vars, when bot is "on ready"
        self.guild = __discord_get_or_fail(self.guilds, self.guild)
        self.drop_channel = __discord_get_or_fail(self.guild.channels, self.drop_channel)
        self.general_channel = __discord_get_or_fail(self.guild.channels, self.general_channel)
        self.mod = __discord_get_or_fail(self.guild.members, self.mod)

        debug_print(f"guild({self.guild}), drop_channel({self.drop_channel}), general_channel({self.general_channel}), mod({self.mod}))")

    async def on_ready(self):
        debug_print(f"{self.user} has connected to Discord!")
        
        self.__init_discord_vars()
        
        if self.guild and self.mod:
            debug_print(f"'{self.user}' is connected to Guild(id:{self.guild.id})")
        else:
            self.close()
            if not self.guild:
                raise ClientException(f"{self.user} is not connected to designated guild!")
            else:
                raise ClientException(f"Bot owner {self.mod} is not found!")

    def run(self, db, production=False):
        self.db = db
        self.mod = os.getenv("BOT_OWNER")

        if production:
            self.guild = os.getenv("DISCORD_GUILD")
            self.drop_channel = os.getenv("DROPS_CHANNEL")
            self.drop_webhook = os.getenv("DROPS_WEBHOOK")
            self.general_channel = os.getenv("GENERAL_CHANNEL")
        else:
            self.guild = os.getenv("DISCORD_DEV_GUILD")
            self.drop_channel = os.getenv("DEV_DROPS_CHANNEL")
            self.drop_webhook = os.getenv("DEV_DROPS_WEBHOOK")
            self.general_channel = os.getenv("DEV_GENERAL_CHANNEL")
        
        super().run(self.TOKEN)

"""Discord Bot Initialization"""
BOT = TheDocksDiscordBot()

"""All commands would be under the tag: docks"""
@BOT.hybrid_group()
async def docks(ctx):
    embed = info_embed(":v", "Honk")
    await ctx.send(embed=embed, ephemeral=True, reference=ctx.message)

"""Command List"""
@docks.command(name="sync")
async def sync(ctx):
    await BOT.tree.sync()
    await ctx.send(f"Commands are synced to {str(BOT.guild)}")

@docks.command(name="player")
@app_commands.autocomplete(option=opt_player_autocompletion)
async def player(ctx, player_name, option:str=None, name_change:str=None):
    await cb_player(BOT, ctx, player_name, option, name_change)

@docks.command(name="drops")
@app_commands.autocomplete(days=days_drops_autocompletion)
async def drops(ctx, days=30):
    await cb_drops(BOT, ctx, days)

@docks.command(name="spin")
@app_commands.autocomplete(randomize_weights=set_true_autocompletion,
                           shuffle_options=set_true_autocompletion,
                           options_detail=set_true_autocompletion)
async def spin(ctx,
               options:str,
               weights:str=None,
               randomize_weights:str=None,
               shuffle_options:str=None,
               options_detail:str=None):
    await spin_cb(BOT, ctx, options, weights, randomize_weights, shuffle_options, options_detail)

if __name__ == "__main__":
    parser = ArgumentParser(
        prog="bot.py",
        description="The Docks Clan Bot",
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
