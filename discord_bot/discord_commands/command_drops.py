import re
import discord

from dataclasses import dataclass, field
from datetime import timedelta, timezone

from discord_bot import EmbedUtil

from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from app.bot import TheDocksDiscordBot

MAX_EMBED_FIELDS = 25
GP_VALUE_RE = re.compile(r"([\d,.]+[kKmMbB]?)\s*gp")
ITEMS_DESC_RE = re.compile(r"\d+\s*x\s*\[(.*?)\]\(.*?\)\s*\(([\d,.]+[kKmMbB]?)\)")
GP_MULTIPLIER = {
    "K": 1_000,
    "M": 1_000_000,
    "B": 1_000_000_000
}

def supported_spaces(bot: "TheDocksDiscordBot") -> Dict[str, discord.abc.Messageable]:
    return {
        "drop": bot.drops_channel,
        "clog": bot.clog_thread
    }

@dataclass
class ItemStats:
    value: int = 0
    count: int = 0

@dataclass
class PlayerDrops:
    total_gp: int = 0
    mvd: str = ""
    num_clogs: int = 0
    items: Dict[str, ItemStats] = field(default_factory=dict)

def _mvd_percentage(total_gp, mvd_value):
    """MVD value / Total GP"""
    perc = 0
    if total_gp != 0:
        perc = mvd_value / total_gp
    return f"{perc * 100:.2f}%"

def _make_embeds(bot: "TheDocksDiscordBot", 
                 historical_days: int, 
                 players_drops: Dict[str, PlayerDrops]) -> discord.Embed:
    drops_for = ""
    if len(players_drops) == 1:
        drops_for = f"**{list(players_drops.keys())[0]}**"
    
    embed = (
        discord.Embed(
            title = f"{historical_days}-Day \"{bot.drops_webhook}\" Drops Archive",
            color = discord.Color.blue(),
            description = f"Gathered {drops_for or 'the clan'}’s drops from the last {historical_days} days — straight from the drops channel and clogs thread. Feast your eyes:")
            .set_thumbnail(url="https://oldschool.runescape.wiki/images/Coins_10000.png?7fa38")
            .set_footer(text="¹MVD Percentage = (MVD Value/Accumulated GP)*100")
    )

    embeds = []
    if len(players_drops) == 0:
        embed.add_field(name="", value="**No drops found 😢**")
        embed.set_footer(text="")
        embeds.append(embed)
    else:
        for idx, (player, drops) in enumerate(players_drops.items(), start=1):
            total_gp = int(drops.total_gp)
            mvd = drops.mvd
            mvd_stat = drops.items.get(mvd, ItemStats())
            num_clogs = drops.num_clogs
            mvd_label = f"{mvd_stat.count}x {mvd}" if mvd else "None"

            embed.add_field(
                name=player,
                value=f"> **Accumulated GP**: {format(total_gp, ',')}gp\n"
                      f"> **Most Valuable Drop (MVD)**: {mvd_label}\n"
                      f"> **MVD Value**: {format(int(mvd_stat.value), ',')}gp\n"
                      f"> **MVD Percentage¹**: {_mvd_percentage(total_gp, mvd_stat.value)}\n"
                      f"> **Number of CLogs**: {num_clogs}\n",
                inline = False
            )

            if idx % MAX_EMBED_FIELDS == 0:
                embeds.append(embed)
                embed = discord.Embed().set_footer(text="¹MVD Percentage = (MVD Value/Accumulated GP)*100")
        
        if len(embed.fields) > 0:
            embeds.append(embed)
    
    return embeds

def _parse_gp_value(line: str):
    value = line.replace(",", "").strip()
    suffix = value[-1:].upper()
    multipler = GP_MULTIPLIER.get(suffix, 1)
    if suffix in GP_MULTIPLIER:
        value = value[:-1]
    return float(value) * multipler

def _parse_drop_embed(embed: discord.Embed):    
    gp_value = 0
    items_stats: Dict[str, ItemStats] = dict()

    # description contains the big value item
    for item, value in ITEMS_DESC_RE.findall(embed.description or ""):
        items_stats[item] = items_stats.get(item, ItemStats())
        items_stats[item].count += 1
        items_stats[item].value += _parse_gp_value(value)

    # fields contain the gp value
    for embed_field in embed.fields:
        if embed_field.name == "Total Value":
            gp_value_search = GP_VALUE_RE.search(embed_field.value)
            if gp_value_search:
                gp_value_str = gp_value_search.group(1).replace(",", "")
                gp_value += _parse_gp_value(gp_value_str)
    
    return gp_value, items_stats

def _parse_embed(embed: discord.Embed, 
                 space: discord.abc.Messageable, 
                 player_drops: PlayerDrops):
    gp_value: int = 0
    items: Dict[str, ItemStats] = dict()

    if space == "drop":
        gp_value, items = _parse_drop_embed(embed)
        player_drops.total_gp += gp_value
        for drop, stats in items.items():
            player_item = player_drops.items.setdefault(drop, ItemStats())
            player_item.count += stats.count
            player_item.value += stats.value
            if stats.value > player_drops.items.get(player_drops.mvd, ItemStats()).value:
                player_drops.mvd = drop
        return
    elif space == "clog":
        """There is nothing to parse from the clog embed at the moment. Instead, increment the player's num clogs"""
        player_drops.num_clogs += 1
        return
    else:
        raise NotImplementedError(f"{space} is not supported.")

async def discord_bot_command_drops(bot: "TheDocksDiscordBot", 
                                    interaction: discord.Interaction, 
                                    historical_days: int=30, 
                                    member: str=None):
    if not member and not interaction.user == bot.mod:
        await interaction.response.send_message(
            embed=EmbedUtil.error_embed("Please specify a member."),
            ephemeral=True
        )
        return
    
    await interaction.response.defer(ephemeral=False)
    await interaction.edit_original_response(content="*One sec, I'm chugging very hard...*")

    delta = (discord.utils.utcnow() - timedelta(days=historical_days)).replace(tzinfo=timezone.utc)
    players_drops: Dict[str, PlayerDrops] = dict()

    for space, space_obj in supported_spaces(bot).items():
        async for message in space_obj.history(after=delta, oldest_first=False, limit=None):
            if not message.author.name == bot.drops_webhook:
                continue

            for embed in message.embeds:
                """
                Filters:
                    - member is populated
                    - check only on rich embeds from Dink
                """
                embed_author = embed.author.name
                if member and not embed_author == member:
                    continue
                if not (embed.footer and "Powered by Donks" in embed.footer.text):
                    continue
                players_drops[embed_author] = players_drops.get(embed_author, PlayerDrops())
                _parse_embed(embed, space, players_drops[embed_author])

    drops_embeds = _make_embeds(bot, historical_days, players_drops)
    await interaction.edit_original_response(embeds=drops_embeds)
