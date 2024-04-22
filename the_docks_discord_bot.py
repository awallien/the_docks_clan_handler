import os
import random as rand
from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
import re
from dotenv import load_dotenv
from discord import ClientException, Embed, Intents, utils as dutils, app_commands
from discord.ext import commands
from clan_database import ClanDatabase
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

"""Discord Bot Commands"""

"""All commands would be under the tag: docks"""
@BOT.hybrid_group()
async def docks(ctx):
    embed = TheDocksBotEmbed.info_embed(["Honk", ":v"][rand.randint(0,1)])
    await ctx.send(embed=embed, ephemeral=True, reference=ctx.message)


@docks.command(name="player")
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


valid_days = [30, 60, 90, 180]
@docks.command(name="drops")
async def drops(ctx, days=30):
    def get_drop_embed_info(embed: Embed):
        info = type("info", (), {"player":"N/A", "item":"N/A", "value":0})()
        info.player = embed.author.name
        
        # get GE value
        ge_value_field = next((field for field in embed.fields if field.name == "GE Value"), None)
        if ge_value_field:
            value = ge_value_field.value
            match = re.search(r'[\d,]+', value)
            if match:
                info.value = int(match.group(0).replace(",", ""))
        else:
            return None
        
        # get item name
        matches = re.findall(r'\[([^\]]+)\]', embed.description)
        if matches:
            info.item = matches[0]
        
        return info

    if days not in valid_days:
        await ctx.send(f"Error: invalid input for days ({days})")
        return

    dtime_days = (datetime.now() - timedelta(days=days)).replace(tzinfo=timezone.utc)
    players_drops = dict() # {K:name, V:{"Total GE Value":<int> "MVI":{"item":<string>, "value":<int>}}
    message_cnt = 1

    async for message in BOT.drop_channel.history(after=dtime_days, oldest_first=True):
        if message.author.name == BOT.drop_webhook:
            if message.embeds:
                debug_print(f"message {message_cnt}")
                message_cnt += 1
                for embed in message.embeds: # There should only be one embed, but looping over all embeds just in case
                    info = get_drop_embed_info(embed)
                    if info is None:
                        break
                    debug_print(f"{info.player}, {info.item}, {info.value}")
                    player_drops_info = players_drops.get(info.player, None)
                    if player_drops_info is None:
                        players_drops[info.player] = {"Total GP": 0, "MVD":{"item": "", "value":0}}
                        player_drops_info = players_drops[info.player]

                    player_drops_info["Total GP"] += info.value
                    player_drops_info_mvi = player_drops_info["MVD"]
                    if info.value > player_drops_info_mvi["value"]:
                        player_drops_info_mvi["value"] = info.value
                        player_drops_info_mvi["item"] = info.item
    
    embed = TheDocksBotEmbed.make_drops_embed(BOT.drop_webhook, days, players_drops)
    await ctx.send(embed=embed, reference=ctx.message)


@drops.autocomplete("days")
async def days_drops_autocompletion(_, current):
    valid_days_str_list = list(map(str, valid_days))
    return [
        app_commands.Choice(name=day, value=day)
        for day in valid_days_str_list if current.lower() in day.lower()
    ]

@docks.command(name="sync")
async def sync(_):
    await BOT.tree.sync()
    await BOT.mod.send(f"synced commands to {str(BOT.guild)}")

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
