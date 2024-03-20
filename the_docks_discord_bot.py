from argparse import ArgumentParser
import os
import shlex
from discord import ClientException, Intents, Embed, Color
from discord import utils as dutils
from discord.ext import commands
from pandas import isna
from player_rank_script import ClanDatabase
from dotenv import load_dotenv
from logger import debug_print, debug_set_enable

load_dotenv()

ICON_URI_PATH = "https://oldschool.runescape.wiki/images/Clan_icon_-_"
rank_to_icon = {
    '1':"Gnome_Child.png?b0561",   '2':"Kitten.png?9dc78",
    '3':"Adventurer.png?3630c",   '4':"Crew.png?6c963",
    '5':"Adventurer.png?3630c",   '6':"Fire.png?f7cb3",
    '7':"Inquisitor.png?0f3a8",   '8':"Barbarian.png?f92d8",
    '9':"Diamond.png?f7cb3",   '10':"Crusader.png?87d1d",
    '11':"Beast.png?53696",  '12':"Epic.png?f3acc",
    '13':"Raider.png?fff9d",  '14':"Gamer.png?3630c",
    'A':"Administrator.png?9dc78", 
    'D':"Deputy_owner.png?b0561",
    'O':"Owner.png?53696"
}

def get_rank_icon_url(rank):
    if rank not in rank_to_icon:
        raise Exception(f"Rank not found: {rank}")
    return ICON_URI_PATH + rank_to_icon[rank]

class TheDocksDiscordBotCog(commands.Cog):

    def __init__(self, bot, db):
        self.db: ClanDatabase = db
        self.bot = bot
        super().__init__()

    def err_embed(self, msg):
        return Embed(
            title=msg,
            color=Color.dark_red()
        )

    def make_player_info_embed(self, p_name, p_info, is_detailed):
        embed = Embed(
            title=p_name,
            color=Color.blue()
        )

        rank = p_info[ClanDatabase.RANK]
        date_joined = p_info[ClanDatabase.JOINED]
        parent = p_info[ClanDatabase.PARENT]

        if isna(parent):
            parent = "N/A"

        embed.set_thumbnail(url=get_rank_icon_url(rank))

        embed.add_field(name="Rank", value=rank, inline=True) \
             .add_field(name="Date Joined", value=date_joined, inline=True) \
             .add_field(name="Parent", value=parent, inline=True)
        
        if is_detailed:
            last_rank_date = p_info[ClanDatabase.LAST_RANKED_DATE]
            total_xp = p_info[ClanDatabase.TOTAL_XP]
            act_cnt = p_info[ClanDatabase.ACTIVE_CNT]
            footer_note = ""

            if total_xp < 0:
                total_xp = "**0xp"
                footer_note = "**Total XP is not available in OSRS Hiscores since last clan rank update"
            else:
                total_xp = int(total_xp)

            if isna(last_rank_date):
                last_rank_date = "N/A"

            embed.add_field(name="Total XP", value=total_xp, inline=True) \
                 .add_field(name="Last Rank Date", value=last_rank_date, inline=True) \
                 .add_field(name="Active Count", value=act_cnt, inline=True)
            
            if footer_note:
                embed.set_footer(text=footer_note)

        return embed

    @commands.command(name="player", help="Retrieve member's info in clan. If player's name has space(s), wrap player name in quote (ex: \"Noob 1234\")")
    async def dump_player_cb(self, ctx, *, args=None):
        if not args or not str(ctx.message.author) == "celerus":
            return
        fields = shlex.split(args)
        player_name = fields[0]
        is_detailed = False
        if len(fields) > 1 and fields[1] == "detail":
            is_detailed = True
        
        player_info = self.db.get_player_data(player_name)
        if player_info is None:
            err_embed = self.err_embed(f"Player {player_name} is not found in clan database")
            await ctx.send(embed=err_embed, ephemeral=True)
        else:
            info_embed = self.make_player_info_embed(player_name, player_info, is_detailed)
            await ctx.send(embed=info_embed, ephemeral=True)

class TheDocksDiscordBot(commands.Bot):
    TOKEN = os.getenv("DISCORD_TOKEN")
    PROD_GUILD = os.getenv("DISCORD_GUILD")
    DEV_GUILD = os.getenv("DISCORD_DEV_GUILD")
    
    def __init__(self, db, guild_type=DEV_GUILD):
        self.cmd_prefix = "/docks "
        self.guild_type = guild_type
        self.db__ = db

        intents = Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(self.cmd_prefix, intents=intents)

    async def on_ready(self):
        guild = dutils.get(self.guilds, name=self.guild_type)
        debug_print(f"{self.user} has connected to Discord!")
        if guild:
            debug_print(f"'{self.user}' is connected to Guild(id:{guild.id})")
        else:
            self.close()
            raise ClientException(f"{self.user} is not connected to designated guild!")
        
        await self.add_cog(TheDocksDiscordBotCog(self, self.db__))

    def run(self):
        super().run(self.TOKEN)

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

    guild = TheDocksDiscordBot.PROD_GUILD if args.production else TheDocksDiscordBot.DEV_GUILD
    db = ClanDatabase(mode_chr="r")

    bot = TheDocksDiscordBot(db, guild)
    bot.run()