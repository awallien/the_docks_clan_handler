import discord

from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime, timedelta, timezone

from discord_bot import DiscordBotUtils as dbu

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import TheDocksDiscordBot

MAX_EMBED_FIELDS = 25

def supported_spaces(bot: TheDocksDiscordBot) -> Dict[str, discord.abc.Messageable]:
    return {
        "drop": bot.drops_channel,
        "clog": bot.clog_thread
    }

@dataclass
class ItemStats:
    value: int
    count: int

@dataclass
class PlayerDrops:
    total_gp: int
    items: Dict[str, ItemStats] = field(default_factory=dict)
    mvd_item: Optional[str] = None
    num_clogs: int

def _mvd_percentage(total_gp, mvd_value):
    """MVD value / Total GP"""
    perc = 0
    if total_gp != 0:
        perc = mvd_value / total_gp
    return f"{perc * 100:.2f}%"

def _make_embeds(bot: TheDocksDiscordBot, 
                 historical_days: int, 
                 players_drops: Dict[str, PlayerDrops]) -> discord.Embed:
    drops_for = ""
    if len(players_drops) == 1:
        drops_for = f"**{list(players_drops.keys)[0]}**"
    
    embed = (
        discord.Embed(
            title = f"{historical_days}-Day \"{bot.drops_webhook}\" Drops Archive",
            color = discord.Color.blue(),
            description = f"Gathered {drops_for or 'the clan'}’s drops from the last {historical_days} days — straight from the drops channel and clogs thread. Feast your eyes:")
            .set_thumbnail(url="https://oldschool.runescape.wiki/images/Coins_10000.png?7fa38")
            .set_footer(text="MVD Percentage = (MVD Value/Accumulated GP)*100")
    )

    embeds = []
    if len(players_drops) == 0:
        embed.add_field(name="", value="**No drops found 😢**")
        embeds.append(embed)
    else:
        for idx, (player, drops) in enumerate(players_drops.items(), start=1):
            total_gp = 0
            mvd = drops.mvd_item
            mvd_value = 0
            mvd_count = 0
            num_clogs = 0
            embed.add_field(
                name=player,
                value=f"> **Accumulated GP**: {format(total_gp, ",")}\n"
                      f"> **Most Valuable Drop (MVD)**: {mvd_count}x {mvd}\n"
                      f"> **MVD Value**: {format(mvd_value, ",")}\n"
                      f"> **MVD Percentage¹**: {_mvd_percentage(total_gp, mvd_value)}\n"
                      f"> **Number of CLogs**: {num_clogs}\n",
                inline = False
            )

            if idx % MAX_EMBED_FIELDS == 0:
                embeds.append(embed)
                embed = discord.Embed()
        
        if len(embed.fields) > 0:
            embeds.append(embed)
    
    return embeds

def _parse_embed(embed: discord.Embed, 
                 space: discord.abc.Messageable, 
                 players_drops: Dict[str, PlayerDrops], 
                 member: str):
    if space == "drop":
        pass
    elif space == "clog":
        pass
    else:
        raise NotImplementedError(f"{space} is not supported.")
    


async def discord_bot_command_drops(bot: TheDocksDiscordBot, 
                                    interaction: discord.Interaction, 
                                    historical_days: int=30, 
                                    member: str=None):
    if not member and not interaction.user == bot.mod:
        await interaction.response.send_message(
            embed=dbu.error_embed(f"Sorry, only Goose is allowed not to specify a player.", title="Please specify a member.")
        )
        return
    
    await interaction.response.defer(ephemeral=True)
    await interaction.edit_original_response(content=f"*One sec, I'm chugging very hard...*")

    delta = (datetime.now() - timedelta(days=historical_days)).replace(tzinfo=timezone.utc)
    players_drops: Dict[str, PlayerDrops] = dict()

    for space, space_obj in supported_spaces(bot).items():
        async for message in space_obj.history(after=delta, oldest_first=False, limit=None):
            if not message.author.name == bot.drops_webhook:
                continue

            for embed in message.embeds:
                _parse_embed(embed, space, players_drops, member)

    drops_embeds = _make_embeds(bot, historical_days, players_drops)
    await interaction.response.send_message(embed=drops_embeds)
