import os
import logging
from logging.handlers import RotatingFileHandler

from pathlib import Path

from discord import Intents, utils as discord_utils, ClientException
from discord_bot import cb_docs
from discord.ext import commands

from .config import settings

class TheDocksDiscordBot(commands.Bot):

    def __init__(self):
        self._cmd_prefix = "/"
        self._intents = self._init_intents()

        self._init_logging()
        super().__init__(command_prefix=self._cmd_prefix, intents=self._intents)

    def _init_logging(self):
        logging.getLogger("discord").setLevel(logging.DEBUG)
        logging.getLogger('discord.http').setLevel(logging.INFO)
        handler = RotatingFileHandler(
            filename=os.path.join(Path(__file__).resolve().parent.parent, "logs", "discord.log"),
            encoding='utf-8',
            maxBytes=10 * 1024 * 1024,  # 10 MiB
            backupCount=5,
            mode='w'
        )
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(formatter)
        discord_utils.setup_logging(handler=handler, formatter=formatter, level=logging.DEBUG)        

    def _init_intents(self):
        intents = Intents.all()
        intents.message_content = True
        intents.members = True
        intents.messages = True
        intents.emojis_and_stickers = True
        intents.guild_scheduled_events = True
        return intents
    
    def _init_discord_vars(self):
        def _discord_get_or_fail(iterable, name):
            if not (res := discord_utils.get(iterable, name=name)):
                print(f"{name} returns None")
                raise ValueError(f"{name} returns None")
            return res

        self.guild = _discord_get_or_fail(self.guilds, settings.DISCORD_GUILD)
        
        self.mod = _discord_get_or_fail(self.guild.members, settings.BOT_OWNER)
        self.allowed_roles = _discord_get_or_fail(self.guild.roles, settings.ALLOWED_ROLES)
        
        self.drops_webhook = settings.DROPS_WEBHOOK
        self.drops_channel = _discord_get_or_fail(self.guild.channels, settings.DROPS_CHANNEL)
        self.clog_thread = _discord_get_or_fail(self.guild.threads, settings.CLOG_THREAD)
        self.clue_thread = _discord_get_or_fail(self.guild.threads, settings.CLUE_THREAD)

        self.general_channel = _discord_get_or_fail(self.guild.channels, settings.GENERAL_CHANNEL)
        self.forum_channel = _discord_get_or_fail(self.guild.channels, settings.FORUM_CHANNEL)
        self.voice_channel = _discord_get_or_fail(self.guild.voice_channels, settings.VOICE_CHANNEL)
        self.dev_channel = _discord_get_or_fail(self.guild.channels, settings.DEV_CHANNEL)

        print(f"guild({self.guild}), mod({self.mod}))")

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")
        self._init_discord_vars()
        if self.guild and self.mod:
            print(f"'{self.user}' is connected to Guild(id:{self.guild.id})")
        else:
            self.close()
            if not self.guild:
                raise ClientException(f"{self.user} is not connected to designated guild!")
            else:
                raise ClientException(f"Bot owner {self.mod} is not found!")

    async def on_command_error(self, ctx, exception):
        print(f"Exception({ctx.author.name},{type(exception)}:{exception})")
        if type(exception) == commands.CheckFailure:
            message = await ctx.reply(f"Sorry, you must be a {self.allowed_role} in order to use my commands. " 
                                      f"If you are a {self.allowed_role}, reach out to {self.mod.global_name} to provide you the role.")
            await message.add_reaction("🤣")

    async def run(self):
        await super().start(settings.DISCORD_TOKEN, reconnect=True)

"""Discord Bot Init"""
BOT = TheDocksDiscordBot()

"""All commands would be under the tag: docks"""
@BOT.hybrid_group(name="docks")
async def docks(ctx: commands.Context):
    await ctx.send("Honk")

@BOT.check
async def check_allowed_role(ctx: commands.Context):
    return BOT.allowed_roles in ctx.author.roles

@docks.command(name="sync")
async def sync(ctx: commands.Context):
    await BOT.tree.sync(guild=BOT.guild)
    await ctx.send(f"Commands are synced to {str(BOT.guild)}", ephemeral=True)

@docks.command(name="docs")
async def docs(ctx):
    await cb_docs(BOT, ctx)
