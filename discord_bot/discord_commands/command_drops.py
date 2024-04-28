from util import debug_print
from datetime import datetime, timedelta, timezone
import re
from discord import Color, Embed, app_commands

VALID_DAYS = [30, 60, 90, 180]

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

async def cb_drops(BOT, ctx, days=30):
    if days not in VALID_DAYS:
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
                for embed in message.embeds:
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
    
    embed = make_drops_embed(BOT.drop_webhook, days, players_drops)
    await ctx.send(embed=embed, reference=ctx.message)

async def days_drops_autocompletion(_, current):
    valid_days_str_list = list(map(str, VALID_DAYS))
    return [
        app_commands.Choice(name=day, value=day)
        for day in valid_days_str_list if current.lower() in day.lower()
    ]

def mvd_percentage(player_drop):
    """MVD value / Total GP"""
    total_gp = player_drop.get("Total GP", 0)
    mvd_value = player_drop.get("MVD", dict()).get("value", 0)

    perc = 0
    if total_gp != 0:
        perc = mvd_value / total_gp
    
    return f"{perc * 100:.2f}%"

def make_drops_embed(drop_wh_name, days, players_drops):
    embed = Embed(
        title=f"{days}-Day \"{drop_wh_name}\" Drop Archive",
        color=Color.blue(),
        description=f"I gathered the drops of The Docks Clan for the past {days} days. Here is what I collected:",
    )

    embed.set_thumbnail(url="https://oldschool.runescape.wiki/images/Coins_10000.png?7fa38")
    embed.set_footer(text="¹MVD Percentage = (MVD/Accumulated GP)*100\n"
                            "If you don't see your drops in the table above, then your plugin is all screwed up, and I can't properly parse your drops. "
                            "Please fix your plugin setup ASAP, if you want, or contact a fellow clan member to help you out.")
    
    for player in players_drops:
        drop_info = players_drops[player]

        embed.add_field(name=player, 
                        value=f"> **Accumulated GP**:                {format(drop_info.get('Total GP', 0), ',')}\n"
                                f"> **Most Valuable Drop (MVD)**:    {drop_info.get('MVD', dict()).get('item', 'N/A')}\n"
                                f"> **MVD Value**:                   {format(drop_info.get('MVD', dict()).get('value', 0), ',')}\n"
                                f"> **MVD Percentage¹**:             {mvd_percentage(drop_info)}",
                        inline=False)

    return embed
