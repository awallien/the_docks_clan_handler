import logging
from logging.handlers import RotatingFileHandler
import discord
from discord import Intents, utils as discord_utils, ClientException
from pathlib import Path

from discord_bot import EmbedUtil as dbu
from discord.ext import commands

from .config import settings
from .bot_cog import DocksGroupCog

from container import Container

class TheDocksDiscordBot(commands.Bot):

    def __init__(self):
        self._init_logging()
        self.container: Container = None
        super().__init__(command_prefix="!", intents=self._init_intents())

    def _init_logging(self):
        logging.getLogger("discord").setLevel(logging.DEBUG)
        logging.getLogger('discord.http').setLevel(logging.INFO)
        logs_dir = Path(__file__).resolve().parent.parent / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            filename=logs_dir / "discord.log",
            encoding='utf-8',
            maxBytes=10 * 1024 * 1024,  # 10 MiB
            backupCount=5,
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
                if settings.dev_env():
                    return
                raise ValueError(f"{name} returns None")
            return res

        self.guild: discord.Guild = _discord_get_or_fail(self.guilds, settings.DISCORD_GUILD)
        
        self.mod: discord.Member = _discord_get_or_fail(self.guild.members, settings.BOT_OWNER)
        self.allowed_role: discord.Role = _discord_get_or_fail(self.guild.roles, settings.ALLOWED_ROLE)
        
        self.drops_webhook: str = settings.DROPS_WEBHOOK
        self.drops_channel: discord.TextChannel = _discord_get_or_fail(self.guild.channels, settings.DROPS_CHANNEL)
        self.clog_thread: discord.Thread = _discord_get_or_fail(self.guild.threads, settings.CLOG_THREAD)
        self.clue_thread: discord.Thread = _discord_get_or_fail(self.guild.threads, settings.CLUE_THREAD)

        self.general_channel: discord.TextChannel = _discord_get_or_fail(self.guild.channels, settings.GENERAL_CHANNEL)
        self.forum_channel: discord.ForumChannel = _discord_get_or_fail(self.guild.channels, settings.FORUM_CHANNEL)
        self.voice_channel: discord.VoiceChannel = _discord_get_or_fail(self.guild.voice_channels, settings.VOICE_CHANNEL)
        self.dev_channel: discord.TextChannel = _discord_get_or_fail(self.guild.channels, settings.DEV_CHANNEL)
        self.welcome_channel: discord.TextChannel = _discord_get_or_fail(self.guild.channels, settings.WELCOME_CHANNEL)

        print(f"guild({self.guild}), mod({self.mod}))")


    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")
        self._init_discord_vars()
        if self.guild and self.mod:
            try:
                synced = await self.tree.sync()
                print(f"Synced {len(synced)} commands")
            except Exception as e:
                print(e)
            print(f"'{self.user}' is connected to Guild(id:{self.guild.id})")
        else:
            await self.close()
            if not self.guild:
                raise ClientException(f"{self.user} is not connected to designated guild!")
            else:
                raise ClientException(f"Bot owner {self.mod} is not found!")
            
    async def on_member_join(self, member):
        if self.allowed_role in member.roles:
            await self.welcome_channel.send(
                embed=dbu.info_embed(
                    msg=(
                        f"Hey {member.mention}, welcome to the server! I'm **Docksy**, here to help you get settled. "
                        "Take a look around, and say hi to everyone! "
                        "When you're ready, type `/docks docs` to check out some helpful info to get started."
                    ),
                    title="Welcome to the server! 👋"
                )
            )

    async def on_command_error(self, ctx, exception):
        print(f"Exception({ctx.author.name},{type(exception)}:{exception})")
        if isinstance(exception, commands.MissingAnyRole):
            message = await ctx.reply(embed=dbu.info_embed(f"Sorry, you must be a {self.allowed_role} in order to use my commands. " 
                                      f"If you are a member, please reach out to {self.mod.display_name} to provide you the role.",
                                      title="Well... this is awkward."))
            await message.add_reaction("🤣")

    async def setup_hook(self):
        await self.add_cog(DocksGroupCog(self))
        
    async def run(self, container: Container):
        self.container = container
        await super().start(settings.DISCORD_TOKEN, reconnect=True)

"""Discord Bot Init"""
BOT = TheDocksDiscordBot()
